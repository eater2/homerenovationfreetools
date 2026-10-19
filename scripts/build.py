"""Generate README.md, catalog.json and llms.txt from data/tools.json and data/ratings.json.

Edit the data files, then run: python scripts/build.py
"""
import html
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = "https://raw.githubusercontent.com/eater2/homerenovationfreetools/main"
MIN_REVIEWS = 3
SKILL = "home-renovation-free-tools"
SITE = "https://home-renovation-free-tools.vercel.app"
MCP_URL = f"{SITE}/mcp"
SKILL_ZIP_URL = f"{SITE}/{SKILL}-skill.zip"


def esc(s):
    return html.escape(s, quote=False)


def load(name, default):
    p = DATA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def short_count(n):
    for div, suf in ((1_000_000, "M"), (1_000, "k")):
        if n >= div:
            return f"{n / div:.1f}".rstrip("0").rstrip(".") + suf
    return str(n)


def stars(rating):
    return "⭐" * max(1, round(rating))


# ---------- ratings ----------

def rating_lines(r):
    """Proof under the tool name: user rating and review count (SourceForge, App Store), GitHub stars."""
    out = []
    for s in r:
        # A score from one or two reviews says little, so the README waits for MIN_REVIEWS (catalog.json keeps it).
        if s["source"] in ("sourceforge", "appstore") and s.get("rating") and s.get("count", 0) >= MIN_REVIEWS:
            label = "SourceForge" if s["source"] == "sourceforge" else "App Store"
            noun = "review" if s["source"] == "sourceforge" else "rating"
            plural = noun if s["count"] == 1 else noun + "s"
            out.append(f'{stars(s["rating"])} <b>{s["rating"]:.1f}</b>/5 · '
                       f'<a href="{esc(s["url"])}" title="{label}">{short_count(s["count"])} {plural}</a> <sub>{label}</sub>')
        elif s["source"] == "github" and s.get("stars"):
            out.append(f'<a href="{esc(s["url"])}"><img alt="GitHub {s["stars"]} stars {esc(s["repo"])}" '
                       f'src="https://img.shields.io/badge/%E2%98%85-{short_count(s["stars"])}-24292f?logo=github&logoColor=white"></a>')
    return out


def name_cell(it, ratings):
    lines = rating_lines(ratings.get(it["id"], []))
    return esc(it["name"]) + "".join(f"<br>{l}" for l in lines)


def ratings_note(ratings):
    dates = sorted(s["fetched_at"][:10] for r in ratings.values() for s in r)
    if not dates:
        return ""
    return (f"<p><sub>⭐ Under a tool's name: user rating and number of reviews on SourceForge or the App Store, "
            f"or GitHub stars for open-source tools. Fetched {dates[-1]}.</sub></p>\n\n")


# ---------- README ----------

def link(url, label):
    return f'<a href="{esc(url)}">{esc(label)}</a>'


def en_cell(it, label):
    en = it.get("en")
    if not en:
        return "—"
    if isinstance(en, str):
        return link(en, label)
    return " / ".join(link(l["url"], l["label"]) for l in en)


