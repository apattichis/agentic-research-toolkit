# figures4papers Reference Index

> In ART, the files this index points to are not included: they are licensed CC BY-NC 4.0 by their authors. See `../assets/figures4papers/README.md` for where to get them. The index below is kept so the examples can be found upstream.

Use this file when a user asks for a `figures4papers` look, cites the older
`scientific-figure-making` skill, or needs a concrete Python/matplotlib reference.

Upstream, these third-party files live under `assets/figures4papers/` of the
nature-figure skill. In ART, get them separately (see the note above) and read
their license and `../assets/figures4papers/THIRD_PARTY_NOTICES.md` before
opening or adapting them. They are not covered by ART's MIT License.

## Use boundary

1. Study layout, palette, axes, legends, and export structure as reference patterns.
2. Reimplement with original code and the user's own data whenever the upstream
   license or written permission does not clearly authorize copying or modification.
3. Never reuse manuscript-specific labels, metric values, statistical results, or
   visual assets as placeholders for real evidence.
4. Record the external reference and implementation provenance in the internal QA
   record when it materially influenced the result.
5. Preserve the editable SVG/PDF/TIFF and source-data rules from `api.md` and
   `qa-contract.md`.

## Upstream project map

Paths below are relative to a separate checkout of the upstream examples, not to files shipped with ART.

| Project | Open when | Upstream path |
|---------|-----------|------------------|
| `figure_ImmunoStruct` | Method-comparison and ablation bars | `../assets/figures4papers/figure_ImmunoStruct/` |
| `figure_CellSpliceNet` | Compact benchmark and cross-species bars | `../assets/figures4papers/figure_CellSpliceNet/` |
| `figure_brainteaser` | Category, rewriting, and self-correction panels | `../assets/figures4papers/figure_brainteaser/` |
| `figure_VIGIL` | Radar, trend, ablation, and probability/manifold panels | `../assets/figures4papers/figure_VIGIL/` |
| `figure_ophthal_review` | Time trends and composition heatmaps | `../assets/figures4papers/figure_ophthal_review/` |
| `figure_RNAGenScape` | Heatmaps, optimization, manifold, and sweep plots | `../assets/figures4papers/figure_RNAGenScape/` |
| `figure_Dispersion` | Conceptual sphere and observation panels | `../assets/figures4papers/figure_Dispersion/` |
| `figure_Cflows` | Diffusion, trajectory, comparison, and ablation panels | `../assets/figures4papers/figure_Cflows/` |
| `figure_FPGM` | Frequency-prior or distribution-style motivation | `../assets/figures4papers/figure_FPGM/` |

## Prefer repository-owned implementation paths

When copying is not clearly authorized, route the pattern through the repository's
own material:

| Requested pattern | Open and use |
|-------------------|--------------|
| Grouped bars, ablation bars, shared legends | `tutorials.md`, `common-patterns.md` |
| Radar or polar comparison | `chart-types.md`, then implement with original code |
| Trends, sweeps, and reference baselines | `tutorials.md`, `chart-types.md` |
| Heatmap or annotated matrix | `tutorials.md`, `template-catalog.md` |
| Probability or manifold concept panel | `chart-types.md` |
| Submission typography, palette, and export | `api.md`, `design-theory.md` |
| CSV-driven reproducible plots | `template-catalog.md`, `scripts/plot_templates.py` |

## Upstream source

<https://github.com/ChenLiu-1996/figures4papers>

Check the current upstream license and obtain permission when required before
redistributing, modifying, or publishing derived materials.
