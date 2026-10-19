#!/usr/bin/env node
// MCP server for Home Renovation Free Tools over stdio (npx -y home-renovation-free-tools).
// Tools live in core.mjs, shared with the HTTP endpoint in api/mcp.mjs.
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createServer, load } from "./core.mjs";

await load();
await createServer().connect(new StdioServerTransport());
