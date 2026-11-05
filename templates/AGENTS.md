# Project agent rules

Claude Code loads this file through CLAUDE.md and Codex loads it directly, so both clients start with the same rules. Fill in the Project section when the project starts.

## Project

- Name: (working name)
- GitHub: (owner/repository, or "local only")
- Zotero collection: (name and key; ask the user, then create it with the `zotero-library` skill)

## Coordinator by default

The session the user talks to is the coordinator and follows the `parent` skill. For a quick question or a single edit, work directly. For anything larger:

1. Plan. State the goal, inputs and the check that means done. Use `router` to choose roles.
2. Delegate. Give each independent part its own worker, in parallel when neither needs the other's result and the work is light (see Budget and load). Each brief names the role, the path to its SKILL.md, inputs, expected output and limits. Workers are read-only unless they need to write, and each writer owns its own files.
3. Critique. Send the result to a fresh `critic` that did not author it. It returns PASS, REVISE or BLOCKED. On REVISE, return the objection to the author and review again.
4. Report. Give the user one answer: the conclusion, what remains open, and a handoff record of the actual workers, their platform and each verdict. Never invent a worker, result or review.

## Workers on both platforms

- Claude Code workers: the `Agent` tool. Codex workers: `spawn_agent` (enable Codex's `multi_agent` feature).
- To hand work to the other client, pipe the brief on stdin to its non-interactive mode (see Client recipes) and save the answer in `.agent-runs/`. Never pass a multi-line brief as a command-line argument: some launchers cut it at the first newline.
- Give each handoff the narrowest permissions the task needs, read-only for research and review. Check what the current environment allows (sandbox, network, approval mode) before asking for anything broader, and ask only when that check shows the task cannot run without it.
- Set a deadline that fits the task. Exit code 0 does not mean the task was done, so read the saved answer. If a handoff fails, passes its deadline or returns nothing, stop it, record the failure in the handoff record, and retry only once the cause is known and fixed; otherwise wait for the other client or ask the user. Never widen permissions or swap in a same-platform critic on your own.
- A handoff uses the user's plan on the other client, so it fails while that client's usage limit is reached.
- Run the critic on the other platform from the author so a different model checks the work (see Budget and load).
- Writers on different platforms never edit the same files at the same time.
- Use Claude Code agent teams (teammates messaging each other) only when workers must challenge each other's findings. Confirm with the user before starting one.

### Client recipes

Tested on Windows 11: the PowerShell handoffs including the `Set-Content` step that saves Claude's reply, and in Git Bash the Codex command with explicit model and effort flags and the research-review variant (it reached arXiv). Not tested yet: the Bash recipes on macOS and Linux. Before the first handoff in a session, check that the other client runs (`codex --version`, `claude --version`). Client flags change between versions, so check `codex exec --help` or `claude --help` if one is refused. Each recipe creates `.agent-runs/` first, because the installer does not.

Claude Code to Codex (read-only worker or critic). Replace `<model>` with the strongest Codex model available (see Budget and load):

```powershell
New-Item -ItemType Directory -Force .agent-runs | Out-Null
$brief = @'
<the brief>
'@
$brief | codex exec -m <model> -c model_reasoning_effort="high" -C . -s read-only -o .agent-runs/<name>.md -
```

```bash
mkdir -p .agent-runs
codex exec -m <model> -c model_reasoning_effort="high" -C . -s read-only -o .agent-runs/<name>.md - <<'EOF'
<the brief>
EOF
```

Codex to Claude Code, local-file review: Claude may only read project files and loads no MCP servers. With `--no-session-persistence` Claude keeps no session file, so the saved file is the only record.

```powershell
New-Item -ItemType Directory -Force .agent-runs | Out-Null
$brief | claude -p --model opus --effort high --no-session-persistence --tools Read --allowedTools Read --permission-mode dontAsk --strict-mcp-config | Set-Content -Encoding utf8 .agent-runs/<name>.md
```

```bash
mkdir -p .agent-runs
claude -p --model opus --effort high --no-session-persistence --tools Read --allowedTools Read --permission-mode dontAsk --strict-mcp-config > .agent-runs/<name>.md <<'EOF'
<the brief>
EOF
```

Codex to Claude Code, research review: for a critic that must run arXiv searches, such as the novelty check in Research ideas. It loads only the arXiv server and allows only its read-only tools besides `Read`.

```powershell
New-Item -ItemType Directory -Force .agent-runs | Out-Null
[IO.File]::WriteAllText("$PWD/.agent-runs/arxiv-mcp.json", '{"mcpServers":{"arxiv":{"type":"http","url":"https://arxiv.caseyjhand.com/mcp"}}}')
$brief | claude -p --model opus --effort high --no-session-persistence --tools Read --mcp-config .agent-runs/arxiv-mcp.json --strict-mcp-config --allowedTools "Read,mcp__arxiv" --permission-mode dontAsk | Set-Content -Encoding utf8 .agent-runs/<name>.md
```

```bash
mkdir -p .agent-runs
printf '%s' '{"mcpServers":{"arxiv":{"type":"http","url":"https://arxiv.caseyjhand.com/mcp"}}}' > .agent-runs/arxiv-mcp.json
claude -p --model opus --effort high --no-session-persistence --tools Read --mcp-config .agent-runs/arxiv-mcp.json --strict-mcp-config --allowedTools "Read,mcp__arxiv" --permission-mode dontAsk > .agent-runs/<name>.md <<'EOF'
<the brief>
EOF
```

Notes from the tested setup:

- In Codex's default sandbox, `claude -p` had no network access and hung with no output. It worked when Codex ran that one command outside the sandbox with approval: from the user in an interactive session, or from Codex's automatic reviewer under `--approve-for-me`. If your sandbox allows network access, try it there first.
- Codex browser tasks: use `--approve-for-me` in place of `-s` (the two cannot be combined). Codex then runs in its workspace-write sandbox and sends approval requests to its automatic reviewer, so the Playwright tools run unattended. Playwright blocks `file:` URLs, so serve local pages with `python -I -m http.server <port> --bind 127.0.0.1 --directory <folder>`.
- On Windows, `codex` installed through a Node version manager can be a `.cmd` launcher that runs through cmd.exe, which is why the brief goes on stdin. If a client installed during the session is not found, reload PATH from the user environment.

## Budget and load

Spend usage and machine time where they change the result, and never save on reasoning.

- **Delegate when it pays off.** Workers suit broad work that splits into independent parts. Do a quick question or a small, tightly connected task directly. Scale effort to the task: a substantial comparison may benefit from two or three workers; only a broad research question needs more, run in batches.
- **Strong models for thinking work.** Planning, research reasoning, writing or checking claims, design and creative work, debugging, and every critic use the strongest available model at high reasoning effort. If you are unsure whether a task needs reasoning, treat it as if it does: redoing a weak result costs more than the saving.
- **Cheaper models only for mechanical work**: a task with a clear spec whose result can be checked without judgement, such as moving or converting files, formatting, or running a known command and collecting its output. In Claude Code, set the `Agent` tool's `model` (for example `sonnet`), or pass `--model` and `--effort` to `claude -p`; in Codex, pass `-m <model>` and `-c model_reasoning_effort="<level>"` to `codex exec`. Record the model the client reports for each worker in the handoff.
- **One critic, on the other platform.** By default one critic checks a result, on the other platform from the author: Codex work gets a Claude Code critic, and Claude Code work gets a Codex critic. Add a second critic only when it brings a check the first cannot, such as a high-stakes result or a separate source-data check, and put it on the other platform from its author too. If the other platform is unavailable, wait for it or ask the user; do not swap in a same-platform critic on your own. Scripts handle mechanical checks (links, formatting, counts); they add to the critic's review of meaning, figures and numbers and never replace it.
- **Parallel for light work, one at a time for heavy work.** Reading, searching, writing and reviewing can run in parallel, at most three workers at once across both platforms; run larger panels in batches. Renders, builds, local models and anything else that works the CPU or GPU hard run one at a time. Start one only when CPU load is under about 40 percent and at least a quarter of memory is free, cap its threads or workers at about half the CPU cores, and wait if the machine is busy.
- **Lock the plan before expensive work.** Before a large build, a full render, a long local-model run or a large worker panel, agree the goal, the inputs and the done-check with the user and get a critic's PASS on the plan. Small previews and feasibility checks may come first. Batch each review round's feedback into one revision and repeat the review until PASS or BLOCKED; stop a worker that is on the wrong path instead of redirecting it piece by piece.
- **Tight briefs, short replies.** Point each worker at the skill or file it needs instead of restating it. Ask for short replies with file paths and keep the detail in saved files. Reuse saved results in `.agent-runs/` instead of rerunning work.
- **Usage limits.** Check remaining usage before a large run. When a client's usage limit is reached, pause and resume after it resets; move the work to the other platform only if the user agrees.

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

To update a skill, never delete an installed skill folder before keeping its local edits, such as a style guide filled in during diagram-design onboarding. Follow "Update an installation" in ART's `docs/installation.md`: copy the installed skill folders to a backup outside the project, compare each with the new toolkit copy (`git diff --no-index <installed folder> <toolkit folder>`), and show the user any local edits. Only then delete the folder in both skill directories, rerun the toolkit installer for each client with `--profile toolkit.json`, and reapply the edits the user wants to keep. The installer stops on any skill or server that differs instead of overwriting it.

### Third-party skills

Each is copied from upstream at a pinned commit, with the upstream repository's `LICENSE` file added to the folder, and is unchanged except where the notes below say otherwise.

| Skill | Source and commit | License | Notes |
| --- | --- | --- | --- |
| `find-skills` | vercel-labs/skills `7a5e920` | MIT | Searches skills.sh with `npx -y skills@1.7.6 find <query>`. ART's copy carries its own adaptation: pinned CLI, shows source, install count and stars, installs only after the user agrees, into both project skill folders, never globally. See its `ADAPTATIONS.md`. |
| `nature-figure`, `nature-shared` | yuan1z0825/nature-skills `69817e4` | Apache-2.0 | Use the Python route (matplotlib, numpy and PyMuPDF). Keep its saved preference inside the project, not under `~/.config`. Run its audit scripts, but they check layout, not meaning, so a critic still reads the figure. Its collision audit can fail a clean figure when the PDF groups several labels into one text object; confirm against the rendered PNG and record the reconciliation. Codex does not list `nature-shared` at startup; `nature-figure` still reads its files. ART leaves out the upstream figures4papers reference examples (CC BY-NC 4.0); `assets/figures4papers/README.md` says where to get them. ART also disables the schematic script's download of image URLs from the API response; see its `ADAPTATIONS.md`. |
| `diagram-design` | cathrynlavery/diagram-design `3eb03b8` | MIT | Its PNG export script needs Python Playwright. Without it, capture PNGs with the Playwright MCP browser from a local `http.server`. Use system fonts. ART removes five directly fetched logos with unclear terms; see its `ADAPTATIONS.md`. |
| `research-ideation` | evoscientist/evoskills `4889c22` | Apache-2.0 | Use only as one worker in the "Research ideas" routine. ART's copy carries its adaptation at the top of SKILL.md: arXiv tools instead of `paper-navigator`, no evo-memory, outputs inside the project, condensed ranking, stops before user selection and proposal expansion. See its `ADAPTATIONS.md`. |
| `quarto-authoring` | posit-dev/skills `45685aa` | MIT | Needs Quarto on PATH. Render PDF through Typst (bundled with Quarto). Build `references.bib` from arXiv tool metadata or the project's Better BibTeX export, and use the IEEE CSL from citation-style-language/styles. |

## Figures and documents

Anything visual the user will see goes through the coordinator loop with these checks:

1. The author renders it to PNG and looks at it before handing it over.
2. A critic on the other platform opens the images, reads every page, and checks each number, caption and figure reference against the source data.
3. Fixes go back to the author, then the critic re-checks only what changed.

Standing rules: label synthetic numbers "Illustrative synthetic data" in the figure and the caption. Captions and text must describe what the final figure shows, so check them again after swapping figures. Diagrams for non-specialists use at least 12 px tag text and 13 px labels and legends, plain words for jargon, and no tool names in titles.

## Research ideas

Use this routine rather than a single ideation skill. In a few small blind trials on one problem, a preliminary observation and not a benchmark, the ideation skills tried did not score clearly above independent workers plus a blind critic on average, and every method converged on the same few ideas. Run it like this:

1. Brief three to five idea workers independently, across both platforms, with the same problem, constraints and arXiv budget. Give each a different starting lens: the users and their setting, a case where current methods break, or a cost the field ignores. Have one worker follow `research-ideation` with the override above: in those trials its runs averaged about the same as the others but reached higher peaks, which may help when only the best idea is kept. Each returns three ideas with the problem and its tension, why now, the real-world side, the core insight, a first experiment, the closest prior work by verified arXiv ID, and the biggest risk.
2. Blind critics read only the idea files: one critic on the other platform when all workers ran on one platform; when they ran on both, one critic per platform scores the sets written on the other platform, with the same rubric, and the scores are combined. It scores each idea from 1 to 5 on novelty, real-world side, framing, feasibility and specificity, verifies sampled citations, runs one arXiv novelty search per set's best idea, and names ideas that overlap.
3. Show the user the top ideas with the critic's objections. The chosen idea goes to `claims`.

`superpowers:brainstorming` is a Claude Code plugin for shaping a feature or design with the user. It is not for research ideas, and Codex does not have it.

## Conventions

- Worker output goes in `.agent-runs/`, which git ignores. Playwright snapshots in `.playwright-mcp/` are ignored too.
- Never use em dashes in text, UI or commit messages.
- Commits use Conventional Commits, `type(scope): message`. Show the message to the user, commit only after they approve it, and never add a Co-Authored-By line.