def table(sec, ratings):
    label = sec["link_label"]
    rows = []
    for it in sec["items"]:
        cells = [name_cell(it, ratings), en_cell(it, label),
                 link(it["pl"], "Przejdź") if it.get("pl") else "—", esc(it["desc_pl"])]
        if sec["row_style"] == "multiline":
            rows.append("    <tr>\n" + "".join(f"      <td>{c}</td>\n" for c in cells) + "    </tr>")
        else:
            rows.append("    <tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    if sec["row_style"] == "multiline":
        head = "    <tr>\n" + "".join(f"      <th>{esc(h)}</th>\n" for h in sec["headers"]) + "    </tr>"
    else:
        head = "    <tr>" + "".join(f"<th>{esc(h)}</th>" for h in sec["headers"]) + "</tr>"
    return f"<table>\n  <thead>\n{head}\n  </thead>\n  <tbody>\n" + "\n".join(rows) + "\n  </tbody>\n</table>\n"


def list_item(it):
    if "url" in it:
        return f'  <li>{link(it["url"], it["name"])} – {esc(it["desc_en"])}</li>'
    alts = " / ".join(link(l["url"], l["label"]) for l in it["links"])
    return f'  <li>{esc(it["name"])} – {esc(it["desc_en"])} ({alts})</li>'


def badges():
    """Listings under the title: (alt, image, link)."""
    sh = "https://img.shields.io/badge/"
    gh = "https://github.com/eater2/homerenovationfreetools#ai-agents"
    return [
        ("Official MCP Registry", sh + "MCP_Registry-io.github.eater2%2Fhome--renovation--free--tools-0A66C2?logo=modelcontextprotocol&logoColor=white",
         "https://registry.modelcontextprotocol.io/v0/servers?search=io.github.eater2/home-renovation-free-tools"),
        ("npm", "https://img.shields.io/npm/v/home-renovation-free-tools?logo=npm&label=npm&color=CB3837",
         "https://www.npmjs.com/package/home-renovation-free-tools"),
        ("Claude Code plugin", sh + "Claude_Code-plugin-D97757?logo=claude&logoColor=white", gh),
        ("Remote MCP endpoint", sh + "remote_MCP-free%2C_no_API_key-2EA44F?logo=vercel&logoColor=white", gh),
    ]


def readme(d, ratings):
    badge_html = " ".join(f'<a href="{esc(link)}"><img alt="{alt}" src="{esc(img)}"></a>' for alt, img, link in badges())
    out = [f'<p align="right"><a href="{SITE}/">Website</a> · <a href="llms.txt">llms.txt</a> · <a href="catalog.json">catalog.json</a>'
           ' · <a href="AGENTS.md">AGENTS.md</a></p>\n\n'
           f'<h1 align="center">{esc(d["title"])}</h1>\n\n<p align="center">{badge_html}</p>\n\n'
           f'<p align="center">\n  {d["tagline"]}\n</p>\n\n'
           '<p align="center">\n  <a href="https://airenovationcalculator.com/free-tools">🇬🇧 airenovationcalculator.com</a>'
           ' · <a href="https://kalkulatorremontu.pl/darmowe-narzedzia">🇵🇱 kalkulatorremontu.pl</a>\n</p>\n\n\n']
    out.append(ratings_note(ratings))
    for sec in d["sections"]:
        out.append(f'<h2>{esc(sec["title"])}</h2>\n')
        out.append(f'<p>{sec["intro"]}</p>\n\n' if sec.get("intro") else "\n")
        if sec["type"] == "table":
            out.append(table(sec, ratings))
        else:
            for i, g in enumerate(sec["groups"]):
                out.append(("\n" if i else "") + f'<h3>{esc(g["title"])}</h3>\n\n<ul>\n'
                           + "\n".join(list_item(it) for it in g["items"]) + "\n</ul>\n")
        out.append("\n<hr>\n\n" if sec.get("hr_after") else "\n")
    out.append(
        "<h2 id=\"ai-agents\">🤖 Use it from an AI agent</h2>\n\n"
        "<p>The list is also machine-readable, so Claude, ChatGPT, Gemini or any agent can recommend these tools:</p>\n\n"
        "<ul>\n"
        f'  <li><a href="{RAW}/llms.txt">llms.txt</a> – short plain-text index, one line per tool</li>\n'
        f'  <li><a href="{RAW}/catalog.json">catalog.json</a> – every tool with category, links (EN/PL), descriptions and ratings</li>\n'
        "  <li><b>MCP server</b> – tools <code>search_tools</code>, <code>get_tool</code>, <code>list_categories</code>; English or Polish queries; no key needed."
        f"<br>Remote endpoint: <code>{MCP_URL}</code>"
        '<br>Local: <code>{"mcpServers": {"home-renovation-free-tools": {"command": "npx", "args": ["-y", "home-renovation-free-tools"]}}}</code></li>\n'
        "  <li><b>Claude Code plugin with a skill</b> – install it and Claude suggests free calculators, planners and templates when you plan a renovation:"
        "<br><code>/plugin install home-renovation-free-tools --marketplace eater2/homerenovationfreetools</code></li>\n"
        f'  <li><b>claude.ai</b>: upload <a href="{SKILL_ZIP_URL}">the skill ZIP</a> in Settings → Capabilities → Skills</li>\n'
        '  <li>Other agents: copy <a href="plugin/skills/home-renovation-free-tools/SKILL.md">SKILL.md</a> into your skills folder, or point the agent at <a href="AGENTS.md">AGENTS.md</a></li>\n'
        "</ul>\n\n<hr>\n\n"
        "<h2>🙌 Contributing</h2>\n\n"
        "<p>Want to add a tool or improve this list? Contributions are welcome! Please read the "
        '<a href="CONTRIBUTING.md">contribution guidelines</a>, then fork the repo and submit a pull request 🚀</p>\n\n'
        "<hr>\n\n<h2>📄 License</h2>\n\n"
        '<p>This project is licensed under the <a href="LICENSE">MIT License</a>.</p>\n')
    return "".join(out)


# ---------- agent files ----------

def items(d):
    for sec in d["sections"]:
        if sec["type"] == "table":
            for it in sec["items"]:
                yield sec, None, it
        else:
            for g in sec["groups"]:
                for it in g["items"]:
                    yield sec, g, it


def plain_title(t):
    return t.split(" ", 1)[1] if not t[0].isascii() else t


def catalog(d, ratings):
    out = []
    for sec, g, it in items(d):
        e = {"id": it["id"], "name": it["name"], "category": sec["id"],
             "category_name": plain_title(sec["title"])}
        if g:
            e["group"] = plain_title(g["title"])
        e["desc_en"] = it["desc_en"]
        if it.get("desc_pl"):
            e["desc_pl"] = it["desc_pl"]
        en = it.get("en") or it.get("url")
        if isinstance(en, str):
            e["url_en"] = en
        elif en:
            e["links"] = en
        if it.get("links"):
            e["links"] = it["links"]
        if it.get("pl"):
            e["url_pl"] = it["pl"]
        e["maintainer_tool"] = bool(it.get("own"))
        if ratings.get(it["id"]):
            e["ratings"] = ratings[it["id"]]
        out.append(e)
    return out


def rating_text(r):
    parts = []
    for s in r:
        if s.get("rating") and s.get("count"):
            parts.append(f'{s["rating"]:.1f}/5 from {s["count"]} ({s["source"]})')
        elif s.get("stars"):
            parts.append(f'{s["stars"]} GitHub stars')
    return "; ".join(parts)


def llms(d, cat):
    out = [f"# {plain_title(d['title'])}\n",
           "> Curated list of free home renovation calculators, document templates, room planners, contractor directories, "
           "mobile apps and DIY communities, in English and Polish. Free = the core feature works without payment "
           "(a free account is fine).\n",
           f"Full data (JSON): {RAW}/catalog.json",
           f"Agent instructions: {RAW}/AGENTS.md",
           "Fields per line: name | English link | Polish link | what it does | rating (when known). "
           "[own] = maintained by the list owner (airenovationcalculator.com / kalkulatorremontu.pl).\n"]
    for sec in d["sections"]:
        out.append(f"## {plain_title(sec['title'])}\n")
        for e in (e for e in cat if e["category"] == sec["id"]):
            en = e.get("url_en") or " / ".join(f'{l["label"]}: {l["url"]}' for l in e.get("links", []))
            fields = [e["name"] + (" [own]" if e["maintainer_tool"] else ""), en or "-", e.get("url_pl", "-"), e["desc_en"]]
            if e.get("ratings"):
                fields.append(rating_text(e["ratings"]))
            out.append("- " + " | ".join(fields))
        out.append("")
    return "\n".join(out)


# ---------- website (site/, served by Vercel) ----------

SITE_NAME = "Home Renovation Free Tools"
SITE_CSS = """
:root{--bg:#fff;--text:#1e293b;--muted:#64748b;--line:#e2e8f0;--card:#f8fafc;--accent:#2563eb;--accent-2:#1e3a8a}
@media (prefers-color-scheme:dark){:root{--bg:#0f172a;--text:#e2e8f0;--muted:#94a3b8;--line:#1e293b;--card:#111c33;--accent:#60a5fa;--accent-2:#bfdbfe}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
a{color:var(--accent)}header,main,footer{max-width:1100px;margin:0 auto;padding:0 16px}
header{padding-top:32px;display:flex;gap:20px;align-items:center}header img{width:72px;height:72px;flex:none}
h1{margin:0;font-size:clamp(26px,4vw,38px);line-height:1.15;color:var(--accent-2)}.lead{color:var(--muted);max-width:780px}
nav{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0}nav a{border:1px solid var(--line);border-radius:999px;padding:4px 12px;text-decoration:none;font-size:14px}
h2{margin:40px 0 4px;font-size:24px}h3{margin:24px 0 8px;font-size:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;margin-top:12px}
.tool{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.tool h4{margin:0 0 4px;font-size:16px}.tool p{margin:0 0 6px;font-size:14px}.tool .pl{color:var(--muted);font-size:13px}
.links{display:flex;gap:12px;flex-wrap:wrap;font-size:14px;font-weight:600}.rate{font-size:13px;color:var(--muted);margin:2px 0 6px}
ul.res{padding-left:20px}ul.res li{margin:4px 0}footer{margin:48px auto;color:var(--muted);font-size:14px;border-top:1px solid var(--line);padding-top:16px}
code{font-size:13px;word-break:break-all}
"""


def site_rating(r):
    out = []
    for s in r:
        if s.get("rating") and s.get("count", 0) >= MIN_REVIEWS:
            label = "SourceForge" if s["source"] == "sourceforge" else "App Store"
            out.append(f'★ {s["rating"]:.1f}/5 · <a href="{esc(s["url"])}" rel="nofollow">{short_count(s["count"])} {label} '
                       f'{"reviews" if s["source"] == "sourceforge" else "ratings"}</a>')
        elif s.get("stars"):
            out.append(f'★ {short_count(s["stars"])} <a href="{esc(s["url"])}" rel="nofollow">GitHub stars</a>')
    return f'<div class="rate">{" · ".join(out)}</div>' if out else ""


def site_card(it, ratings, label):
    links = []
    en = it.get("en") or it.get("url")
    if isinstance(en, str):
        links.append(f'<a href="{esc(en)}">{"English" if it.get("pl") else label}</a>')
    elif en:
        links += [f'<a href="{esc(l["url"])}">{esc(l["label"])}</a>' for l in en]
    links += [f'<a href="{esc(l["url"])}">{esc(l["label"])}</a>' for l in it.get("links", [])]
    if it.get("pl"):
        links.append(f'<a href="{esc(it["pl"])}" hreflang="pl">Polski</a>')
    pl = f'<p class="pl" lang="pl">{esc(it["desc_pl"])}</p>' if it.get("desc_pl") else ""
    return (f'<article class="tool"><h4>{esc(it["name"])}</h4>{site_rating(ratings.get(it["id"], []))}'
            f'<p>{esc(it["desc_en"])}</p>{pl}<div class="links">{"".join(links)}</div></article>')


def site_html(d, ratings, cat):
    n = len(cat)
    # Google shows about 60 characters of a title and 155 of a description.
    title = f"{SITE_NAME}: {n} Calculators & Room Planners"
    desc = (f"{n} free home renovation tools (EN/PL): paint, tile, flooring and concrete calculators, room planners, "
            "contract templates and contractor directories.")
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "alternateName": "HomeRenovationFreeTools",
           "url": SITE + "/", "inLanguage": ["en", "pl"]},
          {"@context": "https://schema.org", "@type": "Organization", "name": SITE_NAME, "url": SITE + "/",
           "logo": SITE + "/icon.png", "sameAs": ["https://github.com/eater2/homerenovationfreetools",
                                                   "https://airenovationcalculator.com/", "https://kalkulatorremontu.pl/"]},
          {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "url": SITE + "/", "description": desc,
           "mainEntity": {"@type": "ItemList", "numberOfItems": n, "itemListElement": [
               {"@type": "ListItem", "position": i + 1, "name": e["name"], "url": e.get("url_en") or e.get("url_pl") or e["links"][0]["url"]}
               for i, e in enumerate(cat)]}}]
    nav, body = [], []
    for sec in d["sections"]:
        name = plain_title(sec["title"])
        nav.append(f'<a href="#{sec["id"]}">{esc(name)}</a>')
        body.append(f'<section id="{sec["id"]}"><h2>{esc(sec["title"])}</h2>')
        if sec.get("intro"):
            body.append(f'<p class="lead">{sec["intro"]}</p>')
        if sec["type"] == "table":
            body.append('<div class="grid">' + "".join(site_card(it, ratings, sec["link_label"]) for it in sec["items"]) + "</div>")
        else:
            for g in sec["groups"]:
                body.append(f'<h3>{esc(g["title"])}</h3><ul class="res">' + "".join(
                    f'<li>{list_item(it).strip()[4:-5]}</li>' for it in g["items"]) + "</ul>")
        body.append("</section>")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}/">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/icon.png" type="image/png" sizes="512x512">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#2563eb">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE}/">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:image:width" content="1280">
