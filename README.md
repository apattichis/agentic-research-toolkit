# ART: Agentic Research Toolkit

A project template for giving AI assistants the skills and tools a project needs. Skills describe how to do a task. MCP servers give an assistant access to a browser, academic papers, or web search and extraction.

## Set up by asking your assistant

Open the target project in Codex or Claude Code and paste the request below into a session. The assistant can run the installer for you.

> Set up https://github.com/apattichis/agentic-research-toolkit in this project for the client I'm using. Install the research-team profile plus arXiv, Firecrawl and Playwright. Preview the changes first, preserve existing settings, and tell me which tools you verified. Use project scope.

After setup, ask the coordinator to delegate the task. If you want Claude teammates to communicate directly, explicitly ask for a native agent team and a peer cross-check. Sign in through the client's browser flow if prompted.

## Start a project

Use **Use this template** on GitHub to create a repository with the catalogue and installer. For an existing project, clone the toolkit separately with `git -c core.longpaths=true clone https://github.com/apattichis/agentic-research-toolkit`.

Copy [toolkit.example.json](toolkit.example.json) to `toolkit.json` in your project. Edit its two lists to select the skills and servers you want. An empty list skips that category. The string `"*"` selects everything in a category. Commit the selection file to reuse it across clients.

From the toolkit folder, run the installer with Python 3.11 or later. Use an existing project path, or `.` when working inside a project created from this template.

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

To also give the project the shared agent rules, add `--rules`, or `"rules": true` to the profile. The installer then copies [templates/AGENTS.md](templates/AGENTS.md), and for Claude Code also [templates/CLAUDE.md](templates/CLAUDE.md), which points to it. The rules cover the coordinator workflow, workers and critics on both Claude Code and Codex, the skill for each need, Zotero and Semantic Scholar use, figure checks and the research-idea routine. Fill in the Project section of the copied `AGENTS.md`: the project's name, its GitHub repository and its Zotero collection.

```sh
python install.py --client claude --project . --profile toolkit.json --rules
python install.py --client codex --project . --profile toolkit.json --rules
```

The installer copies complete skill folders, merges selected MCP entries into project settings, and leaves matching installations alone. If a selected name has different contents or settings, it stops so you can review the conflict. Removing an item from the profile does not uninstall it.

## Skills

| Category | Available skills |
| --- | --- |
| [Writing](skills/writing) | [Quarto authoring](skills/writing/quarto-authoring/SKILL.md) |
| [Research](skills/research) | Parent, router, scout, cartographer, claims, critic, synthesizer, experimenter, archivist, dynamics analyst, [Research ideation](skills/research/research-ideation/SKILL.md), [Zotero library](skills/research/zotero-library/SKILL.md) |
| [Visuals](skills/visuals) | [Nature figure](skills/visuals/nature-figure/SKILL.md) with [Nature shared](skills/visuals/nature-shared/SKILL.md), [Diagram design](skills/visuals/diagram-design/SKILL.md) |
| [Development](skills/development) | [Git commit](skills/development/git-commit/SKILL.md), [Find skills](skills/development/find-skills/SKILL.md) |

The research roles are standalone adaptations of the author's earlier research skills.

