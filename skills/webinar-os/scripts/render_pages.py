#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_pages.py - Webinar-OS: renders the landing page, the thank-you page, the deck
(and, in the advanced path, the creatives) from the JSON files of one webinar.
Standard library only (Python 3.9+). Works on Windows / Mac / Linux.

Usage:
    python3 render_pages.py --config outputs/webinars/<slug>/config.json
    python3 render_pages.py --config ... --only pages      landing + thank-you only
    python3 render_pages.py --config ... --only deck       deck.html + script.md only
    python3 render_pages.py --config ... --creatives       also render copy.creatives (advanced)

Inputs (next to config.json unless overridden):
    config.json   facts: slug, project_name, business_name, date_he, time, event_iso, group_link, ...
    copy.json     landing + thank-you copy (8 sections + thank_you)      -> landing/
    deck.json     slides (pattern + fields + notes)                      -> deck.html + script.md

Outputs (default: the folder of config.json):
    landing/index.html              landing page
    landing/thank-you/index.html    thank-you page
    deck.html                       presentation (open in a browser; ?print for PDF)
    script.md                       presenter script from deck.json notes, timed at 2.5 words/sec
    landing/creatives/<id>.html     only with --creatives

Registration mode (decided automatically):
    form_action (Google Form "formResponse" URL) or capture_endpoint -> styled form -> thank-you
    neither                                                          -> one button to group_link

