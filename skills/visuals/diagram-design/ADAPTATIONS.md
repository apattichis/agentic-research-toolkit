# ART adaptations

- Upstream: [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design), pinned at commit `3eb03b8`.
- License: MIT (`LICENSE` in this folder, copied from upstream). That license covers the skill's own work; embedded third-party icons carry their own terms, listed in the "License attribution" section of `references/primitive-icons.md`.

## Changes from upstream

| File | Change | Why |
| --- | --- | --- |
| `references/primitive-icons.md` | Removed the embedded SVG logos for `hop`, `pentaho`, `dagster`, `sas` and `stata`. Each heading stays, with a note that the logo was removed in ART and can be fetched from upstream. Added one sentence to the "License attribution" section saying so. | Upstream marks each of these as "Direct fetch" from a vendor or third-party site (`hop.apache.org`, `cdn.worldvectorlogo.com`, `cdn.prod.website-files.com`, `upload.wikimedia.org`, `icon.icepanel.io`) with "verify license before use". Their redistribution terms are unclear, so ART does not redistribute them. |
| `assets/icons.html` | Removed the gallery cells for the same five logos and left an HTML comment where they were. | Same five logos. |

No other file is changed. No example diagram used the removed logos.

The remaining icons come from Tabler Icons (MIT), Simple Icons (CC0), Devicon (MIT) and log-z/logos (MIT), as upstream records per icon. Brand silhouettes remain their owners' trademarks.

## Getting a removed logo

Fetch it from upstream at the commit above (`references/primitive-icons.md` or `assets/icons.html`) only after checking the logo owner's license and trademark terms, or draw a labeled box instead.

## Updating

Copy the folder from upstream at a newer commit, remove again any icon whose source is not a library with clear redistribution terms (search for "Direct fetch" and "verify license"), and update the commit above.
- Added THIRD_PARTY_NOTICES.md with the MIT notices for the bundled Tabler Icons and Devicon SVGs, and a note on the CC0 Simple Icons logos.
