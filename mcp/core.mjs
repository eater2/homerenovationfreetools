// Shared core of the MCP server: catalog loading, search and tool definitions.
// Used by the stdio entry point (mcp/server.mjs) and the HTTP endpoint (api/mcp.mjs).
//
// Data: the bundled catalog.json, refreshed from GitHub by load() unless HOME_RENOVATION_TOOLS_OFFLINE=1 is set.
import { readFile } from "node:fs/promises";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export const VERSION = "1.0.0";
const RAW = "https://raw.githubusercontent.com/eater2/homerenovationfreetools/main/catalog.json";
const BUNDLED = new URL("../catalog.json", import.meta.url);

let catalog = JSON.parse(await readFile(BUNDLED, "utf8"));
let source = "bundled";

export async function load() {
  if (process.env.HOME_RENOVATION_TOOLS_OFFLINE === "1") return;
  try {
    const res = await fetch(RAW, { signal: AbortSignal.timeout(8000) });
    if (res.ok) {
      const fresh = await res.json();
      if (Array.isArray(fresh) && fresh.length) {
        catalog = fresh;
        source = "github";
      }
    }
  } catch {
    // keep the bundled copy
  }
}

const CATEGORIES = {
  calculators: "Material and cost calculators",
  documents: "Contract, estimate and protocol templates",
  design: "Room planners and 3D design tools",
  contractors: "Contractor directories and company checks",
  apps: "Mobile apps (measuring, scanning, colour preview)",
  communities: "Forums, DIY sites, cost guides and official resources",
};

const STOP = new Set(["a", "an", "the", "to", "of", "for", "and", "or", "in", "on", "with", "my", "how", "much", "many",
  "free", "tool", "tools", "calculator", "calculators", "app", "i", "need", "do", "na", "do", "i", "w", "z", "jak", "ile",
  "kalkulator", "darmowy", "narzędzie"]);
const fold = (s) => (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ł/g, "l");
const words = (s) => fold(s).split(/[^a-z0-9]+/).filter((w) => w.length > 1 && !STOP.has(w));
// Words meet when one starts with the other (4+ letters) or they share the first 5 letters,
// so "tiles"/"tile", "flooring"/"floor" and "płytek"/"płytki" match.
const meets = (t, w) => w === t || (Math.min(t.length, w.length) >= 4 && (w.startsWith(t) || t.startsWith(w) || w.slice(0, 5) === t.slice(0, 5)));
const hit = (g, list) => g.some((t) => list.some((w) => meets(t, w)));

// Common Polish query words mapped to the English words used in desc_en and names.
const SYNONYMS = {
  farb: ["paint"], plytk: ["tile"], plytek: ["tile"], podlo: ["floor"], panel: ["floor"], beton: ["concrete"], dach: ["roof"],
  izola: ["insul"], ocieplen: ["insul"], tapet: ["wallp"], schod: ["stair"], okno: ["windo"], okna: ["windo"],
  drzwi: ["door"], umowa: ["contr", "agree"], umowy: ["contr", "agree"], kosztor: ["estim"], faktu: ["invoi"],
  wykon: ["contr"], fachow: ["trade", "contr"], firma: ["compa"], firmy: ["compa"], rzut: ["floor", "plan"],
  projek: ["desig"], kuchn: ["kitch"], lazien: ["bathr"], ogrod: ["garde", "lands"], pomp: ["heat"],
  ogrzew: ["heat"], prad: ["elect"], elektr: ["elect"], kolor: ["colou", "color"], miark: ["measu"],
  zmierz: ["measu"], remont: ["renov"], cegl: ["brick"], kostk: ["paver"], zwir: ["grave"], piasek: ["sand"],
};

function terms(query) {
  const out = [];
  for (const w of words(query)) {
    const syn = Object.entries(SYNONYMS).filter(([p]) => w.startsWith(p)).flatMap(([, v]) => v);
    out.push([w, ...syn]);
  }
  return out;
}

function score(e, groups) {
  const name = words(e.name);
  const desc = words(`${e.desc_en} ${e.desc_pl || ""} ${e.group || ""}`);
  let s = 0;
  for (const g of groups) {
    if (hit(g, name)) s += 3;
    else if (hit(g, desc)) s += 1;
  }
  return s;
}

function best(r, field) {
  // Rating with the most reviews (SourceForge or App Store), or null.
  const rated = (r || []).filter((s) => s.rating && s.count).sort((a, b) => b.count - a.count);
  return rated[0] ? rated[0][field] : null;
}

