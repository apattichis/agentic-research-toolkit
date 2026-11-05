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

A repository made with **Use this template** starts with the toolkit's own `AGENTS.md` and `CLAUDE.md`, which tell agents how to use the toolkit itself. `--rules` recognises untouched copies of those files, from any recorded version of the toolkit and with either line ending, and replaces them with the rules template. The preview names each file it will replace. If you have edited either file, the installer stops and leaves it alone, as it does for any other `AGENTS.md` or `CLAUDE.md` that differs from the template. Move your edits elsewhere and delete the file, or merge the template into it by hand.

The installer copies complete skill folders, merges selected MCP entries into project settings, and leaves matching installations alone. If a selected name has different contents or settings, it stops so you can review the conflict. Removing an item from the profile does not uninstall it; see [Remove ART from a project](#remove-art-from-a-project).

The installer also keeps worker output and browser snapshots out of git. Git never looks inside a folder that a rule ignores as a whole, and only lines starting with `!` can bring files back. So the installer makes sure the exact lines `.agent-runs/` and `.playwright-mcp/` appear in the project's `.gitignore` after its last `!` line. If either is missing or comes earlier, for example before `!.agent-runs/review.md` or `!**/`, it appends that line at the end, creating the file if needed, and reports the lines it added. This decision needs no git. In a git repository the installer then asks `git check-ignore` about both folders and a few files inside them, and reports whether git ignores them, keeps some, or could not be asked. Files git already tracks in those folders stay tracked whatever `.gitignore` says, so the installer counts them and names the command that untracks them while keeping the files, `git rm -r --cached .agent-runs .playwright-mcp`. Entries covered only by `.git/info/exclude` or a global ignore file are added too, because those do not travel with the project. `--dry-run` only reports them. To check by hand, run `git check-ignore -v .agent-runs/example.md` in the project.

All checks run before the first write, so a conflict or an unreadable configuration file (for example malformed JSON, `"mcpServers": null`, or a server entry that is not an object or table) stops the installer with nothing changed. So does a symbolic link or junction that would take a write outside the project, or a broken link on the way to a destination. If a write fails part way, for example on a full disk, the installer lists what it wrote and what it did not. Fix the cause and run the same command again: it leaves the written items alone and adds the rest.

## Client discovery and verification

| Client | Project skill folder | Project MCP configuration |
| --- | --- | --- |
| Codex | `.agents/skills/` | `.codex/config.toml` |
| Claude Code | `.claude/skills/` | `.mcp.json` |
| Cursor | `.cursor/skills/` | `.cursor/mcp.json` |

Start a new session in the target project. Trust the project and approve its servers if prompted. Check `/mcp` in Codex or Claude Code, or Cursor's MCP settings. To verify actual tool use, ask Playwright to open `https://example.com` and report the page title. Ask arXiv to retrieve metadata for `1706.03762` and report the title. For Firecrawl, ask it to scrape `https://example.com` and return the page title from its metadata (`Example Domain`).

These checks are manual. The installer tests and CI check the files and settings the installer writes, but they cannot start Claude Code, Codex or Cursor, so client discovery is verified by hand with the steps above. A server registered in your user-level settings can hide a broken project entry, so run the checks without a user-level registration of the same server (`claude mcp list` and `codex mcp list` list the servers each client sees).

Other assistants can read an individual skill folder directly. MCP-capable clients can use the same HTTP URL or launch command in [servers.json](../mcp/servers.json) with their own settings format.

## Update an installation

The installer does not update or remove anything it installed earlier. A skill folder that differs from the toolkit's copy, whether from a newer toolkit version or from your own edits (such as a style guide filled in during diagram-design onboarding), makes it stop. To update without losing local changes:

1. Update the toolkit clone with `git pull`. In a repository made from the template, clone a fresh copy of the toolkit next to it and run that copy's installer with `--project` pointing at your repository.
2. Commit or stash the project's own changes, then copy the installed skill folders to a backup outside the project, for example `../art-backup/`.
3. Compare each installed skill with the new version. The output shows both your edits and the update.

   ```sh
   git diff --no-index .claude/skills/scout /path/to/agentic-research-toolkit/skills/research/scout
   ```

4. Delete each skill folder you want to update from the project (the backup keeps a copy), then rerun the installer with the same client and profile. It installs the new version of each missing folder and leaves the others alone.
5. Reapply the edits from step 3 that you still want, and review the result with `git diff` before committing.

For MCP settings, compare each entry the installer reports as different with [servers.json](../mcp/servers.json), or [codex.toml](../mcp/codex.toml) for Codex, then edit or remove the old entry and rerun. For the rules, compare your `AGENTS.md` with the new `templates/AGENTS.md` using `git diff --no-index` and merge the changes by hand, keeping your Project section. The installer does not overwrite a filled-in copy. These commands work in PowerShell and in POSIX shells.

## Remove ART from a project

Removing an item from the profile does not uninstall it. To remove items by hand:

1. Commit or stash the project's changes so `git status` shows exactly what the removal touches.
2. Compare each skill folder you are removing with the toolkit's copy (`git diff --no-index`, as above) and keep anything you changed. Then delete the folder named after the skill in the client's skill folder (see the table above). Keep a companion such as `nature-shared` while a skill that needs it stays installed; [dependencies.json](../skills/dependencies.json) lists them.
3. Delete only the server entries you are removing (`playwright`, `arxiv`, `firecrawl`) from the client's MCP configuration file and keep any other entries. Delete the file only if nothing else is left in it.
4. Delete `AGENTS.md`, and `CLAUDE.md` for Claude Code, only if they hold nothing of yours. Otherwise edit them.
5. Keep the `.agent-runs/` and `.playwright-mcp/` lines in `.gitignore` while those folders exist, because they can hold unpublished research and browser captures. Remove the folders first if you no longer need them.
6. Start a new session in the project and check that the removed skills and servers are gone.