Template mini-syntax (implemented here, no dependency):
    {{a.b.c}}                        dotted path, HTML-escaped, newlines -> <br>
    {{{a.b}}}                        raw HTML
    {{#each a.list}}...{{.}}...{{/each}}   list items ({{.key}} for dict items)
    {{#if a.b}}...{{/if}}            block kept only when the value is truthy
Missing keys render as "" with a warning - never a crash.
"""

import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"

RE_EACH = re.compile(r"\{\{#each ([\w.]+)\}\}(.*?)\{\{/each\}\}", re.S)
RE_IF = re.compile(r"\{\{#if ([\w.]+)\}\}(.*?)\{\{/if\}\}", re.S)
RE_RAW = re.compile(r"\{\{\{([\w.]+)\}\}\}")
RE_VAR = re.compile(r"\{\{([\w.]+)\}\}")
RE_ITEM = re.compile(r"\{\{\.(\w*)\}\}")
RE_TIME = re.compile(r"(\d{1,2}:\d{2})")
HEBREW = re.compile(u"[֐-׿]")

# ===== the design system: ONE token block, identical in all four templates =====
DEFAULT_BRAND = {
    "bg": "#0A0E1A",
    "surface": "#131A2C",
    "ink": "#F4F6FB",
    "muted": "#9BA6C0",
    "accent": "#F5B54A",
    "accent_2": "#FF7A59",
    "radius": "18px",
    "font": "Heebo",
    "logo": "",
}

WORDS_PER_SEC = 2.5
CREATIVE_IDS = ["tomorrow", "tomorrow_time", "today", "one_hour", "live"]

_warned = set()


def warn(msg):
    if msg not in _warned:
        _warned.add(msg)
        print("  ! " + msg, file=sys.stderr)


# ---------------------------------------------------------------- template engine
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
    out = RE_RAW.sub(raw, out)
    out = RE_VAR.sub(var, out)
    return out


# ---------------------------------------------------------------- helpers
def load_json(path, required=True):
    p = Path(path)
    if not p.exists():
        if required:
            sys.exit("x not found: %s" % p)
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit("x invalid JSON in %s: %s" % (p, e))


def hex_to_rgb(value):
    v = str(value or "").strip().lstrip("#")
    if len(v) == 3:
        v = "".join(ch * 2 for ch in v)
    if len(v) != 6:
        return "245,181,74"
    try:
        return "%d,%d,%d" % (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))
    except ValueError:
        return "245,181,74"


def url_or_empty(value):
    """A URL field still holding Hebrew placeholder text renders as empty."""
    v = str(value or "").strip()
    return "" if (not v or HEBREW.search(v)) else v


def resolve_asset(value, config_dir, out_dir):
    """URL stays as is; a local file is copied next to the output and referenced by name."""
    value = str(value or "").strip()
    if not value or HEBREW.search(value):
        return ""
    if value.startswith(("http://", "https://", "/", "data:")):
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


def build_brand(config, config_dir, out_dir):
    brand = dict(DEFAULT_BRAND)
    user = config.get("brand") or {}
    if isinstance(user, dict):
        for k, v in user.items():
            if v not in (None, "") and not (isinstance(v, str) and HEBREW.search(v)):
                brand[k] = v
    brand["accent_rgb"] = hex_to_rgb(brand["accent"])
    brand["logo"] = resolve_asset(brand.get("logo"), config_dir, out_dir)
    return brand


def base_context(config, config_dir, out_dir):
    ctx = dict(config)
    slug = str(config.get("slug") or "").strip()
    if not slug or HEBREW.search(slug):
        sys.exit("x config.slug is required (kebab-case, e.g. 'nutrition-after-birth')")
    ctx["slug"] = slug
    ctx.setdefault("project_name", slug)
    ctx["business_name"] = str(ctx.get("business_name") or ctx.get("host_name") or "").strip() or slug
    for k in ("date_he", "time"):
        if not ctx.get(k):
            warn("config.%s missing -> rendered empty" % k)
            ctx[k] = ""
    if not ctx.get("platform"):
        ctx["platform"] = "זום"
    if not ctx.get("duration_min"):
        ctx["duration_min"] = 60
    for k in ("group_link", "event_iso", "page_url", "privacy_url", "terms_url", "accessibility_url",
              "og_image", "capture_endpoint", "form_action"):
        ctx[k] = url_or_empty(ctx.get(k))
    ctx["contact_line"] = str(ctx.get("contact_line") or "").strip()
    ctx["brand"] = build_brand(config, config_dir, out_dir)
    return ctx


# ---------------------------------------------------------------- pages
def pages_context(config, copy, config_dir, out_dir):
    ctx = dict(copy)
    ctx.update(base_context(config, config_dir, out_dir))
    if not ctx["privacy_url"]:
        warn("config.privacy_url missing -> consent text has no privacy link (add one before going live)")
    ctx["no_privacy"] = not ctx["privacy_url"]
    ctx["no_terms"] = not ctx["terms_url"]

    # registration mode
    endpoint = ctx["capture_endpoint"].rstrip("/")
    form_action = ctx["form_action"]
    if endpoint and not endpoint.startswith("http"):
        warn("capture_endpoint is not a URL -> ignored")
        endpoint = ""
    if form_action and not form_action.startswith("http"):
        warn("form_action is not a URL -> ignored")
        form_action = ""
    ctx["capture_endpoint"] = endpoint
    ctx["form_action"] = form_action
    ctx["mode_form"] = bool(endpoint or form_action)
    ctx["mode_button"] = not ctx["mode_form"]
    if ctx["mode_button"] and not ctx["group_link"]:
        warn("no form_action AND no group_link -> the registration button has nowhere to point")
    fields = ctx.get("form_fields") or {}

    def clean(k, default):
        v = str(fields.get(k) or "").strip()
        return default if (not v or HEBREW.search(v)) else v
    ctx["form_fields"] = {
        "name": clean("name", "first_name"),
        "email": clean("email", "email"),
        "phone": clean("phone", "phone"),
        "consent": clean("consent", "consent"),
    }

    # photos (optional): URL as is, local file copied next to index.html
    ctx["hero_photo"] = resolve_asset(ctx.get("hero_photo"), config_dir, out_dir)
    ctx["host_photo"] = resolve_asset(ctx.get("host_photo"), config_dir, out_dir)
    ctx["host_photo_class"] = "has-photo" if ctx["host_photo"] else ""

    # numbered gains
    gains = ctx.get("gains") if isinstance(ctx.get("gains"), dict) else {}
    items = []
    for i, it in enumerate(gains.get("items") or []):
        d = dict(it) if isinstance(it, dict) else {"title": str(it), "text": ""}
        d["i"] = i
        d["n"] = i + 1
        items.append(d)
    if len(items) != 4:
        warn("gains.items has %d items (the template expects 4)" % len(items))
    ctx["gains"] = dict(gains, items=items)

    # thank_you fallbacks
    ty = ctx.get("thank_you") if isinstance(ctx.get("thank_you"), dict) else {}
    ty.setdefault("title", "נרשמת · %s" % ctx["project_name"])
    ctx["thank_you"] = ty

    ctx["consent_block"] = render((TEMPLATES / "consent-block.html").read_text(encoding="utf-8"), ctx)
    return ctx


def render_pages(ctx, out_dir):
    landing_dir = out_dir / "landing"
    ty_out = landing_dir / "thank-you" / "index.html"
    ty_out.parent.mkdir(parents=True, exist_ok=True)
    landing_out = landing_dir / "index.html"
    landing_out.write_text(render((TEMPLATES / "landing.html").read_text(encoding="utf-8"), ctx), encoding="utf-8")
    ty_out.write_text(render((TEMPLATES / "thank-you.html").read_text(encoding="utf-8"), ctx), encoding="utf-8")
    return [landing_out, ty_out]


# ---------------------------------------------------------------- creatives (advanced)
def render_creatives(ctx, out_dir, config_dir):
    tpl = (TEMPLATES / "creative.html").read_text(encoding="utf-8")
    items = ctx.get("creatives") or []
    if not items:
        warn("copy.creatives is empty -> no creatives rendered")
        return []
    cdir = out_dir / "landing" / "creatives"
    cdir.mkdir(parents=True, exist_ok=True)
    ctx["creative_photo"] = resolve_asset(ctx.get("creative_photo"), config_dir, cdir)
    written = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        cid = str(item.get("id") or (CREATIVE_IDS[i] if i < len(CREATIVE_IDS) else "creative-%d" % (i + 1)))
        local = dict(ctx)
        punch = str(item.get("punch", ""))
        local["punch"] = punch
        local["subline"] = item.get("subline", "")
        local["date_line"] = item.get("date_line") or ("%s · %s" % (ctx.get("date_he", ""), ctx.get("time", "")))
        local["link"] = item.get("link") or ctx.get("short_link") or ""
        local["punch_html"] = RE_TIME.sub(r'<span class="hl">\1</span>', esc(punch))
        local["punch_size"] = "long" if len(punch) > 14 else ""
        local["creative_class"] = "live" if cid == "live" else ""
        local["tag_text"] = item.get("tag") or ("LIVE עכשיו" if cid == "live" else "שידור חי")
        p = cdir / ("%s.html" % cid)
        p.write_text(render(tpl, local), encoding="utf-8")
        written.append(p)
    return written


# ---------------------------------------------------------------- deck
def _title_html(text, highlight):
    """Wraps the highlighted words (if given, and present) in the warm gradient span."""
    t = esc(text)
    h = esc(highlight or "")
    if h and h in t:
        return t.replace(h, '<span class="warm">%s</span>' % h, 1)
    return t


def slide_html(s, idx, ctx):
    pat = str(s.get("pattern") or "bullets")
    label = esc(s.get("label") or s.get("title") or s.get("quote") or pat)
    kicker = '<span class="kicker">%s</span>' % esc(s["kicker"]) if s.get("kicker") else ""
    head = '<section class="slide" data-pattern="%s" aria-label="%s">' % (esc(pat), label)
    body = ""
    if pat == "title":
        ev = s.get("event") or {}
        if isinstance(ev, str):
            ev = {"line": ev}
        chips = []
        if ev.get("line"):
            chips.append("<span>%s</span>" % esc(ev["line"]))
        else:
            for key, icon in (("date", "📅"), ("time", "🕗"), ("host", "🎤")):
                val = ev.get(key) or ctx.get({"date": "date_he", "time": "time", "host": "host_name"}[key])
                if val:
                    chips.append("<span>%s <b>%s</b></span>" % (icon, esc(val)))
        body = "%s<h1>%s</h1>%s<div class=\"event\">%s</div>" % (
            ('<span class="eyebrow">%s</span>' % esc(s["kicker"])) if s.get("kicker") else "",
            _title_html(s.get("title", ""), s.get("highlight")),
            ('<p class="sub">%s</p>' % esc(s["sub"])) if s.get("sub") else "",
            "".join(chips))
    elif pat == "section":
        body = '<div class="n">%s</div><h2>%s</h2>%s' % (
            esc(s.get("n") or "%02d" % idx),
            _title_html(s.get("title", ""), s.get("highlight")),
            ('<p class="sub">%s</p>' % esc(s["sub"])) if s.get("sub") else "")
    elif pat == "bullets":
        reveal = s.get("reveal", True)
        lis = "".join('<li%s>%s</li>' % (' class="reveal"' if reveal else "", esc(it)) for it in (s.get("items") or []))
        body = "%s<h2>%s</h2><ul>%s</ul>" % (kicker, _title_html(s.get("title", ""), s.get("highlight")), lis)
    elif pat == "three-columns":
        cards = []
        for i, c in enumerate(s.get("cards") or []):
            c = c if isinstance(c, dict) else {"title": str(c)}
            cards.append('<div class="card"><div class="icon">%s</div><h3>%s</h3><p>%s</p></div>' % (
                esc(c.get("icon") or str(i + 1)), esc(c.get("title", "")), esc(c.get("text", ""))))
        body = '%s<h2>%s</h2><div class="cols">%s</div>' % (kicker, _title_html(s.get("title", ""), s.get("highlight")), "".join(cards))
    elif pat == "big-stat":
        if not s.get("source"):
            warn("slide %d (big-stat) has no source -> a number without a source must not go on a slide" % idx)
        src = esc(s.get("source", ""))
        if s.get("source_url"):
            src = '%s · <a href="%s" target="_blank" rel="noopener">%s</a>' % (src, esc(s["source_url"]), esc(s.get("source_label") or "לינק"))
        body = '%s<div class="big-num">%s</div><p class="claim">%s</p><div class="source">מקור: %s</div>' % (
            kicker, esc(s.get("num", "")), esc(s.get("claim", "")), src)
    elif pat == "quote":
        body = '<blockquote>%s</blockquote>%s' % (
            esc(s.get("quote") or s.get("title", "")),
            ('<div class="who">%s</div>' % esc(s["who"])) if s.get("who") else "")
    elif pat == "screenshot":
        src = esc(s.get("src") or "screenshot-%d.png" % idx)
        body = '<h2>%s</h2><div class="frame" data-placeholder="%s"><div class="chrome"><i></i><i></i><i></i></div><img src="%s" alt="%s" onerror="this.hidden=true"></div>' % (
            esc(s.get("title", "")), esc(s.get("placeholder") or "כאן צילום מסך (%s)" % src), src, esc(s.get("alt") or s.get("title", "")))
    elif pat == "cta":
        btn = ""
        if s.get("button"):
            btn = '<a class="btn" href="%s" target="_blank" rel="noopener">%s</a>' % (esc(s.get("link") or ctx.get("group_link") or "#"), esc(s["button"]))
        body = '%s<h2>%s</h2>%s%s' % (
            kicker, _title_html(s.get("title", ""), s.get("highlight")), btn,
            ('<p class="small">%s</p>' % esc(s["small"])) if s.get("small") else "")
    else:
        warn("slide %d: unknown pattern '%s' -> rendered as bullets" % (idx, pat))
        return slide_html(dict(s, pattern="bullets"), idx, ctx)
    return head + body + "</section>\n"


def render_deck(config, deck, config_dir, out_dir):
    ctx = base_context(config, config_dir, out_dir)
    ctx["deck"] = {"title": deck.get("title") or ctx["project_name"]}
    slides = deck.get("slides") or []
    if not slides:
        sys.exit("x deck.json has no slides")
    ctx["slides_html"] = "".join(slide_html(s, i + 1, ctx) for i, s in enumerate(slides))
    tpl = (TEMPLATES / "deck-basic.html").read_text(encoding="utf-8")
    deck_out = out_dir / "deck.html"
    deck_out.write_text(render(tpl, ctx), encoding="utf-8")

    # presenter script, timed at 2.5 words/sec (count words, never guess)
    lines = ["# תסריט הגשה · %s" % ctx["deck"]["title"], "",
             "קצב: %.1f מילים לשנייה. `[עצירה]` = שאלה לקהל, `[צ'אט]` = לבקש תגובה בצ'אט. שקף = רעיון אחד." % WORDS_PER_SEC, ""]
    total_words = 0
    for i, s in enumerate(slides, 1):
        notes = str(s.get("notes") or "").strip()
        words = len(re.findall(r"\S+", re.sub(r"\[[^\]]+\]", "", notes)))
        total_words += words
        secs = int(round(words / WORDS_PER_SEC))
        title = s.get("title") or s.get("quote") or s.get("claim") or s.get("pattern")
        lines.append("## שקף %d · %s · %s" % (i, s.get("pattern", ""), title))
        lines.append("")
        lines.append(notes if notes else "(אין הערות לשקף הזה)")
        lines.append("")
        lines.append("*%d מילים · כ-%d שניות*" % (words, secs))
        lines.append("")
    mins = total_words / WORDS_PER_SEC / 60
    lines.append("---")
    lines.append("")
    lines.append("**סך הכל:** %d שקפים · %d מילים · כ-%d דקות דיבור (בלי שאלות ותשובות)." % (len(slides), total_words, round(mins)))
    script_out = out_dir / "script.md"
    script_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return [deck_out, script_out], len(slides), round(mins)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, help="outputs/webinars/<slug>/config.json")
    ap.add_argument("--copy", help="copy.json (default: next to config.json)")
    ap.add_argument("--deck", help="deck.json (default: next to config.json)")
    ap.add_argument("--out", help="output folder (default: the folder of config.json)")
    ap.add_argument("--only", choices=["pages", "deck"], help="render only the pages or only the deck")
    ap.add_argument("--creatives", action="store_true", help="also render copy.creatives (advanced)")
    args = ap.parse_args()

    config_path = Path(args.config).resolve()
    config = load_json(config_path)
    config_dir = config_path.parent
    out_dir = Path(args.out).resolve() if args.out else config_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    copy_path = Path(args.copy).resolve() if args.copy else config_dir / "copy.json"
    deck_path = Path(args.deck).resolve() if args.deck else config_dir / "deck.json"

    print("-> rendering '%s'" % (config.get("project_name") or config.get("slug")))
    outputs = []

    if args.only != "deck":
        copy = load_json(copy_path, required=False)
        if copy is None:
            if args.only == "pages":
                sys.exit("x %s not found" % copy_path)
            print("   (no copy.json yet -> pages skipped)")
        else:
            ctx = pages_context(config, copy, config_dir, out_dir / "landing")
            outputs += render_pages(ctx, out_dir)
            if args.creatives:
                outputs += render_creatives(ctx, out_dir, config_dir)
            mode = ("JSON endpoint: " + ctx["capture_endpoint"]) if ctx["capture_endpoint"] else (
                ("form POST: " + ctx["form_action"]) if ctx["form_action"] else "one button to the WhatsApp group (no form)")
            print("   registration: " + mode)

    if args.only != "pages":
        deck = load_json(deck_path, required=False)
        if deck is None:
            if args.only == "deck":
                sys.exit("x %s not found" % deck_path)
            print("   (no deck.json yet -> deck skipped)")
        else:
            files, n, mins = render_deck(config, deck, config_dir, out_dir)
            outputs += files
            print("   deck: %d slides, ~%d minutes of speaking in script.md" % (n, mins))

    for p in outputs:
        print("ok %s  (%d KB)" % (p, max(1, p.stat().st_size // 1024)))
    if not outputs:
        sys.exit("x nothing rendered: add copy.json and/or deck.json next to config.json")


if __name__ == "__main__":
    main()
