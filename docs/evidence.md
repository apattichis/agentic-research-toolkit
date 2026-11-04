# Evidence

How the skill choices in ART were tested, and what the results were. All runs took place on 3 and 4 November 2026 on one Windows 11 machine, with Claude Code (Sonnet workers) and Codex (gpt-6.1-sol). The sample report, figures and data used as inputs are illustrative synthetic data, made only to test the skills.

## Method

- Each candidate skill ran on the same task, with the same inputs and budget, in its own folder, and was instructed to read nothing outside it. Session logs confirmed this for the ideation critic and every review run; the figure and slide runs were not audited.
- Contenders ran twice each in Codex (three times for ideation, in Claude Code).
- Critics on the other platform scored the outputs blind, under shuffled labels; the mapping stayed with the coordinator.
- A challenger replaces the current choice only if it wins clearly.

## Results

| Stage | Chosen skill | Challengers | Result |
| --- | --- | --- | --- |
| Research ideation (18 ideas, scored out of 25) | No skill (baseline): average 18.33 | evoskills `research-ideation`: average 18.56 | Similar averages over three runs each; equivalence was not established. The skill reached higher peaks (21 against 19) but also produced the weakest idea, so it joins the idea routine as one worker. |
| Publication figures (out of 25) | `nature-figure`: 23.25 | K-Dense `scientific-visualization`: 23.25; evoskills `paper-figures`: 21.00 | A tie at the top. Neither critic reported a data error in any figure. |
| Paper review (10 planted errors) | `critic`: review quality 4.50 out of 5 | K-Dense `peer-review`: 3.75; evoskills `paper-review`: 3.75 | The graders credited every review with all 10 planted errors and found no false claims, so quality decided it. For one error, a wrong table cell, every review blamed the text rather than the cell. |
| Slides and talks (out of 25) | `quarto-authoring`: 23.75 | scientific-writer `scientific-slides`: 22.75; evoskills `academic-slides`: 20.25 | Best mean. The critics found no number that contradicted the source report; one deck had three wording problems. One idea was adopted from the runner-up: one figure panel per slide. |

An earlier single-run ideation trial also compared claude-scholar `research-ideation` and Orchestra `brainstorming-research-ideas`. Neither clearly beat working without a skill, and every method converged on the same few ideas.

## Install from the link

Fresh sessions of Claude Code and Codex, each in an empty folder, were given the repository link and a one-line request to set it up with all skills, the three servers and the rules. They used the first commit on main (bb5bb39), which came before the `--version` option. Both cloned the repository, ran the installer, and ended with all 18 skills, the arXiv, Firecrawl and Playwright servers, and the rules files. Each then made a real arXiv call that returned the right title, through arXiv tools its session already had. On the test machine a full install took under a second per client (0.9 s for Claude Code, 0.7 s for Codex), and the agent-led setups finished within minutes.

## Two-client check in a working project

In a project already set up with ART, fresh sessions in both clients ran the same six checks: the rules loaded, the skills listed, and one real call each to arXiv, Firecrawl, the Playwright browser and Zotero (read only).

| Check | Claude Code | Codex |
| --- | --- | --- |
| Rules loaded | PASS | PASS |
| Skills | PASS (all skills listed) | PASS (`nature-shared` is not listed at startup; `nature-figure` still reads its files) |
| arXiv | PASS | PASS |
| Firecrawl | PASS | PASS |
| Playwright | PASS | PASS |
| Zotero, read only | PASS | PASS |

Delegation was tested in both directions: Claude Code to Codex and Codex to Claude Code. The checks also found one real problem: a fresh session's multi-line brief, passed to Codex as an argument, reached Codex as its first line only, while the same brief passed on stdin worked. The rules now pass briefs on stdin.

## Limits of this evidence

- Two runs per skill (three for ideation) and one model per side; small gaps cannot be separated from run-to-run variation.
- The review test could not separate the skills on detection: the graders credited every reviewer with all ten planted errors.
- The evoskills ideation skill ran without its own paper-search scripts and with its refinement condensed.
- The literature-search, survey, experiment, writing, rebuttal, memory and schematic stages have not been trialled yet.