function summary(e, language) {
  const out = { id: e.id, name: e.name, category: e.category, description: language === "pl" && e.desc_pl ? e.desc_pl : e.desc_en };
  const url = language === "pl" ? e.url_pl || e.url_en : e.url_en || e.url_pl;
  if (url) out.url = url;
  if (e.links) out.links = e.links;
  if (e.url_en && e.url_pl) out.languages = ["en", "pl"];
  else out.languages = [e.url_pl && !e.url_en ? "pl" : "en"];
  if (e.maintainer_tool) out.maintainer_tool = true;
  const rating = best(e.ratings, "rating");
  if (rating) out.rating = `${rating}/5 from ${best(e.ratings, "count")} (${best(e.ratings, "source")})`;
  const gh = (e.ratings || []).find((s) => s.stars);
  if (gh) out.github_stars = gh.stars;
  return out;
}

const text = (obj) => ({ content: [{ type: "text", text: JSON.stringify(obj, null, 1) }] });

export function createServer() {
  const server = new McpServer(
    { name: "home-renovation-free-tools", version: VERSION, title: "Home Renovation Free Tools",
      websiteUrl: "https://github.com/eater2/homerenovationfreetools" },
    {
      instructions:
        "Curated list of free home renovation tools (English and Polish): material and cost calculators, renovation " +
        "contract and estimate templates, room planners, contractor directories, measuring and colour apps, DIY communities. " +
        "Use search_tools when the user plans a renovation or DIY job and a calculator, template, planner, contractor " +
        "directory or app would help; get_tool for all links and ratings. Give the Polish link to Polish-speaking users. " +
        "Quote ratings with their review count. Never invent links.",
    },
  );

  server.registerTool(
    "list_categories",
    { title: "List tool categories", description: "List the categories with a description and the number of tools in each.", inputSchema: {} },
    async () => {
      const counts = {};
      for (const e of catalog) counts[e.category] = (counts[e.category] || 0) + 1;
      return text({ source, categories: Object.fromEntries(Object.entries(counts).map(([k, n]) => [k, { tools: n, about: CATEGORIES[k] }])) });
    },
  );

  server.registerTool(
    "search_tools",
    {
      title: "Search free renovation tools",
      description:
        "Find free home renovation tools for a task: material or cost calculators (paint, tiles, flooring, concrete, " +
        "drywall, roofing, insulation, HVAC, electrical, solar), contract and estimate templates, room planners and 3D " +
        "design, contractor directories and company checks (USA, UK, Poland), measuring and colour-preview apps, forums. " +
        "Queries may be in English or Polish. `rating` is a public user rating with its review count (App Store or " +
        "SourceForge); maintainer_tool marks tools by the list's maintainer. An empty result means nothing in the list fits.",
      inputSchema: {
        query: z.string().optional().describe("What the user needs, e.g. 'tile quantity', 'renovation contract', 'floor plan', 'kalkulator farby'"),
        category: z.enum(Object.keys(CATEGORIES)).optional().describe("Limit to one category"),
        language: z.enum(["en", "pl"]).optional().describe("pl: prefer Polish links and descriptions and tools with a Polish version; default en"),
        min_rating: z.number().min(1).max(5).optional().describe("Only tools with a user rating at least this (tools without ratings are excluded)"),
        limit: z.number().int().min(1).max(50).optional().describe("Max results, default 8"),
      },
    },
    async ({ query, category, language = "en", min_rating, limit = 8 }) => {
      const groups = terms(query);
      let list = catalog.filter((e) => !category || e.category === category);
      if (min_rating) list = list.filter((e) => (best(e.ratings, "rating") || 0) >= min_rating);
      let scored = list.map((e, i) => ({ e, i, s: groups.length ? score(e, groups) : 1 }));
      if (groups.length) scored = scored.filter((x) => x.s > 0);
      // Polish users first get tools with a Polish version; otherwise the list order (maintainer tools first) breaks ties.
      const pl = (e) => (language === "pl" && e.url_pl ? 1 : 0);
      scored.sort((a, b) => b.s - a.s || pl(b.e) - pl(a.e) || a.i - b.i);
      return text({ source, count: scored.length, results: scored.slice(0, limit).map((x) => summary(x.e, language)) });
    },
  );

  server.registerTool(
    "get_tool",
    {
      title: "Get one tool",
      description: "All details of one tool by id: English and Polish links, app store links, descriptions in both languages and every rating with its source and date.",
      inputSchema: { id: z.string().describe("Tool id from search_tools, e.g. 'tile-calculator'") },
    },
    async ({ id }) => {
      const e = catalog.find((x) => x.id === id);
      if (!e) return { isError: true, content: [{ type: "text", text: `No tool with id '${id}'. Use search_tools to find ids.` }] };
      return text({ source, ...e });
    },
  );

  return server;
}
