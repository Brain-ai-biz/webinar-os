#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dub_links.py - Webinar-OS: the 2 public short links via Dub (free plan is enough).
    <slug>-group -> WhatsApp group invite      (config.group_link  -> config.short_link)
    <slug>-live  -> Zoom / broadcast link      (config.broadcast_link -> config.short_broadcast_link)
Public posts always use the short link, so a destination can change later without touching posts.

Needs DUB_API_KEY in .env (app.dub.co -> Settings -> API Keys).

Usage (Windows: python instead of python3):
    python3 dub_links.py --config outputs/webinars/<slug>/config.json create        both (skips what exists)
    python3 dub_links.py --config ... create group|live
    python3 dub_links.py --config ... update group --url https://chat.whatsapp.com/NEW   (group 2 is full? swap here)
    python3 dub_links.py --config ... delete group|live      (removes the link from Dub + config)
    python3 dub_links.py --check

Safety: never adopts a link that already exists in the workspace. On a key collision it tries
<slug>-group-2, -3 ... Only ids stored in config (dub.group_id / dub.live_id) are ever PATCHed.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_project_root, read_env, http, load_json, save_json  # noqa: E402

API = "https://api.dub.co"
KINDS = {"group": ("group_link", "short_link", "group_id"),
         "live": ("broadcast_link", "short_broadcast_link", "live_id")}


def create(token, key, url, domain):
    for suffix in ["", "-2", "-3", "-4"]:
        body = {"url": url, "key": key + suffix}
        if domain:
            body["domain"] = domain
        s, d = http("POST", API + "/links", token, body, timeout=30)
        if s in (200, 201) and isinstance(d, dict) and d.get("id"):
            return d
        msg = str(d)
        if s == 409 or "already exists" in msg or "conflict" in msg.lower():
            continue
        sys.exit("x Dub create failed (status %s): %s" % (s, msg[:300]))
    sys.exit("x Dub: keys %s .. %s-4 all taken. pick another slug" % (key, key))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--domain", help="custom domain in your Dub workspace (default: dub.sh)")
    ap.add_argument("action", nargs="?", choices=["create", "update", "delete"])
    ap.add_argument("kind", nargs="?", choices=["group", "live"])
    ap.add_argument("--url", help="new destination (update)")
    args = ap.parse_args()

    token = read_env(find_project_root()).get("DUB_API_KEY")
    if not token:
        env_set = Path(__file__).resolve().parent / "env_set.py"
        sys.exit("x DUB_API_KEY missing. app.dub.co -> Settings -> API Keys -> Create, then: "
                 "%s %s DUB_API_KEY <key>" % (Path(sys.executable).name, env_set))
    s, ws = http("GET", API + "/links?pageSize=1", token, timeout=30)
    if s != 200:
        sys.exit("x Dub key rejected (status %s): %s" % (s, str(ws)[:200]))
    print("ok Dub key valid")
    if args.check:
        return
    if not args.config or not args.action:
        ap.error("--config and an action are required")

    cfg_path = Path(args.config).resolve()
    cfg = load_json(cfg_path)
    slug = str(cfg.get("slug") or "").strip()
    dub = cfg.setdefault("dub", {})
    kinds = [args.kind] if args.kind else ["group", "live"]

    for kind in kinds:
        src_key, short_key, id_key = KINDS[kind]
        if args.action == "create":
            if dub.get(id_key):
                print(".. %s link exists already: %s" % (kind, cfg.get(short_key)))
                continue
            dest = str(cfg.get(src_key) or "").strip()
            if not dest.startswith("http"):
                print(".. %s: config.%s is empty, skipping (fill it and run again)" % (kind, src_key))
                continue
            d = create(token, "%s-%s" % (slug, kind), dest, args.domain)
            dub[id_key] = d["id"]
            cfg[short_key] = d["shortLink"]
            print("ok %s: %s -> %s" % (kind, d["shortLink"], dest))
        elif args.action == "delete":
            link_id = dub.get(id_key)
            if not link_id:
                print(".. no %s link in config" % kind)
                continue
            s, d = http("DELETE", "%s/links/%s" % (API, link_id), token, timeout=30)
            if s not in (200, 204):
                sys.exit("x Dub delete failed (status %s): %s" % (s, str(d)[:300]))
            dub.pop(id_key, None)
            cfg[short_key] = ""
            print("ok %s link deleted" % kind)
        else:
            if not args.url or not args.url.startswith("http"):
                ap.error("--url https://... required for update")
            link_id = dub.get(id_key)
            if not link_id:
                sys.exit("x no %s link in config (create it first)" % kind)
            s, d = http("PATCH", "%s/links/%s" % (API, link_id), token, {"url": args.url}, timeout=30)
            if s != 200:
                sys.exit("x Dub update failed (status %s): %s" % (s, str(d)[:300]))
            cfg[src_key] = args.url
            print("ok %s now points to %s" % (cfg.get(short_key), args.url))
    save_json(cfg_path, cfg)
    print("ok config updated")


if __name__ == "__main__":
    main()
