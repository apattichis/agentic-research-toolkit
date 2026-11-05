# ART adaptations

- Upstream: [evoscientist/evoskills](https://github.com/evoscientist/evoskills), skill `research-ideation`, pinned at commit `4889c22`.
- License: Apache-2.0 (`LICENSE` in this folder, copied from upstream). Under section 4(b) of that license, this file and the "ART adaptation" section of `SKILL.md` are the notice that ART changed the files listed below.

## Changes from upstream

| File | Change | Why |
| --- | --- | --- |
| `SKILL.md` frontmatter | `description` rewritten to describe the adapted workflow and to point at ART's `scout`, `cartographer` and `claims` instead of skills ART does not bundle. `name`, `allowed-tools` and `metadata` (author EvoScientist, version 2.1.2) are unchanged. | The upstream description promises evo-memory updates, user selection and proposal expansion, which ART skips. |
| `SKILL.md` | Added the "ART adaptation (read first)" section above the upstream text. The upstream text below it is unchanged. | Makes the skill work when installed on its own, without the ART rulebook. |

What the adaptation section changes in behavior:

1. Paper search uses the arXiv MCP tools instead of the `paper-navigator` scripts, which ART does not bundle. The upstream ban on generic web search for paper discovery still applies.
2. Step 0 (load evo-memory) and Step 6 (update evo-memory) are skipped. Nothing is written to `/memory` or any other root path.
3. Outputs go inside the project, at the brief's path or `.agent-runs/research-ideation/`, instead of `/direction-summary.md` and `/research-proposal.md`.
4. Refinement and ranking are kept condensed to fit the brief's budget.
5. The skill stops after the ranked ideas: no selection prompt, no proposal expansion (Step 7) and no Step 8.
6. Handoffs to unbundled skills are replaced with ART's `scout`, `cartographer`, `claims` and `experimenter`.

Files under `references/` and `assets/` are unchanged from upstream.

## Updating

Copy the folder from upstream at a newer commit, reapply the frontmatter change and the adaptation section, update the commit above, and check that the upstream text has not added new required dependencies.
