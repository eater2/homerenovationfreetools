// Smoke test: start the server over stdio and call every tool.
import assert from "node:assert/strict";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({
  command: process.execPath,
  args: [new URL("./server.mjs", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")],
  env: { ...process.env, HOME_RENOVATION_TOOLS_OFFLINE: "1" },
});
const client = new Client({ name: "smoke-test", version: "1.0.0" });
await client.connect(transport);

const listed = (await client.listTools()).tools;
const tools = listed.map((t) => t.name).sort();
assert.deepEqual(tools, ["get_tool", "list_categories", "search_tools"]);
assert.ok(listed.every((t) => t.annotations?.title && t.annotations.readOnlyHint === true && t.annotations.destructiveHint === false));

const call = async (name, args = {}) => JSON.parse((await client.callTool({ name, arguments: args })).content[0].text);

const cats = await call("list_categories");
assert.deepEqual(Object.keys(cats.categories).sort(), ["apps", "calculators", "communities", "contractors", "design", "documents"]);

const tiles = await call("search_tools", { query: "how many tiles for a bathroom floor" });
assert.equal(tiles.results[0].id, "tile-calculator", JSON.stringify(tiles.results.map((r) => r.id)));
console.log("tiles:", tiles.results.map((r) => r.name).join(", "));

const farba = await call("search_tools", { query: "kalkulator farby", language: "pl" });
assert.equal(farba.results[0].id, "paint-calculator");
assert.match(farba.results[0].url, /kalkulatorremontu\.pl/);
console.log("farba (pl):", farba.results.map((r) => `${r.name} ${r.url}`).join(", "));

const plytki = await call("search_tools", { query: "ile płytek na łazienkę", language: "pl" });
assert.equal(plytki.results[0].id, "tile-calculator", JSON.stringify(plytki.results.map((r) => r.id)));

const umowa = await call("search_tools", { query: "umowa z wykonawcą", language: "pl" });
assert.ok(umowa.results.some((r) => r.category === "documents"), JSON.stringify(umowa.results));

const plan = await call("search_tools", { query: "floor plan", category: "design" });
assert.ok(plan.results.length && plan.results.every((r) => r.category === "design"));

const rated = await call("search_tools", { category: "apps", min_rating: 4.5, limit: 50 });
assert.ok(rated.results.length && rated.results.every((r) => Number(r.rating.split("/")[0]) >= 4.5));
console.log("apps rated 4.5+:", rated.results.map((r) => `${r.name} (${r.rating})`).join(", "));

assert.equal((await call("search_tools", { query: "xyzzy qwrtpk" })).count, 0);

const one = await call("get_tool", { id: "thumbtack" });
assert.equal(one.name, "Thumbtack");
assert.ok(one.ratings.length);
const missing = await client.callTool({ name: "get_tool", arguments: { id: "nope" } });
assert.equal(missing.isError, true);

await client.close();
console.log("MCP smoke test passed");
