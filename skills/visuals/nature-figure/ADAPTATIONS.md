# ART adaptations

- Upstream: [yuan1z0825/nature-skills](https://github.com/yuan1z0825/nature-skills), skill `nature-figure`, pinned at commit `69817e4`. Its companion `nature-shared` is bundled unchanged.
- License: Apache-2.0 (`LICENSE` in this folder, copied from upstream). Under section 4(b) of that license, this file and the "ART adaptation" comments in the changed files are the notice that ART changed them.

## Changes from upstream

| File | Change | Why |
| --- | --- | --- |
| `assets/figures4papers/` | Removed the third-party figures4papers reference scripts and images. Added `README.md` saying where to get them and a status note in `THIRD_PARTY_NOTICES.md`. `references/demos.md`, `README.md` and `README_EN.md` point to that README instead of the removed files. | figures4papers is licensed CC BY-NC 4.0, which does not fit ART's commercial-use-friendly license. |
| `scripts/generate_openrouter_schematic.py` | URL downloads are disabled. The script saves only image bytes returned in the response (`data[].b64_json`). A returned `data[].url` is never fetched: it is recorded under `unfetched_image_urls` in `<basename>_request_metadata.json` and printed, and the script exits with an error when no image bytes came back. The upstream `_require_downloadable_url` check and its `ipaddress` and `urllib.parse` imports are removed. | Upstream checked only literal IP addresses and the name `localhost` before downloading a response-supplied URL. A hostname resolving to a private address, or a redirect, passed that check, so a hostile or compromised response could make the script request local or internal services. Disabling the download is simpler and safer than validating every resolved address and redirect. |
| `tests/test_schematic_url_safety.py` | Tests now check that `file:`, loopback, link-local and ordinary HTTPS URLs are never fetched, that returned bytes are still saved next to a recorded URL, and that the metadata lists each unfetched URL. The upstream test that expected an HTTPS download is replaced. | Covers the new behavior, including the hostname case the upstream tests missed. |
| `references/openrouter-image-generation.md` | Added one paragraph describing the disabled URL download. | Keeps the reference in line with the script. |

Reference images passed with `--reference-image <url>` are unchanged: the URL is sent to the images API, not fetched by the script.

## Updating

Copy the folder from upstream at a newer commit, reapply the changes above (leave out figures4papers again and keep the response-URL download disabled), run `python -I -m pytest tests -q` in this folder, and update the commit above.
