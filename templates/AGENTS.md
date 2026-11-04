# Project agent rules

Claude Code loads this file through CLAUDE.md and Codex loads it directly, so both clients start with the same rules. Fill in the Project section when the project starts.

## Project

- Name: (working name)
- GitHub: (owner/repository, or "local only")
- Zotero collection: (name and key; ask the user, then create it with the `zotero-library` skill)

## Coordinator by default

The session the user talks to is the coordinator and follows the `parent` skill. For a quick question or a single edit, work directly. For anything larger:

1. Plan. State the goal, inputs and the check that means done. Use `router` to choose roles.
2. Delegate. Give each independent part its own worker, in parallel when neither needs the other's result. Each brief names the role, the path to its SKILL.md, inputs, expected output and limits. Workers are read-only unless they need to write, and each writer owns its own files.
3. Critique. Send the result to a fresh `critic` that did not author it. It returns PASS, REVISE or BLOCKED. On REVISE, return the objection to the author and review again.
4. Report. Give the user one answer: the conclusion, what remains open, and a handoff record of the actual workers, their platform and each verdict. Never invent a worker, result or review.

## Workers on both platforms

- Claude Code workers: the `Agent` tool. Codex workers: `spawn_agent` (enable Codex's `multi_agent` feature).
- Claude Code to Codex: pipe the brief on stdin, `$brief | codex exec -C . -s read-only -o .agent-runs/<name>.md -`. Never pass a multi-line brief as an argument: on Windows the Codex launcher runs through cmd.exe, which cuts it at the first newline. Exit code 0 does not mean the task was done, so read the saved answer. If `codex` is not found, reload PATH from the user environment.
- Codex browser tasks: use `--approve-for-me` in place of `-s` (the two cannot be combined). Codex then runs in its workspace-write sandbox and sends approval requests to its automatic reviewer, so the Playwright tools run unattended. Playwright blocks `file:` URLs, so serve local pages with `python -I -m http.server <port> --bind 127.0.0.1 --directory <folder>`.
- Codex to Claude Code: pipe the brief from a PowerShell here-string into `claude -p --no-session-persistence --tools Read --allowedTools Read --permission-mode dontAsk --strict-mcp-config`. Request escalated permissions (outside the sandbox) on the first attempt: inside the sandbox it has no network and hangs with no output. With escalation it answers in about 10 seconds. Under `--approve-for-me` the automatic reviewer approves; in an interactive session the user approves. It uses the user's Claude plan, so it fails while Claude's usage limit is reached. With `--no-session-persistence` Claude keeps no session file, so save the verdict to `.agent-runs/`.
- When a result matters, run the critic on the other platform from the author so a different model checks it.
- Writers on different platforms never edit the same files at the same time.
- Use Claude Code agent teams (teammates messaging each other) only when workers must challenge each other's findings. Confirm with the user before starting one.

## Skills and tools

The same skills are installed in `.claude/skills/` and `.agents/skills/` from ART (apattichis/agentic-research-toolkit), selected by `toolkit.json`.

| Need | Skill |
| --- | --- |
| Coordinate, choose the next role | `parent`, `router` |
| Gather and verify evidence | `scout` |
| Map findings, form a testable hypothesis | `cartographer`, `claims` |
| Design and run a bounded test | `experimenter`, `dynamics-analyst` |
| Review, revise, file results | `critic`, `synthesizer`, `archivist` |
| Commits | `git-commit` |
| Find and vet new skills | `find-skills` |
| Find, add and file papers in the user's Zotero library | `zotero-library` |
| Academic figures and method schematics | `nature-figure` (needs its sibling `nature-shared`) |
| Product and explainer diagrams | `diagram-design` |
| Reports and PDFs with figures and citations | `quarto-authoring` |
| Slides and talks | `quarto-authoring` (reveal.js HTML; render each slide to PNG for checks; one figure panel per slide) |
| Generate and rank research ideas | The "Research ideas" routine below, with `research-ideation` as one of its workers |

MCP servers: arXiv for papers and metadata, Firecrawl for web search and scraping, Playwright for pages that need interaction. Prefer arXiv for papers. Claude Code may ask to approve the servers in `.mcp.json`. Codex reads `.codex/config.toml` only once the project is trusted in Codex; until then its servers come from the user config.

Zotero (installed once per machine for the user's account; follow the `zotero-library` skill): read and search the whole library freely. Agents may add new papers, create the project's collection and add papers to it, and attach files only to papers they added. Never delete anything, never remove a paper from a collection, and never change existing collections, items, notes or annotations; block the tools that could in both clients' settings. Search the library before adding a paper so nothing is duplicated, and tag added papers `added-by-agent`. In Codex every Zotero call needs approval, so delegated Codex runs that use Zotero need `--approve-for-me`.

Semantic Scholar: the user's key is in the `S2_API_KEY` environment variable (send it as the `x-api-key` header, never print it). The limit is one request per second for the whole key, across all endpoints and all agents at once, so keep requests at least 1.1 seconds apart and let only one worker use Semantic Scholar at a time; parallel workers use arXiv instead. On HTTP 429, wait and retry with exponential backoff.

To update a skill, delete its folder in both skill directories and rerun the toolkit installer for each client with `--profile toolkit.json`. The installer stops on any skill or server that differs instead of overwriting it.

### Third-party skills

Each is copied from upstream at a pinned commit, with the upstream repository's `LICENSE` file added to the folder, and is unchanged except where the notes below say otherwise.

| Skill | Source and commit | License | Notes |
| --- | --- | --- | --- |
| `find-skills` | vercel-labs/skills `7a5e920` | MIT | Searches skills.sh with `npx -y skills@1.7.6 find <query>`. Its step 6 installs globally without confirmation (`npx skills add <package> -g -y`); override it: show the user each candidate's source, install count and stars, install only after their yes, put the skill in both project skill folders, and record its source. |
| `nature-figure`, `nature-shared` | yuan1z0825/nature-skills `69817e4` | Apache-2.0 | Use the Python route (matplotlib, numpy and PyMuPDF). Keep its saved preference inside the project, not under `~/.config`. Run its audit scripts, but they check layout, not meaning, so a critic still reads the figure. Its collision audit can fail a clean figure when the PDF groups several labels into one text object; confirm against the rendered PNG and record the reconciliation. Codex does not list `nature-shared` at startup; `nature-figure` still reads its files. ART leaves out the upstream figures4papers reference examples (CC BY-NC 4.0); `assets/figures4papers/README.md` says where to get them. |
| `diagram-design` | cathrynlavery/diagram-design `3eb03b8` | MIT | Its PNG export script needs Python Playwright. Without it, capture PNGs with the Playwright MCP browser from a local `http.server`. Use system fonts. |
| `research-ideation` | evoscientist/evoskills `4889c22` | Apache-2.0 | Use only as one worker in the "Research ideas" routine. Its SKILL.md requires the `paper-navigator` scripts for every search, which are not installed; override that: search with the arXiv tools, skip Step 0 and the evo-memory update, keep refinement and ranking condensed, and stop before user selection and proposal expansion. Never write to `/memory` at the drive root. |
| `quarto-authoring` | posit-dev/skills `45685aa` | MIT | Needs Quarto on PATH. Render PDF through Typst (bundled with Quarto). Build `references.bib` from arXiv tool metadata or the project's Better BibTeX export, and use the IEEE CSL from citation-style-language/styles. |

## Figures and documents

Anything visual the user will see goes through the coordinator loop with these checks:

1. The author renders it to PNG and looks at it before handing it over.
2. A critic on the other platform opens the images, reads every page, and checks each number, caption and figure reference against the source data.
3. Fixes go back to the author, then the critic re-checks only what changed.

Standing rules: label synthetic numbers "Illustrative synthetic data" in the figure and the caption. Captions and text must describe what the final figure shows, so check them again after swapping figures. Diagrams for non-specialists use at least 12 px tag text and 13 px labels and legends, plain words for jargon, and no tool names in titles.

## Research ideas

No ideation skill replaces this routine: in blind trials, ideation skills did not beat independent workers plus a blind critic on average, and every method converged on the same few ideas. Run it like this:

1. Brief three to five idea workers independently, across both platforms, with the same problem, constraints and arXiv budget. Give each a different starting lens: the users and their setting, a case where current methods break, or a cost the field ignores. Have one worker follow `research-ideation` with the override above: its runs averaged the same as the others but reached higher peaks, which helps when only the best idea is kept. Each returns three ideas with the problem and its tension, why now, the real-world side, the core insight, a first experiment, the closest prior work by verified arXiv ID, and the biggest risk.
2. A blind critic on the other platform reads only the idea files. It scores each idea from 1 to 5 on novelty, real-world side, framing, feasibility and specificity, verifies sampled citations, runs one arXiv novelty search per set's best idea, and names ideas that overlap.
3. Show the user the top ideas with the critic's objections. The chosen idea goes to `claims`.

`superpowers:brainstorming` is a Claude Code plugin for shaping a feature or design with the user. It is not for research ideas, and Codex does not have it.

## Conventions

- Worker output goes in `.agent-runs/`, which git ignores. Playwright snapshots in `.playwright-mcp/` are ignored too.
- Never use em dashes in text, UI or commit messages.
- Commits use Conventional Commits, `type(scope): message`. Show the message to the user, commit only after they approve it, and never add a Co-Authored-By line.
