"""Fetch public user opinions (ratings and review counts) for the tools named in data/rating-ids.json.

Sources (only ones that allow automated access):
  sourceforge  rating and review count from sourceforge.net/software/product/<slug>/ (allowed by robots.txt);
               the page must link the tool's own domain
  appstore     rating and rating count of the vendor's iOS app (Apple iTunes Lookup API)
  github       stars of an open-source tool's repo (REST API; GITHUB_TOKEN raises the rate limit)

Google Play has no public API and its terms forbid automated access; G2, Capterra and Trustpilot block
automated clients. They are not fetched.

Writes data/ratings.json. A source that fails keeps its previous value. Then run python scripts/build.py.
Usage: python scripts/fetch_ratings.py [--only id,id]
"""
import argparse
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
UA = "Mozilla/5.0 homerenovationfreetools/1.0 (+https://github.com/eater2/homerenovationfreetools)"
SF_DELAY = 1.5  # seconds between SourceForge requests


def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def base_domain(url):
    host = urllib.parse.urlparse(url).netloc.lower()
    parts = host.split(".")
    return ".".join(parts[-3:] if len(parts) > 2 and len(parts[-2]) <= 3 else parts[-2:])


def tool_urls(it):
    en = it.get("en") or it.get("url") or []
    urls = [en] if isinstance(en, str) else [l["url"] for l in en]
    return urls + [l["url"] for l in it.get("links", [])] + ([it["pl"]] if it.get("pl") else [])


def sourceforge(url, it):
    time.sleep(SF_DELAY)
    page = get(url)
    domains = {base_domain(u) for u in tool_urls(it)} - {"apple.com", "google.com"}
    if not any(d in page for d in domains):  # page must reference the tool's own domain
        raise ValueError(f"{url} does not link {domains}")
    rating = re.search(r'itemprop="ratingValue">([\d.]+)<', page)
    count = (re.search(r'itemprop="reviewCount" content="(\d+)"', page)
             or re.search(r"\((\d[\d,]*) Reviews? &(?:amp;)? Ratings\)", page))
    return {"source": "sourceforge", "rating": float(rating.group(1)) if rating else None,
            "count": int(count.group(1).replace(",", "")) if count else 0, "url": url}


def appstore(app_id, country):
    r = json.loads(get(f"https://itunes.apple.com/lookup?id={app_id}&country={country}"))["results"]
    if not r:
        raise ValueError(f"app {app_id} not in the {country} store")
    a = r[0]
    return {"source": "appstore", "app": a["trackName"], "rating": round(a.get("averageUserRating", 0), 2),
            "count": a.get("userRatingCount", 0), "price": a.get("formattedPrice"), "country": country,
            "url": f"https://apps.apple.com/{country}/app/id{app_id}"}


def github(repo):
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    r = json.loads(get(f"https://api.github.com/repos/{repo}", headers))
    return {"source": "github", "repo": r["full_name"], "stars": r["stargazers_count"],
            "pushed_at": r["pushed_at"][:10], "url": r["html_url"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated tool ids")
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}

    tools = {}
    for sec in json.loads((DATA / "tools.json").read_text(encoding="utf-8"))["sections"]:
        for it in sec.get("items", []) + [i for g in sec.get("groups", []) for i in g["items"]]:
            tools[it["id"]] = it
    ids = {k: v for k, v in json.loads((DATA / "rating-ids.json").read_text(encoding="utf-8")).items() if not k.startswith("_")}
    unknown = set(ids) - set(tools)
    assert not unknown, f"rating-ids.json names unknown tools: {unknown}"

    path = DATA / "ratings.json"
    old = json.loads(path.read_text(encoding="utf-8"))["tools"] if path.exists() else {}
    out = {k: v for k, v in old.items() if k in ids}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    failed = 0
    for tid, src in ids.items():
        if only and tid not in only:
            continue
        prev = {s["source"]: s for s in old.get(tid, [])}
        results = []
        for name, arg in src.items():
            try:
                if name == "sourceforge":
                    res = sourceforge(arg, tools[tid])
                elif name == "appstore":
                    res = appstore(*arg)
                else:
                    res = github(arg)
                res["fetched_at"] = now
            except (urllib.error.URLError, ValueError, KeyError, TimeoutError) as e:
                print(f"{tid} {name}: {e}")
                failed += 1
                res = prev.get(name)
            if res:
                results.append(res)
        out[tid] = results
        print(tid, "; ".join(f'{r["source"]} {r.get("rating") or r.get("stars")} ({r.get("count", "")})' for r in results), flush=True)
    path.write_text(json.dumps({"tools": dict(sorted(out.items()))}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
    print(f"{len(out)} tools with sources, {failed} failed lookups")


if __name__ == "__main__":
    main()