The Git commit skill comes from [GitHub's Awesome Copilot collection](https://github.com/github/awesome-copilot/blob/8178d1939a203f691067073dcab2a3f1e14072d3/skills/git-commit/SKILL.md), with its MIT license included. It follows the repository's commit rules, defaults to Conventional Commits and verifies the result. The toolkit adaptation preserves unrelated staged work when committing selected files.

Find skills comes unchanged from [Vercel Labs' skills repository](https://github.com/vercel-labs/skills/blob/7a5e920bead4b1039a6d6df5d7e1163b7b09423a/skills/find-skills/SKILL.md), with its MIT license included. It searches the open skills ecosystem at [skills.sh](https://skills.sh/) through the `npx skills` CLI. Its final step installs globally without confirmation (`npx skills add <package> -g -y`). In a project, present the candidates with source, install count and stars, install only after the user agrees, and put the skill in the project's skill folders.

The visual and report skills come unchanged from upstream at pinned revisions, each with its repository's license file added. [Nature figure and Nature shared](https://github.com/yuan1z0825/nature-skills/tree/69817e4dad8bfc52fa4e59a9d8355e4264a4d3a7/skills) (Apache-2.0) make publication figures and vector method schematics with layout audits. Nature figure reads files from its sibling Nature shared, so the installer adds Nature shared whenever Nature figure is selected; [skills/dependencies.json](skills/dependencies.json) records this. Its example figures make it about 34 MB, and on Windows the toolkit should be cloned with `git -c core.longpaths=true`. [Diagram design](https://github.com/cathrynlavery/diagram-design/tree/3eb03b8/skills/diagram-design) (MIT) makes editorial architecture, flow and sequence diagrams as HTML and SVG; its PNG export script needs Python Playwright, so a browser screenshot of the page also works. [Quarto authoring](https://github.com/posit-dev/skills/tree/45685aa/quarto/quarto-authoring) (MIT) writes Quarto documents with figures, cross-references and citations; install [Quarto](https://quarto.org/docs/get-started/) to render them, and Quarto's bundled Typst produces PDF without LaTeX.

[Research ideation](https://github.com/evoscientist/evoskills/tree/4889c22/skills/research-ideation) (Apache-2.0) comes unchanged from evoskills with the repository's license file added. It is meant as one idea worker among several, not a replacement for independent workers and a blind critic: in blind trials its ideas averaged the same as working without a skill but reached higher peaks. Its instructions require evoskills' paper-navigator scripts for every search, which are not included, so tell it to search with the arXiv tools, skip its memory steps, and stop before proposal expansion.

The Zotero library skill files papers into a per-project collection without changing anything already in the library. It needs the [Zotero MCP server](https://github.com/54yyyu/zotero-mcp) (MIT), installed once per machine for the user's account rather than per project. With Zotero 7 or later running and "Allow other applications on this computer to communicate with Zotero" enabled, run the following in PowerShell.

```powershell
py -3.12 -m venv "$env:LOCALAPPDATA\zotero-mcp"
& "$env:LOCALAPPDATA\zotero-mcp\Scripts\python.exe" -m pip install "zotero-mcp-server[pdf]==0.15.1"
claude mcp add zotero --scope user -e ZOTERO_LOCAL=true -- "$env:LOCALAPPDATA\zotero-mcp\Scripts\zotero-mcp.exe" serve
```

For Codex, add a `[mcp_servers.zotero]` entry to `~/.codex/config.toml` with the same command and `args = ["serve"]`, `env_vars = ["ZOTERO_API_KEY", "ZOTERO_LIBRARY_ID"]` and `ZOTERO_LOCAL = "true"` under `[mcp_servers.zotero.env]`. Reading works without a key. Adding papers on Zotero versions before 10 needs a key from zotero.org/settings/keys, stored by the user in the `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID` environment variables. Block the tools that delete or change existing content: in Claude Code, deny `mcp__zotero__` plus each of `zotero_delete_item`, `zotero_delete_collection`, `zotero_delete_annotation`, `zotero_merge_duplicates`, `zotero_update_item`, `zotero_update_collection`, `zotero_batch_update`, `zotero_set_item_parent`, `zotero_manage_note`, `zotero_create_annotation`, `zotero_update_annotation`, `zotero_add_item_relation`, `zotero_remove_item_relation` and `zotero_authorize_local_writes` in `~/.claude/settings.json`; in Codex, list the same names in `disabled_tools`. The full install is about 360 MB.

## MCP servers

| Server | When to use it | Setup |
| --- | --- | --- |
| Playwright | Open and interact with pages when ordinary fetching does not work. | Install Node.js 20+ with npx and Microsoft Edge. The pinned server launches Edge headlessly with an isolated profile. |
| arXiv | Find papers and check metadata or available full text before writing a research note. | The community-hosted HTTP endpoint at `https://arxiv.caseyjhand.com/mcp` requires network access. |
| Firecrawl | Search the wider web for sources, scrape a known public URL, or parse a document. Prefer arXiv for paper metadata and Playwright for pages that need interaction. | Hosted HTTP server. Search, Scrape and Parse work without an account or API key, within daily limits. [Keyless access](https://docs.firecrawl.dev/mcp-server/keyless) |

To opt in, add `"firecrawl"` to your profile's `mcp` list or run `python install.py --client codex --project . --server firecrawl`. The example profile keeps its existing two-server selection.

For a machine with Chrome instead of Edge, change the Playwright browser argument from `msedge` to `chrome` in the installed configuration. [Playwright MCP documentation](https://github.com/microsoft/playwright-mcp)

## Client discovery and verification

| Client | Project skill folder | Project MCP configuration |
| --- | --- | --- |
| Codex | `.agents/skills/` | `.codex/config.toml` |
| Claude Code | `.claude/skills/` | `.mcp.json` |
| Cursor | `.cursor/skills/` | `.cursor/mcp.json` |

Start a new session in the target project. Trust the project and approve its servers if prompted. Check `/mcp` in Codex or Claude Code, or Cursor's MCP settings. To verify actual tool use, ask Playwright to open `https://example.com` and report the page title. Ask arXiv to retrieve metadata for `1706.03762` and report the title. For Firecrawl, ask it to scrape `https://example.com` and return the page title from its metadata (`Example Domain`).

Other assistants can read an individual skill folder directly. MCP-capable clients can use the same HTTP URL or launch command in [servers.json](mcp/servers.json) with their own settings format.

## A small research workflow

For a paper question that needs a short answer, select the `scout` skill. Ask the agent to read its guide before starting. For a reviewed answer, also select Critic and give it the draft and the evidence cards.

1. Frame one question that a primary source can answer. Use arXiv to identify the paper and read the relevant section.
2. Use Firecrawl to locate the publisher's copy and compare the relevant passage. Use Playwright when a page needs interaction or you want to check what a reader sees. Two copies of the same paper verify the reading, but count as one source.
3. Record the claim, the section that supports it, a link and any qualification. Check what the source actually says before drafting the answer.
4. Write the answer in plain language, naming the evidence for each point. Keep the evidence and any setup issues in the project note.
In unattended Codex sessions, browser navigation may require interactive approval. If approval is unavailable, mark the browser check as skipped and name the evidence actually used. For a task that requires browser verification, run that step in an interactive session.

## Delegate a research project

Install the [research team profile](profiles/research-team.json) with Python 3.11 or later. From the toolkit checkout run the following command, replacing the project path and choosing `codex` or `claude`.

```sh
python install.py --project "/path/to/project" --client codex --profile profiles/research-team.json
```

Open the target project in the chosen client and give the coordinator one brief:

> Use the parent skill to coordinate a delegated research team. Investigate [question] using [sources]. Return a short answer with the evidence and a separate critic's verdict.

The profile supplies one coordinator and four supporting role guides. The client supplies actual subagents. Codex needs its multi-agent capability enabled; Claude Code needs the Agent tool available. The coordinator chooses assignments and launches workers; installing a profile by itself starts no agents. The critic gets the author's result and checks it in its own context. Check the client's worker activity or tool log to verify delegation. The profile works with local sources. For web research, add the desired server flags when installing, and check that the assigned worker can access the tool.

Model selection is separate from role assignment. This profile sets no model names or reasoning levels. Each client uses its own worker defaults unless you configure an override. A scout and critic may use the same model in separate contexts. When recording a handoff, include the model only if the client reports it.

### Claude Code agent teams

For a researcher-to-critic handoff, the lead can dispatch ordinary subagents. Choose Claude Code's native agent teams when researchers need to challenge one another directly. Ask each investigator to own a different hypothesis and send the other a specific item of evidence to check. To verify that a team actually formed, check for a teammate-to-teammate message and its reply alongside the final verdict. A list of named workers alone cannot establish this.

Agent teams must be available and enabled in the Claude Code session. See [Claude Code agent teams](https://code.claude.com/docs/en/agent-teams) for setup. The coordinator's division of work also draws on [Anthropic's research system write-up](https://www.anthropic.com/research/multi-agent-research-system) and the [Superpowers parallel dispatch skill](https://github.com/obra/superpowers/blob/main/skills/dispatching-parallel-agents/SKILL.md).

### Why there is one coordinator

Give the parent coordinator the question and desired outcome. It assigns independent inputs to separate workers, checks that all expected evidence came back, and sends the proposed conclusion to a fresh critic. When teammates need to challenge each other directly, it uses peer messaging where available. The researcher does not select a dispatch strategy.

We compared the existing coordinator alone, with Superpowers dispatch, with pstack swarm, and with both on the same two-site task in Claude Code. All four reached 104/125 and rejected the incorrect claim about both sites. The combination made source coverage explicit; one report also confused rows with observations. The default therefore combines independent assignments and coverage reconciliation with a final check of units and claim scope. A missing-source test withheld the unsupported overall estimate. Codex also ran the combination with two scouts and a separate critic. These small trials establish functionality, not a general speed or accuracy advantage.

The coordinator bundles the [Superpowers dispatch guide](skills/research/parent/references/dispatching-parallel-agents/GUIDE.md) and [pstack swarm guide](skills/research/parent/references/swarm/GUIDE.md) as internal references, each with its MIT license. [Superpowers source revision](https://github.com/obra/superpowers/tree/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/dispatching-parallel-agents) · [pstack source revision](https://github.com/backnotprop/pstack/tree/6c75f4e67546c2ddbf9634734c1e3ebbea34861a/skills/swarm)
