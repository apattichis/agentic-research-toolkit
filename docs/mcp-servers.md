# MCP servers

Part of [ART: Agentic Research Toolkit](../README.md).

| Server | When to use it | Setup |
| --- | --- | --- |
| Playwright | Open and interact with pages when ordinary fetching does not work. | Install Node.js 20+ with npx and Microsoft Edge. The pinned server launches Edge headlessly with an isolated profile. |
| arXiv | Find papers and check metadata or available full text before writing a research note. | The community-hosted HTTP endpoint at `https://arxiv.caseyjhand.com/mcp` requires network access. |
| Firecrawl | Search the wider web for sources, scrape a known public URL, or parse a document. Prefer arXiv for paper metadata and Playwright for pages that need interaction. | Hosted HTTP server. Search, Scrape and Parse work without an account or API key, within daily limits. [Keyless access](https://docs.firecrawl.dev/mcp-server/keyless) |

To opt in, add `"firecrawl"` to your profile's `mcp` list or run `python install.py --client codex --project . --server firecrawl`. The example profile keeps its existing two-server selection.

For a machine with Chrome instead of Edge, change the Playwright browser argument from `msedge` to `chrome` in the installed configuration. [Playwright MCP documentation](https://github.com/microsoft/playwright-mcp)
