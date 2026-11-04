# ART: Agentic Research Toolkit

![Version 0.1.0](https://img.shields.io/badge/version-0.1.0-1f6f78) ![License: MIT](https://img.shields.io/badge/license-MIT-2f7a3e) ![Clients: Claude Code and Codex](https://img.shields.io/badge/clients-Claude%20Code%20%7C%20Codex-56625f)

**Your AI research team, set up in minutes.**

![How ART works: you ask, a coordinator plans and delegates to workers on Claude Code and Codex, a critic on the other model checks the work, and you get one answer](docs/how-it-works.png)

A project template for giving AI assistants the skills and tools a project needs. Skills describe how to do a task. MCP servers give an assistant access to a browser, academic papers, or web search and extraction.

## What you get

With ART's skills and project rules installed in both, and each client's own delegation tools available, Claude Code and Codex work as one research team that follows a single rulebook. You ask in plain language. A coordinator plans the work, hands the parts to specialist workers on either platform, and sends important results to a critic on the other model before you see them.

### What's inside

- **18 skills**: guides an agent loads when a task needs one, such as how to verify a source, review a draft or make a publication figure. See [Skills](#skills).
- **3 MCP servers**: connections that give agents real tools: arXiv for papers, Firecrawl for web search and pages, and Playwright for a real browser. Zotero and Semantic Scholar can be added once per machine. See [MCP servers](#mcp-servers).
- **One rulebook** ([templates/AGENTS.md](templates/AGENTS.md)): the rules both clients follow, covering the coordinator workflow, cross-model critics, figure checks, the idea routine and safety rules.
- **An installer** ([install.py](install.py)): copies the skills, server settings and rules into a project for Claude Code, Codex or Cursor, and stops instead of overwriting anything you changed.

### The team

![Meet the team: a coordinator, eight core research roles and seven specialists](docs/team.png)

- **Coordinator** (`parent`, `router`): plans the goal, the inputs and what done means, picks the roles, and reports back with a record of who did what.
- **Core research team**: scout, cartographer, claims, experimenter, dynamics analyst, critic, synthesizer and archivist.
- **Specialists**: an idea panel (independent idea workers, one of them following `research-ideation`, and a blind scoring critic), a librarian (`zotero-library`), a figure maker (`nature-figure`), a diagrammer (`diagram-design`), a publisher for reports and slides (`quarto-authoring`), a skill scout (`find-skills`) and a committer (`git-commit`).

### How a task runs

1. You ask Claude Code or Codex.
2. The coordinator plans and delegates, in parallel where the parts are independent.
3. Workers run on Claude Code, Codex or both.
4. A critic on the other model returns PASS, REVISE or BLOCKED. Revisions go back to the author and are checked again.
5. You get one answer: the result, what is still open, and who did what.

Team formats: solo for quick questions, a delegated team by default, cross-model review, the idea panel, and debate teams in which Claude Code teammates challenge each other (available, not yet tested).

### Safety rules

These are instructions in the project rules (`--rules`), plus the Zotero settings described below:

- Agents show you the commit message and commit only after you approve it.
- With the Zotero setup below, selected tools that delete or edit existing items are blocked in both clients. The rules forbid using the remaining collection tool to remove a paper from a collection, and forbid other destructive actions. Agents can add papers and fill the project's collection.
- Findings need evidence, and important work is checked by a critic that did not write it. The rules ask for this check; they cannot guarantee that every mistake is caught.

### Tested

Four skill choices were tested head-to-head against two or three alternatives each, with blind critics on the other platform: research ideation, publication figures, paper review and slides. No challenger clearly beat the chosen tools. Both clients passed the same checks in a working project, and on the test machine fresh sessions of each set ART up within minutes from the repository link and a one-line request. The results are in [docs/evidence.md](docs/evidence.md).

### Limits

- You need Python 3.11 or later and Claude Code, Codex or Cursor; the browser server also needs Node.js 20 or later and Microsoft Edge. Zotero and the API keys are optional and set up once per machine. Each project then needs one installer command per client; on the test machine it ran in under a second per client.
- A Semantic Scholar key starts at one request per second, shared by every agent that uses it.
- Delegating to Claude Code stops while your Claude usage limit is reached.
- Debate teams and the Cursor client are available but not yet tested.
- Tested on Windows 11 so far; macOS and Linux have not been tried yet.

### Status and roadmap

ART is at version 0.1.0, a pre-release: the first release is planned but not yet tagged. It works and is tested, but expect changes. Next on the list: head-to-head trials for literature search, surveys and experiments; testing debate teams and the Cursor client; and new skills, added only after they hold up in trials. Changes are recorded in [CHANGELOG.md](CHANGELOG.md).

### Give this link to your assistant

Open your project in Claude Code or Codex and paste:

> Set up https://github.com/apattichis/agentic-research-toolkit in this project for the client I'm using, with all skills, the arXiv, Firecrawl and Playwright servers, and the project rules. Preview the changes first, preserve existing settings, and tell me which tools you verified.

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

The visual and report skills come from upstream at pinned revisions, each with its repository's license file added, and unchanged except as noted below. [Nature figure and Nature shared](https://github.com/yuan1z0825/nature-skills/tree/69817e4dad8bfc52fa4e59a9d8355e4264a4d3a7/skills) (Apache-2.0) make publication figures and vector method schematics with layout audits. Nature figure reads files from its sibling Nature shared, so the installer adds Nature shared whenever Nature figure is selected; [skills/dependencies.json](skills/dependencies.json) records this. ART leaves out the upstream skill's figures4papers reference examples, which are licensed CC BY-NC 4.0; [their folder](skills/visuals/nature-figure/assets/figures4papers/README.md) says where to get them. On Windows, clone the toolkit with `git -c core.longpaths=true`. [Diagram design](https://github.com/cathrynlavery/diagram-design/tree/3eb03b8/skills/diagram-design) (MIT) makes editorial architecture, flow and sequence diagrams as HTML and SVG; its PNG export script needs Python Playwright, so a browser screenshot of the page also works. [Quarto authoring](https://github.com/posit-dev/skills/tree/45685aa/quarto/quarto-authoring) (MIT) writes Quarto documents with figures, cross-references and citations; install [Quarto](https://quarto.org/docs/get-started/) to render them, and Quarto's bundled Typst produces PDF without LaTeX.

[Research ideation](https://github.com/evoscientist/evoskills/tree/4889c22/skills/research-ideation) (Apache-2.0) comes unchanged from evoskills with the repository's license file added. It is meant as one idea worker among several, not a replacement for independent workers and a blind critic: in blind trials its ideas averaged about the same as working without a skill (18.56 against 18.33 out of 25, three runs each) but reached higher peaks. Its instructions require evoskills' paper-navigator scripts for every search, which are not included, so tell it to search with the arXiv tools, skip its memory steps, and stop before proposal expansion.

The Zotero library skill files papers into a per-project collection. It adds papers and collection memberships. It never deletes items, collections, notes or annotations, never edits existing items, and never removes a paper from a collection. It needs the [Zotero MCP server](https://github.com/54yyyu/zotero-mcp) (MIT), installed once per machine for the user's account rather than per project. With Zotero 7 or later running and "Allow other applications on this computer to communicate with Zotero" enabled, run the following in PowerShell.

```powershell
py -3.12 -m venv "$env:LOCALAPPDATA\zotero-mcp"
& "$env:LOCALAPPDATA\zotero-mcp\Scripts\python.exe" -m pip install "zotero-mcp-server[pdf]==0.15.1"
claude mcp add zotero --scope user -e ZOTERO_LOCAL=true -- "$env:LOCALAPPDATA\zotero-mcp\Scripts\zotero-mcp.exe" serve
```

For Codex, add a `[mcp_servers.zotero]` entry to `~/.codex/config.toml` with the same command and `args = ["serve"]`, `env_vars = ["ZOTERO_API_KEY", "ZOTERO_LIBRARY_ID"]` and `ZOTERO_LOCAL = "true"` under `[mcp_servers.zotero.env]`. Reading works without a key. Adding papers on Zotero versions before 10 needs a key from zotero.org/settings/keys, stored by the user in the `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID` environment variables. Block selected tools that delete or change existing content (the `zotero-library` skill also forbids removing collection memberships with `zotero_set_item_collections`, which stays allowed for adding them): in Claude Code, deny `mcp__zotero__` plus each of `zotero_delete_item`, `zotero_delete_collection`, `zotero_delete_annotation`, `zotero_merge_duplicates`, `zotero_update_item`, `zotero_update_collection`, `zotero_batch_update`, `zotero_set_item_parent`, `zotero_manage_note`, `zotero_create_annotation`, `zotero_update_annotation`, `zotero_add_item_relation`, `zotero_remove_item_relation` and `zotero_authorize_local_writes` in `~/.claude/settings.json`; in Codex, list the same names in `disabled_tools`. The full install is about 360 MB.

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

## License and trademarks

ART is released under the [MIT License](LICENSE). Third-party skills keep their own licenses, included in each skill folder. Claude Code is a product of Anthropic and Codex is a product of OpenAI; ART is an independent project and is not affiliated with either.
