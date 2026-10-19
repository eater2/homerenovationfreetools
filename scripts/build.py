"""Generate README.md, catalog.json and llms.txt from data/tools.json and data/ratings.json.

Edit the data files, then run: python scripts/build.py
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = "https://raw.githubusercontent.com/eater2/homerenovationfreetools/main"
MIN_REVIEWS = 3


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


def readme(d, ratings):
    out = [f'<h1 align="center">{esc(d["title"])}</h1>\n\n<p align="center">\n  {d["tagline"]}\n</p>\n\n'
           '<p align="center">\n  <a href="https://airenovationcalculator.com/free-tools">🇬🇧 airenovationcalculator.com</a>'
           ' · <a href="https://kalkulatorremontu.pl/darmowe-narzedzia">🇵🇱 kalkulatorremontu.pl</a>\n</p>\n\n'
           '<p align="center">\n  <sub>🤖 For AI agents: <a href="llms.txt">llms.txt</a> · <a href="catalog.json">catalog.json</a>'
           ' · <a href="#ai-agents">Claude skill</a></sub>\n</p>\n\n\n']
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
        "  <li><b>Claude Code plugin with a skill</b> – install it and Claude suggests free calculators, planners and templates when you plan a renovation:"
        "<br><code>/plugin install home-renovation-free-tools --marketplace eater2/homerenovationfreetools</code></li>\n"
        '  <li>Other agents: copy <a href="skills/home-renovation-free-tools/SKILL.md">SKILL.md</a> into your skills folder, or point the agent at <a href="AGENTS.md">AGENTS.md</a></li>\n'
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
    print(f"{len(cat)} tools, {sum(1 for e in cat if e.get('ratings'))} with ratings")


if __name__ == "__main__":
    main()
