// Remote MCP endpoint (Streamable HTTP, stateless) on Vercel: https://<deployment>/mcp
// Same tools as the stdio server; see mcp/core.mjs.
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { createServer, load } from "../mcp/core.mjs";

// Refresh the catalog at most every 10 minutes per warm instance.
const TTL_MS = 10 * 60 * 1000;
let loadedAt = 0;
let loading = null;

async function ensureLoaded() {
  if (Date.now() - loadedAt < TTL_MS) return;
  loading ??= load().then(() => { loadedAt = Date.now(); }).finally(() => { loading = null; });
  await loading;
}

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Mcp-Session-Id, Mcp-Protocol-Version");
  res.setHeader("Access-Control-Expose-Headers", "Mcp-Session-Id");
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") {
    // Stateless server: no GET stream or session to delete.
    return res.status(405).setHeader("Allow", "POST, OPTIONS").json({
      jsonrpc: "2.0", error: { code: -32000, message: "Method not allowed. POST MCP JSON-RPC messages to this URL." }, id: null,
    });
  }

  // One log line per call for usage stats (Vercel runtime logs). Tool name and category only, never the query text.
  for (const msg of [].concat(req.body || [])) {
    if (msg?.method) {
      console.log(JSON.stringify({ evt: "mcp", method: msg.method, tool: msg.params?.name, category: msg.params?.arguments?.category }));
    }
  }

  await ensureLoaded();
  const server = createServer();
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true });
  res.on("close", () => { transport.close(); server.close(); });
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
}
