# MCP servers

Part of [ART: Agentic Research Toolkit](../README.md).

| Server | When to use it | Setup |
| --- | --- | --- |
| Playwright | Open and interact with pages when ordinary fetching does not work. | Install Node.js 20+ with npx and Microsoft Edge. The pinned server launches Edge headlessly with an isolated profile. |
| arXiv | Find papers and check metadata or available full text before writing a research note. | The community-hosted HTTP endpoint at `https://arxiv.caseyjhand.com/mcp` requires network access. |
| Firecrawl | Search the wider web for sources, scrape a known public URL, or parse a document. Prefer arXiv for paper metadata and Playwright for pages that need interaction. | Hosted HTTP server. Search, Scrape and Parse work without an account or API key, within daily limits. [Keyless access](https://docs.firecrawl.dev/mcp-server/keyless) |

To opt in, add `"firecrawl"` to your profile's `mcp` list or run `python install.py --client codex --project . --server firecrawl`. The example profile keeps its existing two-server selection.

For a machine with Chrome instead of Edge, change the Playwright browser argument from `msedge` to `chrome` in the installed configuration. [Playwright MCP documentation](https://github.com/microsoft/playwright-mcp)

## Who sees your data

Each server and service below receives part of what agents send. Hosted endpoints cannot be pinned by this checkout: the operator can change the server, its tools or its limits at any time. Whatever a tool returns also goes to the model provider your client is configured with (Claude Code or Codex), as part of the conversation. Keep confidential or unpublished material out of hosted services unless you are allowed to share it.

| Service | Operator and where it runs | What reaches the operator | Pinned by this checkout |
| --- | --- | --- | --- |
| arXiv | The community [cyanheads/arxiv-mcp-server](https://github.com/cyanheads/arxiv-mcp-server) project's public endpoint, not arXiv itself. Hosted. | Search queries and requested paper IDs. The server then fetches from arXiv. | No. The project publishes versioned npm releases (`@cyanheads/arxiv-mcp-server`) if you prefer to run a fixed version locally; ART does not configure that. |
| Firecrawl | Firecrawl, a hosted company service. | Search queries, requested URLs, and any document content sent for parsing. Keyless use is rate-limited. | No. The official `firecrawl-mcp` package runs locally but still calls the Firecrawl API, or a self-hosted Firecrawl through `FIRECRAWL_API_URL`. |
| Playwright | Microsoft's open-source server, run locally through npx. | No server operator. The browser contacts every site it visits, and npx downloads the package from the npm registry. `--isolated` keeps the browser profile in memory; it is not a security boundary ([upstream notes](https://github.com/microsoft/playwright-mcp/blob/v0.0.84/README.md#security)). | Yes, `@playwright/mcp@0.0.84`. |
| Zotero (optional) | `zotero-mcp-server`, run locally against your Zotero desktop app. | Zotero reads are local, but the items, notes and full text they return are processed by your client's model provider, so that content can leave your machine. Adding papers through the Zotero web API sends the new item and your key to zotero.org. | Yes, the pip version in [Skills](skills.md). |
| Semantic Scholar (optional) | The Allen Institute for AI. Called directly over HTTP by the rules, not through an MCP server. | Search queries, paper IDs and your API key. | No, hosted API. |
| OpenRouter (optional) | OpenRouter, a hosted company service, used only when you ask `nature-figure` for an AI-drawn schematic draft. | The image prompt, which can describe unpublished work, any reference images (local files are sent as image bytes, and image URLs as given), and your API key. | No, hosted API. |
