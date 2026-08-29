#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
screenshot.py - Webinar-OS (advanced path): render the creatives (and any HTML) to PNG with the
browser that is already installed (Chrome / Edge / Chromium, headless). No Playwright, no pip.

Usage (Windows: python instead of python3):
    python3 screenshot.py --dir outputs/webinars/<slug>/landing/creatives
    python3 screenshot.py --dir ... --no-story          (1:1 only)
    python3 screenshot.py --file page.html --size 1080x1080 --out page.png
    python3 screenshot.py --browser "/path/to/chrome" ...

Output: next to each HTML -> <id>.png (1080x1080) and <id>-story.png (1080x1920).
Exit 3 if no browser was found (the report says how to screenshot manually).
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from doctor import find_browser  # noqa: E402


def shoot(browser, html_path, out_png, w, h, query="", budget_ms=8000):
    url = Path(html_path).resolve().as_uri() + (("?" + query) if query else "")
    cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
           "--no-default-browser-check", "--force-device-scale-factor=1",
           "--window-size=%d,%d" % (w, h), "--virtual-time-budget=%d" % budget_ms,
           "--screenshot=%s" % str(Path(out_png).resolve()), url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return False, "timeout"
    ok = Path(out_png).exists() and Path(out_png).stat().st_size > 1000
    return ok, (r.stderr or "")[-300:] if not ok else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", help="folder with creative HTML files")
    ap.add_argument("--file", help="single HTML file")
    ap.add_argument("--out", help="output PNG (with --file)")
    ap.add_argument("--size", default="1080x1080", help="WxH for --file")
    ap.add_argument("--no-story", action="store_true")
    ap.add_argument("--browser", help="path to chrome/edge binary")
    args = ap.parse_args()

    browser = args.browser or find_browser()
    if not browser:
        print("x לא נמצא Chrome/Edge. צילום ידני: פותחים את קובץ ה-HTML בדפדפן, F12, Cmd/Ctrl+Shift+P, "
              "'Capture full size screenshot'. ל-9:16 מוסיפים ?story לכתובת.")
        sys.exit(3)

    jobs = []
    if args.file:
        w, h = [int(x) for x in args.size.lower().split("x")]
        jobs.append((Path(args.file), Path(args.out or Path(args.file).with_suffix(".png")), w, h, ""))
    elif args.dir:
        for f in sorted(Path(args.dir).glob("*.html")):
            jobs.append((f, f.with_suffix(".png"), 1080, 1080, ""))
            if not args.no_story:
                jobs.append((f, f.with_name(f.stem + "-story.png"), 1080, 1920, "story"))
    else:
        ap.error("--dir or --file required")

    t0 = time.time()
    failed = 0
    for src, dst, w, h, q in jobs:
        ok, err = shoot(browser, src, dst, w, h, q)
        print(("ok %s" if ok else "x  %s  %s") % (dst, err) if not ok else "ok %s (%dx%d)" % (dst, w, h))
        failed += 0 if ok else 1
    print("%d/%d done in %.0fs with %s" % (len(jobs) - failed, len(jobs), time.time() - t0, browser))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
