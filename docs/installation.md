# Installation

Part of [ART: Agentic Research Toolkit](../README.md).

## Set up by asking your assistant

Open the target project in Codex or Claude Code and paste the request below into a session. The assistant can run the installer for you.

> Set up https://github.com/apattichis/agentic-research-toolkit in this project for the client I'm using. Install the research-team profile plus arXiv, Firecrawl and Playwright. Preview the changes first, preserve existing settings, and tell me which tools you verified. Use project scope.

After setup, ask the coordinator to delegate the task. If you want Claude teammates to communicate directly, explicitly ask for a native agent team and a peer cross-check. Sign in through the client's browser flow if prompted.

## Start a project

Use **Use this template** on GitHub to create a repository with the catalogue and installer. For an existing project, clone the toolkit separately with `git -c core.longpaths=true clone https://github.com/apattichis/agentic-research-toolkit`.

Copy [toolkit.example.json](../toolkit.example.json) to `toolkit.json` in your project. Edit its two lists to select the skills and servers you want. An empty list skips that category. The string `"*"` selects everything in a category. Commit the selection file to reuse it across clients.

From the toolkit folder, run the installer with Python 3.11 or later. Use an existing project path, or `.` when working inside a project created from this template. For an existing project, give the profile's full path too, for example `--project "/path/to/project" --profile "/path/to/project/toolkit.json"`, because the installer reads the profile from the folder you run it in.

```sh
python install.py --list
python install.py --client codex --project . --profile toolkit.json --dry-run
python install.py --client codex --project . --profile toolkit.json
```

Replace `codex` with `claude` or `cursor` for another client. For a one-off install, choose individual items or the full set.

```sh
python install.py --client claude --project . --skill scout --server arxiv
python install.py --client cursor --project . --all
```

To also give the project the shared agent rules, add `--rules`, or `"rules": true` to the profile. The installer then copies [templates/AGENTS.md](../templates/AGENTS.md), and for Claude Code also [templates/CLAUDE.md](../templates/CLAUDE.md), which points to it. The rules cover the coordinator workflow, workers and critics on both Claude Code and Codex, budget and load limits, the skill for each need, Zotero and Semantic Scholar use, figure checks and the research-idea routine. Fill in the Project section of the copied `AGENTS.md`: the project's name, its GitHub repository and its Zotero collection.

```sh
python install.py --client claude --project . --profile toolkit.json --rules
python install.py --client codex --project . --profile toolkit.json --rules
```

The installer copies complete skill folders, merges selected MCP entries into project settings, and leaves matching installations alone. If a selected name has different contents or settings, it stops so you can review the conflict. Removing an item from the profile does not uninstall it.

## Client discovery and verification

| Client | Project skill folder | Project MCP configuration |
| --- | --- | --- |
| Codex | `.agents/skills/` | `.codex/config.toml` |
| Claude Code | `.claude/skills/` | `.mcp.json` |
| Cursor | `.cursor/skills/` | `.cursor/mcp.json` |

Start a new session in the target project. Trust the project and approve its servers if prompted. Check `/mcp` in Codex or Claude Code, or Cursor's MCP settings. To verify actual tool use, ask Playwright to open `https://example.com` and report the page title. Ask arXiv to retrieve metadata for `1706.03762` and report the title. For Firecrawl, ask it to scrape `https://example.com` and return the page title from its metadata (`Example Domain`).

Other assistants can read an individual skill folder directly. MCP-capable clients can use the same HTTP URL or launch command in [servers.json](../mcp/servers.json) with their own settings format.
