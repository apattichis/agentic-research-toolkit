# Changelog

ART follows [semantic versioning](https://semver.org/). While it is early, versions stay at 0.x: a new minor version (0.2.0) adds skills or features, and a patch version (0.1.1) fixes them. Releases will be tagged on GitHub as `vX.Y.Z`. `python install.py --version` prints the version of the toolkit checkout.

## 0.1.0 (planned first release)

- 18 skills for Claude Code, Codex and Cursor: a coordinator (`parent`, `router`), eight core research roles, and specialists for ideas, Zotero, figures, diagrams, reports and slides, finding skills, and commits.
- 3 MCP servers in the catalogue: arXiv, Firecrawl and Playwright.
- An optional project rulebook (`--rules`): coordinator workflow, workers and critics on both Claude Code and Codex, budget and load limits (model choice, heavy work one at a time, usage limits), figure checks, the research-idea routine, and Zotero and Semantic Scholar rules.
- An installer that copies skills, server settings and rules, adds required companion skills automatically, stops instead of overwriting existing changes, and reports its version with `--version`.
- Setup notes for the Zotero MCP server, including manual deny lists that block selected tools which delete or edit existing items in both clients. The rules forbid removing collection memberships and other destructive actions; adding papers and collection memberships stays allowed.
- A README overview with figures and the crew, and guides for installation, skills, MCP servers and workflows.
- The nature-figure skill ships without its upstream figures4papers reference examples (CC BY-NC 4.0); a note in their folder says where to get them.
- The project rules keep portable policy for handoffs between Claude Code and Codex (least permissions first, check what the environment allows, deadlines and failure handling) and move the tested commands into a Client recipes part with PowerShell and Bash examples.
- The MCP servers guide shows who operates each server and service, what data reaches them, and which ones this checkout can pin.
- The guides no longer quote trial scores; they note only that small internal trials informed the design, and the rules present trial findings as preliminary observations.
- The project rules require a backup and a diff of local edits before an installed skill folder is deleted for an update, and the client recipes create `.agent-runs/` first, set the Codex model and effort, and add a Claude research-review variant with read-only arXiv access.
- The README leads with what sets ART apart and names companion projects that work well with it.
