#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deploy_netlify.py - Webinar-OS: put the rendered pages live on Netlify with ONE API call.
Zips the landing/ folder in memory and POSTs it. No CLI, no Node. Standard library only.

Needs NETLIFY_AUTH_TOKEN in .env (Personal access token: app.netlify.com/user/applications).

Usage:
    python3 deploy_netlify.py --config outputs/webinars/<slug>/config.json
        first run: creates a site named <slug>-<random> (renamed to <slug> if free), deploys, writes
        config.netlify_site_id + config.page_url. next runs: redeploys to the same site.
    python3 deploy_netlify.py --config ... --dir other/folder
    python3 deploy_netlify.py --check           only verifies the token
"""
import argparse
import io
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_project_root, read_env, http, load_json, save_json  # noqa: E402

API = "https://api.netlify.com/api/v1"


def zip_dir(folder):
    buf = io.BytesIO()
    folder = Path(folder)
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(folder.rglob("*")):
            if f.is_file() and not f.name.startswith("."):
                z.write(f, f.relative_to(folder).as_posix())
    return buf.getvalue()


def wait_ready(token, deploy_id, timeout=180):
    t0 = time.time()
    while time.time() - t0 < timeout:
        s, d = http("GET", "%s/deploys/%s" % (API, deploy_id), token, timeout=30)
        if s == 200 and isinstance(d, dict):
            if d.get("state") == "ready":
                return d
            if d.get("state") == "error":
                sys.exit("x Netlify deploy failed: %s" % d.get("error_message"))
        time.sleep(3)
    sys.exit("x Netlify deploy did not become ready in %ds" % timeout)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config")
    ap.add_argument("--dir", help="folder to deploy (default: <config dir>/landing)")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    token = read_env(find_project_root()).get("NETLIFY_AUTH_TOKEN")
    if not token:
        sys.exit("x NETLIFY_AUTH_TOKEN missing. app.netlify.com/user/applications -> New access token, then: "
                 "python3 env_set.py NETLIFY_AUTH_TOKEN <token>")
    s, me = http("GET", API + "/user", token, timeout=30)
    if s != 200:
        sys.exit("x Netlify token rejected (status %s): %s" % (s, str(me)[:200]))
    print("ok Netlify token valid (%s)" % (me.get("email") if isinstance(me, dict) else ""))
    if args.check:
        return
    if not args.config:
        ap.error("--config required")

    cfg_path = Path(args.config).resolve()
    cfg = load_json(cfg_path)
    slug = str(cfg.get("slug") or "").strip()
    folder = Path(args.dir).resolve() if args.dir else cfg_path.parent / "landing"
    if not (folder / "index.html").exists():
        sys.exit("x %s/index.html not found. run render_pages.py first" % folder)
    blob = zip_dir(folder)
    print("-> zipped %s (%d KB)" % (folder, len(blob) // 1024))

    site_id = str(cfg.get("netlify_site_id") or "").strip()
    hdr = {"Content-Type": "application/zip"}
    if site_id:
        s, d = http("POST", "%s/sites/%s/deploys" % (API, site_id), token, blob, hdr, timeout=300)
        if s not in (200, 201):
            sys.exit("x deploy failed (status %s): %s" % (s, str(d)[:300]))
        deploy = wait_ready(token, d["id"])
        s, site = http("GET", "%s/sites/%s" % (API, site_id), token, timeout=30)
    else:
        s, site = http("POST", API + "/sites", token, blob, hdr, timeout=300)
        if s not in (200, 201) or not isinstance(site, dict) or "id" not in site:
            sys.exit("x site creation failed (status %s): %s" % (s, str(site)[:300]))
        site_id = site["id"]
        # try to claim a readable name; fall back silently if taken
        for name in (slug, slug + "-webinar", slug + "-live"):
            s2, r = http("PATCH", "%s/sites/%s" % (API, site_id), token, {"name": name}, timeout=30)
            if s2 == 200:
                site = r
                break
        deploy_id = (site.get("deploy_id") or (site.get("published_deploy") or {}).get("id"))
        if deploy_id:
            wait_ready(token, deploy_id)
        else:
            time.sleep(5)

    url = (site.get("ssl_url") or site.get("url") or "").rstrip("/") + "/"
    cfg["netlify_site_id"] = site_id
    cfg["page_url"] = url
    save_json(cfg_path, cfg)
    print("ok live: %s   (thank-you: %sthank-you/)" % (url, url))
    print("ok config updated: netlify_site_id, page_url")


if __name__ == "__main__":
    main()
