#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deploy_netlify.py - Webinar-OS step 9: puts the rendered landing folder live on Netlify.
Zips landing/ in memory and POSTs it. No CLI, no Node, standard library only (urllib).
Works on Windows / Mac / Linux, Python 3.9+.

The token is read from --token, from NETLIFY_AUTH_TOKEN (env or .env), or asked for at the
prompt. Given on the command line it is saved once to the project .env (via env_set.py), so the
next runs need no token. It is never printed back.

Netlify Forms: a brand new site is created with form detection OFF
(processing_settings.ignore_html_forms = true). With detection off the form on the page returns
404 on submit and every registration is lost in silence, so right after creating the site this
script turns detection on and deploys again. Nothing to click in the dashboard.

Usage (Windows: python instead of python3):
    python3 deploy_netlify.py --config outputs/webinars/<slug>/config.json --token <token>
        first run:  creates the site, turns form detection on, deploys, writes
                    config.netlify_site_id + config.page_url, re-renders the pages so the live
                    address sits inside them, deploys once more.
        next runs:  redeploys the same folder to the same site (the address does not change).
    python3 deploy_netlify.py --config ... --token <token> --site-name my-webinar
    python3 deploy_netlify.py --config ... --dry-run     shows what would be sent, no token needed
    python3 deploy_netlify.py --token <token> --check    only checks that the token works
    python3 deploy_netlify.py --config ... --submissions          the registrations, as a table
    python3 deploy_netlify.py --config ... --submissions --spam   the ones Netlify quarantined
