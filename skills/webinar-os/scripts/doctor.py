#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doctor.py - Webinar-OS: a 5-second check that the kit can run on this computer.
Standard library only. No keys, no network calls.

    python3 doctor.py            (Windows: python doctor.py)

Checks: Python version, the skill files, a writable outputs/ folder, and whether a
Chrome/Edge browser exists (only needed for the advanced creatives-to-PNG path).
Exit 1 if something blocking is missing.
"""
import os
import platform
import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SKILL = Path(__file__).resolve().parent.parent
REQUIRED = [
    "SKILL.md", "config.template.json",
    "templates/landing.html", "templates/thank-you.html", "templates/deck-basic.html",
    "templates/creative.html", "templates/consent-block.html",
    "scripts/render_pages.py",
    "reference/research.md", "reference/deck-structure.md", "reference/copy-blocks.md",
    "reference/manual-paths.md", "reference/schedule.md", "reference/webinar-day.md",
    "reference/design-system.md", "reference/advanced.md",
]

BROWSERS = {
    "Darwin": [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ],
    "Windows": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ],
    "Linux": [],
}


def find_browser():
    for p in BROWSERS.get(platform.system(), []):
        p = os.path.expandvars(p)
        if Path(p).exists():
            return p
    for name in ("google-chrome", "chrome", "chromium", "chromium-browser", "msedge", "microsoft-edge"):
        found = shutil.which(name)
        if found:
            return found
    if platform.system() == "Windows":
        local = os.environ.get("LOCALAPPDATA", "")
        for rel in (r"Google\Chrome\Application\chrome.exe", r"Microsoft\Edge\Application\msedge.exe"):
            p = Path(local) / rel
            if p.exists():
                return str(p)
    return ""


def main():
    ok = True
    v = sys.version_info
    if v >= (3, 9):
        print("ok Python %d.%d.%d" % (v.major, v.minor, v.micro))
    else:
        print("!! Python %d.%d - צריך 3.9 ומעלה (python.org/downloads)" % (v.major, v.minor))
        ok = False

    missing = [f for f in REQUIRED if not (SKILL / f).exists()]
    if missing:
        ok = False
        for f in missing:
            print("!! חסר בסקיל: %s" % f)
    else:
        print("ok כל קובצי הסקיל במקום (%d)" % len(REQUIRED))

    try:
        out = Path.cwd() / "outputs" / "webinars"
        out.mkdir(parents=True, exist_ok=True)
        test = out / ".write-test"
        test.write_text("ok", encoding="utf-8")
        test.unlink()
        print("ok אפשר לכתוב ל-%s" % out)
    except Exception as e:
        ok = False
        print("!! אי אפשר לכתוב לתיקיית הפרויקט (%s). לפתוח את Claude Code בתיקייה בתוך Documents / Desktop" % e)

    b = find_browser()
    print(("ok דפדפן לצילום קריאייטיבים (מתקדם): %s" % b) if b else
          ".. אין Chrome/Edge. לא חוסם: צריך רק למסלול המתקדם של קריאייטיבים כ-PNG")

    print("\n" + ("מוכן. הפעלה: /webinar-os" if ok else "יש מה לתקן (שורות !!)."))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
