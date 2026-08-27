#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_pages.py - Webinar-OS: builds the landing page, thank-you page and 5 creatives
from config.json + copy.json. Standard library only (Python 3.9+), works on Windows/Mac/Linux.

Usage:
    python3 render_pages.py --config outputs/webinars/<slug>/config.json
    python3 render_pages.py --config ... --out outputs/webinars/<slug>/out
    python3 render_pages.py --config ... --copy path/to/copy.json
    python3 render_pages.py --config ... --no-creatives

Outputs (default: <config dir>/out/):
    out/index.html                 landing page
    out/thank-you/index.html       thank-you page
    out/creatives/<id>.html        5 creatives (1080x1080; add ?story for 9:16)

Config keys used (all optional except slug):
    slug, project_name, date_he, time, event_iso, group_link, page_url,
    brand_name, brand_url, privacy_url, accessibility_url, hero_photo, creative_photo,
    capture_endpoint            JSON POST endpoint (Make / Zapier / n8n / Worker / own server)
    form_action + form_fields   Google Form "formResponse" URL + {name,email,phone} field names
                                (neither set -> page shows a WhatsApp-group button, no form)
    brand.{bg,panel,text,muted,accent,accent_2,on_accent,font,logo}

Template mini-syntax (implemented here, no dependency):
    {{a.b.c}}                       dotted path, HTML-escaped, newlines -> <br>
    {{{a.b}}}                       raw (used for the consent block)
    {{#each a.list}}...{{.}}...{{/each}}   list items ({{.key}} for dict items)
    {{#if a.b}}...{{/if}}           block kept only when the value is truthy
Missing keys render as "" with a warning - never a crash.
"""

import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"

RE_EACH = re.compile(r"\{\{#each ([\w.]+)\}\}(.*?)\{\{/each\}\}", re.S)
RE_IF = re.compile(r"\{\{#if ([\w.]+)\}\}(.*?)\{\{/if\}\}", re.S)
RE_RAW = re.compile(r"\{\{\{([\w.]+)\}\}\}")
RE_VAR = re.compile(r"\{\{([\w.]+)\}\}")
RE_ITEM = re.compile(r"\{\{\.(\w*)\}\}")

DEFAULT_BRAND = {
    "bg": "#0B1220",
    "panel": "#131C2E",
    "text": "#F5F7FB",
    "muted": "#9AA6BD",
    "accent": "#F5A623",
    "accent_2": "#FFC857",
    "on_accent": "#1A1200",
    "font": "Assistant",
    "logo": "",
}

CREATIVE_IDS = ["tomorrow", "tomorrow_time", "today", "one_hour", "live"]

_warned = set()


def warn(msg):
    if msg not in _warned:
        _warned.add(msg)
        print("  ! " + msg, file=sys.stderr)


def lookup(ctx, path):
    cur = ctx
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return None
    return cur


def esc(value):
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    return html.escape(str(value), quote=True).replace("\n", "<br>")


def render(template, ctx):
    def each(m):
        path, body = m.group(1), m.group(2)
        items = lookup(ctx, path)
        if items is None:
            warn("missing list '%s' -> rendered empty" % path)
            return ""
        if not isinstance(items, list):
            items = [items]
        out = []
        for item in items:
            def item_sub(mm, item=item):
                key = mm.group(1)
                if not key:
                    return esc(item)
                return esc(item.get(key)) if isinstance(item, dict) else ""
            out.append(RE_ITEM.sub(item_sub, body))
        return "".join(out)

    def cond(m):
        return m.group(2) if lookup(ctx, m.group(1)) else ""

    def raw(m):
        v = lookup(ctx, m.group(1))
        if v is None:
            warn("missing key '%s' -> rendered empty" % m.group(1))
            return ""
        return str(v)

    def var(m):
        v = lookup(ctx, m.group(1))
        if v is None:
            warn("missing key '%s' -> rendered empty" % m.group(1))
            return ""
        return esc(v)

    out = RE_EACH.sub(each, template)
    out = RE_IF.sub(cond, out)
    out = RE_RAW.sub(raw, out)   # raw block may itself contain {{vars}} -> resolved next
    out = RE_VAR.sub(var, out)
    return out


def load_json(path, required=True):
    p = Path(path)
    if not p.exists():
        if required:
            sys.exit("x not found: %s" % p)
        warn("%s not found - copy keys will render empty" % p)
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit("x invalid JSON in %s: %s" % (p, e))


def hex_to_rgb(value):
    v = str(value or "").strip().lstrip("#")
    if len(v) == 3:
        v = "".join(ch * 2 for ch in v)
    if len(v) != 6:
        return "245,166,35"
    try:
        return "%d,%d,%d" % (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))
    except ValueError:
        return "245,166,35"


def resolve_asset(value, config_dir, out_dir):
    """URL stays as is; a local file is copied next to index.html and referenced by name."""
    value = str(value or "").strip()
    if not value or value.startswith(("http://", "https://", "/", "data:")):
        return value
    src = Path(value)
    if not src.is_absolute():
        src = (config_dir / value) if (config_dir / value).exists() else (Path.cwd() / value)
    if src.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(out_dir / src.name))
        return src.name
    warn("asset '%s' not found -> skipped" % value)
    return ""


HEBREW = re.compile(r"[\u0590-\u05FF]")


def url_or_empty(value):
    """A URL field still holding the template's Hebrew placeholder text renders as empty."""
    v = str(value or "").strip()
    return "" if (not v or HEBREW.search(v)) else v


def build_context(config, copy, config_dir, out_dir):
    slug = str(config.get("slug") or "").strip()
    if not slug or slug.startswith("SHORT-KEBAB"):
        sys.exit("x config.slug is required (kebab-case, e.g. 'ai-webinar')")
    ctx = dict(copy)          # copy keys at top level: ticker, hero, problem, ...
    ctx.update(config)        # config keys win on collision
    ctx["slug"] = slug
    ctx.setdefault("project_name", slug)
    for k in ("date_he", "time"):
        if not ctx.get(k):
            warn("config.%s missing -> rendered empty" % k)
            ctx[k] = ""
    ctx["group_link"] = url_or_empty(ctx.get("group_link"))
    ctx["event_iso"] = url_or_empty(ctx.get("event_iso"))
    ctx["page_url"] = url_or_empty(ctx.get("page_url"))
    ctx["brand_name"] = str(ctx.get("brand_name") or ctx.get("host") or "").strip() or slug
    ctx["brand_url"] = url_or_empty(ctx.get("brand_url")) or "#"
    ctx["privacy_url"] = url_or_empty(ctx.get("privacy_url"))
    ctx["accessibility_url"] = url_or_empty(ctx.get("accessibility_url"))
    if not ctx["privacy_url"]:
        warn("config.privacy_url missing -> consent text has no privacy link (add one before going live)")

    # brand tokens
    brand = dict(DEFAULT_BRAND)
    user_brand = ctx.get("brand") or {}
    if isinstance(user_brand, dict):
        for k, v in user_brand.items():
            if v not in (None, "") and not (isinstance(v, str) and HEBREW.search(v)):
                brand[k] = v
    brand["accent_rgb"] = hex_to_rgb(brand["accent"])
    brand["google_font_query"] = str(brand["font"]).replace(" ", "+") + ":wght@300;400;600;700;800"
    brand["logo"] = resolve_asset(brand.get("logo"), config_dir, out_dir)
    ctx["brand"] = brand

    # capture mode
    endpoint = url_or_empty(ctx.get("capture_endpoint")).rstrip("/")
    form_action = url_or_empty(ctx.get("form_action"))
    if endpoint and not endpoint.startswith("http"):
        warn("capture_endpoint '%s' is not a URL -> ignored" % endpoint)
        endpoint = ""
    if form_action and not form_action.startswith("http"):
        warn("form_action '%s' is not a URL -> ignored" % form_action)
        form_action = ""
    ctx["capture_endpoint"] = endpoint
    ctx["form_action"] = form_action
    ctx["mode_form"] = bool(endpoint or form_action)
    ctx["mode_button"] = not ctx["mode_form"]
    if ctx["mode_button"] and not ctx["group_link"]:
        warn("no capture_endpoint / form_action AND no group_link -> the registration card has nothing to point to")
    fields = ctx.get("form_fields") or {}
    clean = lambda k: (str(fields.get(k) or "").strip() if not HEBREW.search(str(fields.get(k) or "")) else "")
    ctx["form_fields"] = {
        "name": clean("name") or "name",
        "email": clean("email") or "email",
        "phone": clean("phone") or "phone",
        "consent": clean("consent") or "consent",
    }

    # photos: URL as is, local file copied next to index.html
    ctx["hero_photo"] = resolve_asset(url_or_empty(ctx.get("hero_photo")), config_dir, out_dir)
    ctx["creative_photo"] = resolve_asset(url_or_empty(ctx.get("creative_photo")), config_dir, out_dir / "creatives")

    # consent block read fresh at render time
    ctx["consent_block"] = (TEMPLATES / "consent-block.html").read_text(encoding="utf-8")
    return ctx


def render_creatives(ctx, out_dir):
    tpl = (TEMPLATES / "creative.html").read_text(encoding="utf-8")
    items = ctx.get("creatives") or []
    if not items:
        warn("copy.creatives is empty -> no creatives rendered")
        return []
    cdir = out_dir / "creatives"
    cdir.mkdir(parents=True, exist_ok=True)
    written = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        cid = str(item.get("id") or (CREATIVE_IDS[i] if i < len(CREATIVE_IDS) else "creative-%d" % (i + 1)))
        local = dict(ctx)
        local["punch"] = item.get("punch", "")
        local["subline"] = item.get("subline", "")
        local["date_line"] = item.get("date_line") or ("%s · %s" % (ctx.get("date_he", ""), ctx.get("time", "")))
        local["link"] = item.get("link") or ctx.get("short_link") or ""
        p = cdir / ("%s.html" % cid)
        p.write_text(render(tpl, local), encoding="utf-8")
        written.append(p)
    return written


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, help="outputs/webinars/<slug>/config.json")
    ap.add_argument("--copy", help="copy.json (default: next to config.json)")
    ap.add_argument("--out", help="output dir (default: <config dir>/out)")
    ap.add_argument("--no-creatives", action="store_true", help="skip the 5 creatives")
    args = ap.parse_args()

    config_path = Path(args.config).resolve()
    config = load_json(config_path)
    config_dir = config_path.parent
    copy_path = Path(args.copy).resolve() if args.copy else config_dir / "copy.json"
    copy = load_json(copy_path, required=False)

    out_dir = Path(args.out).resolve() if args.out else config_dir / "out"
    ctx = build_context(config, copy, config_dir, out_dir)

    landing_tpl = (TEMPLATES / "landing.html").read_text(encoding="utf-8")
    ty_tpl = (TEMPLATES / "thank-you.html").read_text(encoding="utf-8")

    landing_out = out_dir / "index.html"
    ty_out = out_dir / "thank-you" / "index.html"
    ty_out.parent.mkdir(parents=True, exist_ok=True)

    print("-> rendering webinar '%s' (%s)" % (ctx["slug"], ctx.get("project_name")))
    landing_out.write_text(render(landing_tpl, ctx), encoding="utf-8")
    ty_out.write_text(render(ty_tpl, ctx), encoding="utf-8")
    outputs = [landing_out, ty_out]
    if not args.no_creatives:
        outputs += render_creatives(ctx, out_dir)

    for p in outputs:
        print("ok %s  (%d KB)" % (p, max(1, p.stat().st_size // 1024)))
    mode = "JSON endpoint: " + ctx["capture_endpoint"] if ctx["capture_endpoint"] else (
        "form POST: " + ctx["form_action"] if ctx["form_action"] else "WhatsApp-group button only (no form)")
    print("   capture mode: " + mode)
    if ctx["page_url"]:
        print("   live at: %s  ->  %sthank-you/" % (ctx["page_url"], ctx["page_url"].rstrip("/") + "/"))


if __name__ == "__main__":
    main()
