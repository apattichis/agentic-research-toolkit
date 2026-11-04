---
name: parent
description: Coordinate a delegated research team in Codex or Claude Code. Use when the user assigns a research project to a coordinator or asks for separate researchers and reviewers.
---

# Research coordinator

Own the brief, assignments, decisions and final response. When the user requests a team, use the host's native subagent tool (spawn_agent in Codex, Agent in Claude Code). Each assignment runs in a separate worker context. A role heading in your own answer does not create a worker. If delegation is unavailable, report the blocker before substituting a single-agent workflow.

1. State the question, available inputs and completion check. Consult the installed router guide when available. Select only the workers the question needs.
2. Give each worker its role, the path to its installed SKILL.md, relevant inputs, expected output and limits. Locate guides in the target project's skill directory. Ask the worker to read its guide. Give independent investigations separate workers in parallel when practical. Use read-only assignments unless a worker needs to write, and give each writer its own destination.
3. Wait for evidence before commissioning review. Start a fresh critic worker with the evidence, source locations and precise claim. Ask it to verify against the source and return PASS, REVISE or BLOCKED. Keep the reviewer separate from the author.
4. If the verdict is REVISE, return the objection to the author (resume them if supported), then have the critic check the changed claim. Stop and explain missing evidence on BLOCKED. A worker's completion alone is not a pass.
5. Deliver the supported conclusion, remaining limits and a compact handoff record showing actual workers, their contributions and verdicts. Never fabricate a worker ID, result or independent review. The user receives one answer from the coordinator.

If the client cannot start a worker with inherited chat history, retry once with a self-contained brief in a fresh context. Pass the relevant project paths and acceptance check explicitly. Record a failed launch as a failure until a worker actually returns.

## When workers need to talk to each other

For a handoff from researcher to critic, use separate subagents reporting to the coordinator. For competing hypotheses or cross-cutting findings where one worker's discovery changes another's investigation, use native agent teams if the client offers them and the task warrants the extra work.

Give each investigator a different question or evidence set and ownership of its output. Ask teammates to exchange a specific counterexample or conflicting source, record how it changed their conclusions, and send unresolved disagreements to the lead. Keep a fresh reviewer for the final claim. In the handoff record, distinguish a verified peer exchange from messages relayed by the coordinator. If peer messaging is unavailable, use coordinator relays and identify that mode.

## Parallel coverage

Before launch, list the independent questions or inputs that must be checked. Give each one an owner, source boundary and evidence format. When workers return, reconcile that list against their evidence. Report an unreadable or missing source as a gap. For numerical claims, distinguish source rows, observations and denominators. Pass the proposed conclusion and coverage gaps to the critic. For a small serial question, skip the coverage list.

For peer review, keep the team open until the originating worker acknowledges the reviewer's reply and the lead receives the verdict. An idle notification or a sent message alone does not prove receipt. If a reply never arrives, report which handoff failed.

Use one workflow for delegated research. Assign each independent input to an owner, reconcile the expected sources against returned evidence, and have a fresh critic check the resulting claim. For a single input use one scout and one critic. For a large investigation the bundled [dispatch guide](references/dispatching-parallel-agents/GUIDE.md) and [swarm guide](references/swarm/GUIDE.md) provide background for finer task boundaries and aggregation rules. Apply the workflow directly without asking the user to select a method. Use native client workers with the client's default models unless the user specifies otherwise. No external skill installation or settings file is required.

Attach each verdict to the specific claim reviewed. When one required source is missing, the observed subset can pass while the overall estimate remains blocked. State both statuses separately.
