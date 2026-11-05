# ART adaptations

- Upstream: [backnotprop/pstack](https://github.com/backnotprop/pstack/tree/6c75f4e67546c2ddbf9634734c1e3ebbea34861a/skills/swarm), `skills/swarm/SKILL.md`, pinned at commit `6c75f4e67546c2ddbf9634734c1e3ebbea34861a`, bundled here as `GUIDE.md`.
- License: MIT (`LICENSE` in this folder, copied from upstream).

## Changes from upstream

| File | Change | Why |
| --- | --- | --- |
| `GUIDE.md` | Added an "ART note" between the frontmatter and the upstream text, without editing that text. | Step 3 and Phase B name pstack settings files, a `grok-4.7-xhigh-fast` default model, the `poteto-mode` skill and Cursor-only `Task` parameters, none of which ART ships. They conflict with ART's model guidance, which comes from the project rulebook and the `parent` skill. |

## Updating

Copy the upstream file at a newer commit to `GUIDE.md`, reapply the ART note, and update the commit above.
