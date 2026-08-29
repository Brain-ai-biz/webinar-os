#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared helpers for Webinar-OS scripts. Standard library only."""
import json
import os
import sys
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def find_project_root(start=None):
    """Walk up from start (default cwd) until a folder with .claude/ or .env or .git is found."""
    p = Path(start or Path.cwd()).resolve()
    for cand in [p] + list(p.parents):
        if (cand / ".claude").exists() or (cand / ".env").exists() or (cand / ".git").exists():
            return cand
    return p


def read_env(root=None):
    """Parse .env (KEY=value lines) plus real environment. Real env wins."""
    root = Path(root or find_project_root())
    data = {}
    f = root / ".env"
    if f.exists():
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            data[k.strip()] = v
    for k, v in os.environ.items():
        if v:
            data[k] = v
    return data


def load_json(path):
    p = Path(path)
    if not p.exists():
        sys.exit("x not found: %s" % p)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit("x invalid JSON in %s: %s" % (p, e))


def save_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def http(method, url, token=None, data=None, headers=None, timeout=60):
    """Tiny HTTP helper (urllib). Returns (status, parsed_json_or_text)."""
    import urllib.request
    import urllib.error
    hdrs = {"User-Agent": "webinar-os/1.0"}
    if token:
        hdrs["Authorization"] = "Bearer " + token
    if headers:
        hdrs.update(headers)
    body = None
    if data is not None:
        if isinstance(data, (dict, list)):
            body = json.dumps(data).encode("utf-8")
            hdrs.setdefault("Content-Type", "application/json")
        else:
            body = data
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", errors="replace")
            status = r.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code
    except Exception as e:  # network down, DNS, timeout
        return 0, str(e)
    try:
        return status, json.loads(raw) if raw else {}
    except ValueError:
        return status, raw
