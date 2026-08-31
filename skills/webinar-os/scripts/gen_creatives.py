#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_creatives.py - Webinar-OS: generates the creative background images for one webinar
with the OpenAI images API (model gpt-image-2). Standard library only (Python 3.9+),
works on Windows / Mac / Linux.

Usage (Windows: python instead of python3):
    python3 gen_creatives.py --config outputs/webinars/<slug>/config.json --dry-run
    python3 gen_creatives.py --config outputs/webinars/<slug>/config.json --key sk-...
    python3 gen_creatives.py --config ... --only story-a,post-b
    python3 gen_creatives.py --config ... --key sk-... --variations 3

Inputs (next to config.json):
    config.json      slug, project_name, business_name ...
    creatives.json   [{"id","direction","prompt","size","use","punch","subline"}, ...]
                     size: "1:1" (1024x1024) or "9:16" (1024x1536)
                     use:  "hero" (default, the image is the ad) or "card" (dimmed background
                           of templates/creative.html) - see reference/creatives.md section 4.1

Output:
    outputs/webinars/<slug>/creatives/bg-<id>.png     background image, no text on it
    (with --variations N: bg-<id>-1.png .. bg-<id>-N.png; you open them and keep the best)
    a table of what was created

The key: read from --key, from the OPENAI_API_KEY environment variable, or from .env.
It is never written to a file and never printed. No key = the texts stay ready and only the
images are skipped (exit 0).
"""
import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_project_root, read_env, load_json  # noqa: E402

API_URL = "https://api.openai.com/v1/images/generations"
MODEL = "gpt-image-2"
SIZES = {"1:1": "1024x1024", "9:16": "1024x1536", "1024x1024": "1024x1024", "1024x1536": "1024x1536"}

# never in an image we ship (reference/creatives.md, section 4.2)
BANNED = (" No text, no letters, no words, no numbers, no logos, no signage, no watermark. "
          "Not the AI cliche, none of these anywhere in the frame: no brains, no neural networks, "
          "no circuit boards, no glowing purple or electric blue gradients, no holograms, "
          "no humanoid robots, no generic futuristic tech wallpaper, no stock-photo handshakes, "
          "no floating UI panels or HUD overlays, no neon light trails, no connected-dots globe, "
          "no people in suits pointing at transparent screens. ")

CRAFT = ("Real light, real texture, one clear subject, a restrained palette of two colours plus one "
         "accent, honest contrast, no plastic digital glow, no over-smoothing, correct anatomy. ")

# the reserved quiet area depends on what the image is for (reference/creatives.md, section 4.1)
ROOM = {
    # the image itself is the ad: the headline sits over the top of it
    "hero": ("Composition: generous quiet negative space across the upper half of the frame, "
             "free of detail, for a headline to be added later."),
    # the image becomes the dimmed background of templates/creative.html: it fades out downward
    "card": ("Composition: the visual interest lives in the upper two thirds of the frame and the "
             "bottom third is almost empty. Bright, high contrast, graphic, so it survives being "
             "dimmed to a faint texture behind text."),
}

def get_key(cli_key):
    if cli_key:
        return cli_key.strip()
    env = read_env(find_project_root())
    return (env.get("OPENAI_API_KEY") or "").strip() or None


def build_prompt(item):
    prompt = str(item.get("prompt") or "").strip()
    if not prompt:
        prompt = str(item.get("direction") or "abstract editorial background")
    use = str(item.get("use") or "hero").strip().lower()
    room = ROOM.get(use, ROOM["hero"])
    return prompt + BANNED + CRAFT + room


def generate(key, prompt, size, timeout=180):
    payload = json.dumps({"model": MODEL, "prompt": prompt, "size": size, "n": 1}).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=payload,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    item = (data.get("data") or [{}])[0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    url = item.get("url")
    if not url:
        raise RuntimeError("no image in the response")
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()


def explain_error(err):
    """Plain Hebrew for the three failures that actually happen."""
    if isinstance(err, urllib.error.HTTPError):
        code = err.code
        if code == 401:
            return "המפתח לא תקין או פג תוקף. אפשר להנפיק חדש ב-platform.openai.com בעמוד API keys."
        if code == 429:
            return "חריגה מהקצב או מהמכסה בחשבון. כדאי לחכות דקה, או לבדוק יתרה ב-platform.openai.com בעמוד Billing."
        if code == 400:
            return "הבקשה נדחתה (ניסוח או גודל לא נתמך). כדאי לנסח את התיאור מחדש בלי שמות מותג ובלי אנשים אמיתיים."
        return "השרת החזיר שגיאה %d. אפשר לנסות שוב בעוד דקה." % code
    if isinstance(err, urllib.error.URLError):
        return "אין חיבור לרשת כרגע. כדאי לבדוק את האינטרנט ולהריץ שוב את אותה פקודה."
    return "תקלה: %s" % err


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, help="path to config.json of the webinar")
    ap.add_argument("--key", help="OpenAI key (a password: never saved, never printed)")
    ap.add_argument("--only", help="comma separated ids to generate")
    ap.add_argument("--variations", type=int, default=1,
                    help="how many options to generate per item (2-3 recommended: you pick the best)")
    ap.add_argument("--dry-run", action="store_true", help="print what would be sent, no key needed")
    args = ap.parse_args()

    config_path = Path(args.config).resolve()
    config = load_json(config_path)
    out_dir = config_path.parent
    slug = config.get("slug") or out_dir.name

    spec_path = out_dir / "creatives.json"
    if not spec_path.exists():
        sys.exit("x חסר הקובץ creatives.json בתיקייה %s. השלב כותב אותו לפני ההרצה." % out_dir)
    items = load_json(spec_path)
    if isinstance(items, dict):
        items = items.get("creatives") or []
    if not items:
        sys.exit("x הרשימה ב-creatives.json ריקה, אין מה לייצר.")

    wanted = [s.strip() for s in (args.only or "").split(",") if s.strip()]
    if wanted:
        items = [it for it in items if str(it.get("id")) in wanted]
        if not items:
            sys.exit("x לא נמצא אף מזהה מתוך --only ברשימה.")

    cdir = out_dir / "creatives"
    cdir.mkdir(parents=True, exist_ok=True)

    cmd_hint = ('python3 %s --config %s --key <המפתח>'
                % (Path(__file__).name, config_path))

    key = None if args.dry_run else get_key(args.key)
    if not args.dry_run and not key:
        print("הטקסטים מוכנים במלואם ב-ads.md; רק התמונות דולגו, כי אין מפתח.")
        print("אפשר להנפיק מפתח ב-platform.openai.com בעמוד API keys, ואז להריץ:")
        print("  " + cmd_hint)
        return 0

    n_var = max(1, int(args.variations or 1))
    print("וובינר: %s · %d קריאייטיבים · %d גרסאות לכל אחד · תיקייה: %s"
          % (slug, len(items), n_var, cdir))
    rows, failed = [], 0
    for i, item in enumerate(items, 1):
        cid = str(item.get("id") or "creative-%d" % i)
        size = SIZES.get(str(item.get("size") or "1:1"), "1024x1024")
        prompt = build_prompt(item)
        if args.dry_run:
            rows.append((cid, size, item.get("direction") or "", "יבש (dry-run)"))
            print("\n[%s] %s · %s · %s" % (cid, item.get("direction") or "", size,
                                           str(item.get("use") or "hero")))
            print(prompt)
            continue
        for v in range(1, n_var + 1):
            name = "bg-%s.png" % cid if n_var == 1 else "bg-%s-%d.png" % (cid, v)
            target = cdir / name
            label = cid if n_var == 1 else "%s (%d)" % (cid, v)
            try:
                blob = generate(key, prompt, size)
                target.write_bytes(blob)
                rows.append((label, size, item.get("direction") or "", target.name))
            except Exception as e:  # noqa: BLE001
                failed += 1
                rows.append((label, size, item.get("direction") or "", "נכשל"))
                print("  ! %s: %s" % (label, explain_error(e)))

    print("\n%-16s %-12s %-28s %s" % ("מזהה", "גודל", "כיוון", "קובץ"))
    for r in rows:
        print("%-16s %-12s %-28s %s" % r)
    print("\nסיכום: %d מתוך %d." % (len(rows) - failed, len(rows)))
    if not args.dry_run:
        if n_var > 1:
            print("יש כמה גרסאות לכל מזהה. פותחים את כולן, בוחרים אחת לפי רף האיכות")
            print("(reference/creatives.md, סעיף 7), ורק אז ממשיכים.")
        print("השלב הבא: הטקסט העברי מולבש מעל התמונה עם templates/creative.html (render_pages.py --creatives),")
        print("ולא נכתב בתוך התמונה עצמה.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