"""
import argparse
import io
import os
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_project_root, read_env, http, load_json, save_json  # noqa: E402

API = "https://api.netlify.com/api/v1"
HERE = Path(__file__).resolve().parent


def die(*lines):
    for line in lines:
        print(line, file=sys.stderr)
    sys.exit(1)


def explain(status, body):
    """Netlify status code -> one plain Hebrew line the participant can act on."""
    if status == 0:
        return ("x אין תשובה מהרשת. בודקים חיבור לאינטרנט, מחכים דקה ומריצים שוב את אותה פקודה. "
                "מאחורי חומת אש בעבודה? מנסים מרשת אחרת, או מעלים ידנית (Netlify Drop).")
    if status in (401, 403):
        return ("x הטוקן נדחה. יוצרים טוקן חדש (app.netlify.com ← User settings ← Applications ← "
                "Personal access tokens ← New access token), מעתיקים אותו במלואו ומריצים שוב.")
    if status == 422:
        return ("x השם הזה כבר תפוס אצל מישהו אחר ב-Netlify. מריצים שוב עם "
                "--site-name ושם אחר (אותיות קטנות באנגלית, מספרים ומקפים).")
    if status == 404:
        return ("x האתר לא נמצא. אם מחקת אותו ב-Netlify: מוחקים את netlify_site_id מהקונפיג "
                "ומריצים שוב, וייווצר אתר חדש.")
    return "x השרת החזיר שגיאה %s: %s" % (status, str(body)[:200])


def get_token(args):
    token = str(args.token or "").strip()
    if not token:
        token = str(os.environ.get("NETLIFY_AUTH_TOKEN") or "").strip()
    if not token:
        token = str(read_env(find_project_root()).get("NETLIFY_AUTH_TOKEN") or "").strip()
    if not token:
        try:
            import getpass
            token = getpass.getpass("הדבק/י כאן את הטוקן של Netlify (לא יוצג על המסך): ").strip()
        except Exception:
            token = ""
    if not token:
        die("x חסר טוקן.",
            "  app.netlify.com ← User settings ← Applications ← Personal access tokens ← New access token,",
            "  ואז מריצים שוב עם --token <הטוקן>.")
    if str(args.token or "").strip():
        save_token(token)
    return token


def save_token(token):
    """Keep the token in the project .env, so the next runs need no --token.
    One dry line, no lecture."""
    r = subprocess.run([sys.executable, str(HERE / "env_set.py"), "NETLIFY_AUTH_TOKEN", token],
                       capture_output=True, text=True)
    print("ok נשמר ל-.env" if r.returncode == 0 else "   (הטוקן לא נשמר ל-.env, ההרצה ממשיכה)")


def zip_dir(folder):
    """Zips the folder in memory. Returns (bytes, sorted list of inner paths)."""
    buf = io.BytesIO()
    folder = Path(folder)
    names = []
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(folder.rglob("*")):
            if f.is_file() and not f.name.startswith("."):
                inner = f.relative_to(folder).as_posix()
                z.write(f, inner)
                names.append(inner)
    return buf.getvalue(), names


def wait_ready(token, deploy_id, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        s, d = http("GET", "%s/deploys/%s" % (API, deploy_id), token, timeout=30)
        if s == 200 and isinstance(d, dict):
            state = d.get("state")
            if state == "ready":
                return d
            if state == "error":
                die("x הפריסה נכשלה בצד של Netlify: %s" % d.get("error_message"))
        elif s not in (200, 0):
            die(explain(s, d))
        time.sleep(3)
    die("x הפריסה לא הסתיימה תוך %d שניות. נכנסים ל-app.netlify.com לראות את הסטטוס, ומריצים שוב." % timeout)


def deploy_zip(token, site_id, blob):
    s, d = http("POST", "%s/sites/%s/deploys" % (API, site_id), token, blob,
                {"Content-Type": "application/zip"}, timeout=600)
    if s not in (200, 201) or not isinstance(d, dict) or "id" not in d:
        die(explain(s, d))
    wait_ready(token, d["id"])


def enable_forms(token, site_id):
    """Form detection is OFF on a new site (processing_settings.ignore_html_forms = true).
    Left off, a submit on the page answers 404 and no lead is ever stored."""
    s, r = http("PATCH", "%s/sites/%s" % (API, site_id), token,
                {"processing_settings": {"html": {"pretty_urls": True}, "ignore_html_forms": False}},
                timeout=30)
    if s == 200:
        print("ok זיהוי טפסים הופעל באתר")
        return True
    print("   לא הצלחתי להפעיל זיהוי טפסים (%s). ב-Netlify: Site configuration ← Forms ← Enable form detection" % s)
    return False


def show_submissions(token, site_id, spam=False):
    """Step 9 and the follow-up: the registrations, straight from Netlify."""
    s, forms = http("GET", "%s/sites/%s/forms" % (API, site_id), token, timeout=30)
    if s != 200:
        die(explain(s, forms))
    names = [f.get("name") for f in forms] if isinstance(forms, list) else []
    if not names:
        print("   אין טופס מזוהה באתר הזה. אם הדף כבר באוויר עם טופס: מריצים שוב את ההעלאה,")
        print("   היא מדליקה זיהוי טפסים ומעלה שוב, ואחר כך שולחים הרשמת בדיקה אחת.")
        return
    print("-> טפסים באתר: %s" % ", ".join(str(n) for n in names))
    url = "%s/sites/%s/submissions?per_page=100" % (API, site_id)
    if spam:
        url += "&state=spam"
    s, subs = http("GET", url, token, timeout=60)
    if s != 200:
        die(explain(s, subs))
    if not isinstance(subs, list) or not subs:
        print("   %s" % ("אין הרשמות בהסגר" if spam else "אין הרשמות עדיין"))
        if not spam:
            print("   ליד שנעלם? לפעמים Netlify מסמן הרשמה תקינה כספאם, ואז היא לא ברשימה הזו:")
            print("   מריצים את אותה פקודה עם --spam")
        return
    print("-> %d הרשמות%s" % (len(subs), " בהסגר (ספאם)" if spam else ""))
    rows = [("מתי", "שם", "טלפון", "מייל")]
    for it in subs:
        d = it.get("data") or {}
        rows.append((str(it.get("created_at") or "")[:16].replace("T", " "),
                     str(d.get("name") or d.get("first_name") or ""),
                     str(d.get("phone") or ""),
                     str(d.get("email") or "")))
    w = [max(len(r[i]) for r in rows) for i in range(4)]
    for i, r in enumerate(rows):
        print("   " + "  ".join(r[j].ljust(w[j]) for j in range(4)))
        if i == 0:
            print("   " + "  ".join("-" * w[j] for j in range(4)))
    if not spam:
        print("   חסרה שורה שאת/ה בטוח/ה ששלחת? היא כנראה בהסגר: אותה פקודה עם --spam")


def site_url(site):
    return (site.get("ssl_url") or site.get("url") or "").rstrip("/") + "/"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", help="outputs/webinars/<slug>/config.json")
    ap.add_argument("--dir", help="folder to deploy (default: <config dir>/landing)")
    ap.add_argument("--token", help="Netlify personal access token (or NETLIFY_AUTH_TOKEN, or a prompt)")
    ap.add_argument("--site-name", help="the name in <name>.netlify.app (default: config.slug)")
    ap.add_argument("--check", action="store_true", help="only check that the token works")
    ap.add_argument("--dry-run", action="store_true", help="show what would be sent, without a token and without uploading")
    ap.add_argument("--submissions", action="store_true", help="list the registrations stored by Netlify Forms")
    ap.add_argument("--spam", action="store_true", help="with --submissions: the quarantined ones instead")
    args = ap.parse_args()

    # ---------------------------------------------------------------- dry run
    if args.dry_run:
        if not args.config and not args.dir:
            ap.error("--dry-run needs --config or --dir")
        folder = Path(args.dir).resolve() if args.dir else Path(args.config).resolve().parent / "landing"
        if not (folder / "index.html").exists():
            die("x לא נמצא index.html בתיקייה %s. מריצים קודם את render_pages.py." % folder)
        blob, names = zip_dir(folder)
        cfg = load_json(Path(args.config).resolve()) if args.config else {}
        site_id = str(cfg.get("netlify_site_id") or "").strip()
        name = str(args.site_name or cfg.get("slug") or "").strip()
        print("-> dry run, שום דבר לא נשלח ושום קובץ לא משתנה")
        print("   תיקייה: %s" % folder)
        if site_id:
            print("   יעד: POST %s/sites/%s/deploys" % (API, site_id))
        else:
            print("   יעד: POST %s/sites  (יצירת אתר חדש בשם '%s')" % (API, name or "<slug>"))
            print("        ואחריו PATCH %s/sites/<id>  עם השם ועם הפעלת זיהוי טפסים" % API)
        print("   גוף הבקשה: application/zip, %d bytes, %d קבצים" % (len(blob), len(names)))
        print("   כותרת: Authorization: Bearer <token> (הטוקן לא מודפס)")
        for n in names:
            print("     - %s" % n)
        print("   אחרי הפריסה ייכתבו לקונפיג: netlify_site_id, page_url")
        return

    # ---------------------------------------------------------------- token
    token = get_token(args)
    s, me = http("GET", API + "/user", token, timeout=30)
    if s != 200:
        die(explain(s, me))
    print("ok הטוקן תקין (%s)" % (me.get("email") if isinstance(me, dict) else ""))
    if args.check:
        return
    if not args.config:
        ap.error("--config required")

    # ---------------------------------------------------------------- the registrations
    if args.submissions:
        cfg = load_json(Path(args.config).resolve())
        sid = str(cfg.get("netlify_site_id") or "").strip()
        if not sid:
            die("x אין netlify_site_id בקונפיג. מעלים קודם את הדף לאוויר.")
        show_submissions(token, sid, args.spam)
        return

    # ---------------------------------------------------------------- inputs
    cfg_path = Path(args.config).resolve()
    cfg = load_json(cfg_path)
    slug = str(cfg.get("slug") or "").strip()
    folder = Path(args.dir).resolve() if args.dir else cfg_path.parent / "landing"
    if not (folder / "index.html").exists():
        die("x לא נמצא index.html בתיקייה %s. מריצים קודם את render_pages.py." % folder)
    blob, names = zip_dir(folder)
    print("-> נארזו %d קבצים (%d KB) מתוך %s" % (len(names), max(1, len(blob) // 1024), folder))

    site_id = str(cfg.get("netlify_site_id") or "").strip()
    wanted = str(args.site_name or slug or "").strip().lower()
    wanted = re.sub(r"[^a-z0-9-]+", "-", wanted).strip("-")

    # ---------------------------------------------------------------- deploy
    if site_id:
        deploy_zip(token, site_id, blob)
        s, site = http("GET", "%s/sites/%s" % (API, site_id), token, timeout=30)
        if s != 200 or not isinstance(site, dict):
            die(explain(s, site))
    else:
        s, site = http("POST", API + "/sites", token, blob, {"Content-Type": "application/zip"}, timeout=600)
        if s not in (200, 201) or not isinstance(site, dict) or "id" not in site:
            die(explain(s, site))
        site_id = site["id"]
        # detection is off on a new site; turning it on now, before anyone can register
        forms_on = enable_forms(token, site_id)
        if wanted:
            for name in (wanted, wanted + "-webinar", wanted + "-live"):
                s2, r = http("PATCH", "%s/sites/%s" % (API, site_id), token, {"name": name}, timeout=30)
                if s2 == 200 and isinstance(r, dict):
                    site = r
                    break
                if s2 == 422:
                    print("   השם '%s' תפוס, מנסה שם אחר" % name)
        deploy_id = site.get("deploy_id") or (site.get("published_deploy") or {}).get("id")
        if deploy_id:
            wait_ready(token, deploy_id)
        else:
            time.sleep(5)
        if forms_on:
            # the first deploy was zipped before detection was on, so the form is not registered yet
            deploy_zip(token, site_id, blob)

    url = site_url(site)

    # ------------------------------------- the live address goes into the pages
    changed = cfg.get("page_url") != url or cfg.get("netlify_site_id") != site_id
    cfg["netlify_site_id"] = site_id
    cfg["page_url"] = url
    save_json(cfg_path, cfg)
    if changed:
        before = (folder / "index.html").read_bytes()
        r = subprocess.run([sys.executable, str(HERE / "render_pages.py"),
                            "--config", str(cfg_path), "--only", "pages"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("   הרינדור החוזר נכשל, הדף באוויר עם התוכן הקודם: %s" % (r.stderr or "").strip()[:200])
        elif (folder / "index.html").read_bytes() != before:
            print("-> הכתובת החיה נכנסה לדפים, מעלה שוב")
            blob, _ = zip_dir(folder)
            deploy_zip(token, site_id, blob)

    print("ok הדף באוויר: %s" % url)
    print("ok דף התודה: %sthank-you/" % url)
    print("ok נשמרו בקונפיג: netlify_site_id, page_url")
    print("   הנרשמים: python3 %s --config %s --submissions" % (Path(__file__).name, cfg_path))
    print("   עדכון אחרי שינוי: מרנדרים שוב ומריצים בדיוק את אותה פקודה.")


if __name__ == "__main__":
    main()
