#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
env_set.py - Webinar-OS: write a key into the project's .env safely.
Creates .env if missing, makes sure .gitignore ignores it, replaces an existing key in place.
Never prints the value back.

Usage (Windows: python instead of python3):
    python3 env_set.py NETLIFY_AUTH_TOKEN "nfp_xxx"
    python3 env_set.py --check NETLIFY_AUTH_TOKEN          -> exit 0 if set, 1 if not
    python3 env_set.py --list                              -> which Webinar-OS keys are set (names only)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_project_root, read_env, write_utf8  # noqa: E402

KNOWN = ["NETLIFY_AUTH_TOKEN", "DUB_API_KEY", "OPENAI_API_KEY"]


def read_lines(path):
    """Read a text file as lines. utf-8-sig drops the BOM that Windows editors
    (Notepad, PowerShell Out-File) prepend; the lstrip is a belt-and-braces guard.
    Writing back via write_utf8 leaves the file BOM-free with LF newlines."""
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if lines:
        lines[0] = lines[0].lstrip("\ufeff")
    return lines


def ensure_gitignore(root):
    gi = root / ".gitignore"
    lines = read_lines(gi)
    if not any(l.strip() in (".env", "/.env", ".env*") for l in lines):
        lines.append(".env")
        write_utf8(gi, "\n".join(lines).rstrip("\n") + "\n")
        return True
    return False


def set_key(root, key, value):
    f = root / ".env"
    lines = read_lines(f)
    out, done = [], False
    for l in lines:
        if l.split("=", 1)[0].strip() == key and not l.lstrip().startswith("#"):
            out.append("%s=%s" % (key, value))
            done = True
        else:
            out.append(l)
    if not done:
        if out and out[-1].strip():
            out.append("")
        out.append("%s=%s" % (key, value))
    write_utf8(f, "\n".join(out).rstrip("\n") + "\n")
    return done


def main():
    root = find_project_root()
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    if args[0] == "--list":
        env = read_env(root)
        for k in KNOWN:
            print("%-20s %s" % (k, "set" if env.get(k) else "missing"))
        return
    if args[0] == "--check":
        if len(args) < 2 or not args[1].strip():
            sys.exit("x usage: env_set.py --check KEY")
        key = args[1].strip()
        ok = bool(read_env(root).get(key))
        print("%s: %s" % (key, "set" if ok else "missing"))
        sys.exit(0 if ok else 1)
    key, value = args[0].strip(), " ".join(args[1:]).strip()
    if not key.replace("_", "").isalnum() or not value:
        sys.exit("x usage: env_set.py KEY value")
    added = ensure_gitignore(root)
    replaced = set_key(root, key, value)
    print("ok %s %s in %s" % (key, "updated" if replaced else "added", root / ".env"))
    if added:
        print("ok .env added to .gitignore")


if __name__ == "__main__":
    main()
