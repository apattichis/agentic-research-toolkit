# ART adaptations

- Upstream: [vercel-labs/skills](https://github.com/vercel-labs/skills), skill `find-skills`, pinned at commit `7a5e920`.
- License: MIT (`LICENSE` in this folder, copied from upstream).

## Changes from upstream

| File | Change | Why |
| --- | --- | --- |
| `SKILL.md` | Added the "ART adaptation (read first)" section between the frontmatter and the upstream text. The frontmatter and the upstream text are unchanged. | Upstream runs an unpinned CLI and, in its step 6, installs globally without confirmation (`npx skills add <package> -g -y`). The skill must be safe when installed on its own, without the ART rulebook. |

What the adaptation section changes in behavior:

1. Every `skills` command uses the pinned CLI, `npx -y skills@1.7.6`, with search as `npx -y skills@1.7.6 find <query>`.
2. Candidates are shown with their source, install count and GitHub stars before anything is installed.
3. A skill is installed only after the user agrees, at project scope in both `.claude/skills/` and `.agents/skills/`, never with `-g` and never with the CLI's own `-y`.
4. The installed source and version are reported so the project can record them.
5. `skills update` is not run on the user's behalf.

## Updating

Copy the folder from upstream at a newer commit, reapply the adaptation section, update the commit above, and check whether a newer pinned CLI version should replace `1.7.6`.