<meta property="og:image:height" content="640">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="text/plain" title="llms.txt" href="{RAW}/llms.txt">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{SITE_CSS}</style>
</head>
<body>
<header><img src="/icon.png" alt="{SITE_NAME} logo" width="72" height="72">
<div><h1>{esc(d["title"])}</h1><p class="lead">{d["tagline"]}</p></div></header>
<main>
<nav>{"".join(nav)}<a href="#ai-agents">For AI agents</a></nav>
{"".join(body)}
<section id="ai-agents"><h2>🤖 Use it from an AI agent</h2>
<p>Machine-readable: <a href="{RAW}/llms.txt">llms.txt</a> · <a href="{RAW}/catalog.json">catalog.json</a>.
MCP server (no key): <code>{MCP_URL}</code> or <code>npx -y home-renovation-free-tools</code>.
Claude Code: <code>/plugin install home-renovation-free-tools --marketplace eater2/homerenovationfreetools</code>.
claude.ai: <a href="/{SKILL}-skill.zip">skill ZIP</a>.</p></section>
</main>
<footer>Maintained by <a href="https://airenovationcalculator.com/">airenovationcalculator.com</a> · <a href="https://kalkulatorremontu.pl/" hreflang="pl">kalkulatorremontu.pl</a>.
Add a tool on <a href="https://github.com/eater2/homerenovationfreetools">GitHub</a>. Ratings are public user ratings with their source; MIT licence.</footer>
</body>
</html>
"""


def write_site(d, ratings, cat):
    (ROOT / "site" / "index.html").write_text(site_html(d, ratings, cat), encoding="utf-8", newline="\n")
    (ROOT / "site" / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8", newline="\n")
    lastmod = max([s["fetched_at"][:10] for r in ratings.values() for s in r] or ["2026-10-19"])
    (ROOT / "site" / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{SITE}/</loc><lastmod>{lastmod}</lastmod></url>\n</urlset>\n", encoding="utf-8", newline="\n")


def skill_zip():
    """Skill ZIP for claude.ai, byte-identical on every OS: LF text, stored (no compression), fixed timestamp."""
    md = (ROOT / "plugin" / "skills" / SKILL / "SKILL.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    info = zipfile.ZipInfo(f"{SKILL}/SKILL.md", date_time=(2026, 1, 1, 0, 0, 0))
    info.create_system = 3  # "Unix", so Windows and Linux write the same header
    info.external_attr = 0o644 << 16
    with zipfile.ZipFile(ROOT / "site" / f"{SKILL}-skill.zip", "w", zipfile.ZIP_STORED) as z:
        z.writestr(info, md.encode("utf-8"))


def check_versions():
    """One version in package.json, server.json, the plugin manifests and the MCP server code."""
    def j(p):
        return json.loads((ROOT / p).read_text(encoding="utf-8"))
    server = j("server.json")
    core = re.search(r'VERSION = "([^"]+)"', (ROOT / "mcp" / "core.mjs").read_text(encoding="utf-8")).group(1)
    versions = {"package.json": j("package.json")["version"], "server.json": server["version"],
                "server.json packages": server["packages"][0]["version"],
                "plugin.json": j("plugin/.claude-plugin/plugin.json")["version"],
                "marketplace.json": j(".claude-plugin/marketplace.json")["plugins"][0]["version"], "mcp/core.mjs": core}
    assert len(set(versions.values())) == 1, f"versions differ: {versions}"
    assert j("package.json")["mcpName"] == server["name"], "package.json mcpName must equal server.json name"


def write(name, text):
    (ROOT / name).write_text(text, encoding="utf-8", newline="\n")


def main():
    d = load("tools.json", None)
    ratings = load("ratings.json", {}).get("tools", {})
    ids = [it["id"] for _, _, it in items(d)]
    dup = {i for i in ids if ids.count(i) > 1}
    assert not dup, f"duplicate ids: {dup}"
    missing = [it["id"] for _, _, it in items(d) if not it.get("desc_en")]
    assert not missing, f"desc_en missing: {missing}"
    cat = catalog(d, ratings)
    write("README.md", readme(d, ratings))
    write("catalog.json", json.dumps(cat, ensure_ascii=False, indent=2) + "\n")
    write("llms.txt", llms(d, cat))
    write_site(d, ratings, cat)
    skill_zip()
    check_versions()
    print(f"{len(cat)} tools, {sum(1 for e in cat if e.get('ratings'))} with ratings")


if __name__ == "__main__":
    main()
