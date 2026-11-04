# Workflows

Part of [ART: Agentic Research Toolkit](../README.md).

## A small research workflow

For a paper question that needs a short answer, select the `scout` skill. Ask the agent to read its guide before starting. For a reviewed answer, also select Critic and give it the draft and the evidence cards.

1. Frame one question that a primary source can answer. Use arXiv to identify the paper and read the relevant section.
2. Use Firecrawl to locate the publisher's copy and compare the relevant passage. Use Playwright when a page needs interaction or you want to check what a reader sees. Two copies of the same paper verify the reading, but count as one source.
3. Record the claim, the section that supports it, a link and any qualification. Check what the source actually says before drafting the answer.
4. Write the answer in plain language, naming the evidence for each point. Keep the evidence and any setup issues in the project note.
In unattended Codex sessions, browser navigation may require interactive approval. If approval is unavailable, mark the browser check as skipped and name the evidence actually used. For a task that requires browser verification, run that step in an interactive session.

## Delegate a research project

Install the [research team profile](../profiles/research-team.json) with Python 3.11 or later. From the toolkit checkout run the following command, replacing the project path and choosing `codex` or `claude`.

```sh
python install.py --project "/path/to/project" --client codex --profile profiles/research-team.json
```

Open the target project in the chosen client and give the coordinator one brief:

> Use the parent skill to coordinate a delegated research team. Investigate [question] using [sources]. Return a short answer with the evidence and a separate critic's verdict.

The profile supplies one coordinator and four supporting role guides. The client supplies actual subagents. Codex needs its multi-agent capability enabled; Claude Code needs the Agent tool available. The coordinator chooses assignments and launches workers; installing a profile by itself starts no agents. The critic gets the author's result and checks it in its own context. Check the client's worker activity or tool log to verify delegation. The profile works with local sources. For web research, add the desired server flags when installing, and check that the assigned worker can access the tool.

Model selection is separate from role assignment. This profile sets no model names or reasoning levels. Each client uses its own worker defaults unless you configure an override. A scout and critic may use the same model in separate contexts. When recording a handoff, include the model only if the client reports it.

### Claude Code agent teams

For a researcher-to-critic handoff, the lead can dispatch ordinary subagents. Choose Claude Code's native agent teams when researchers need to challenge one another directly. Ask each investigator to own a different hypothesis and send the other a specific item of evidence to check. To verify that a team actually formed, check for a teammate-to-teammate message and its reply alongside the final verdict. A list of named workers alone cannot establish this.

Agent teams must be available and enabled in the Claude Code session. See [Claude Code agent teams](https://code.claude.com/docs/en/agent-teams) for setup. The coordinator's division of work also draws on [Anthropic's research system write-up](https://www.anthropic.com/research/multi-agent-research-system) and the [Superpowers parallel dispatch skill](https://github.com/obra/superpowers/blob/main/skills/dispatching-parallel-agents/SKILL.md).

### Why there is one coordinator

Give the parent coordinator the question and desired outcome. It assigns independent inputs to separate workers, checks that all expected evidence came back, and sends the proposed conclusion to a fresh critic. When teammates need to challenge each other directly, it uses peer messaging where available. The researcher does not select a dispatch strategy.

We compared the existing coordinator alone, with Superpowers dispatch, with pstack swarm, and with both on the same two-site task in Claude Code. All four reached 104/125 and rejected the incorrect claim about both sites. The combination made source coverage explicit; one report also confused rows with observations. The default therefore combines independent assignments and coverage reconciliation with a final check of units and claim scope. A missing-source test withheld the unsupported overall estimate. Codex also ran the combination with two scouts and a separate critic. These small trials establish functionality, not a general speed or accuracy advantage.

The coordinator bundles the [Superpowers dispatch guide](../skills/research/parent/references/dispatching-parallel-agents/GUIDE.md) and [pstack swarm guide](../skills/research/parent/references/swarm/GUIDE.md) as internal references, each with its MIT license. [Superpowers source revision](https://github.com/obra/superpowers/tree/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/dispatching-parallel-agents) · [pstack source revision](https://github.com/backnotprop/pstack/tree/6c75f4e67546c2ddbf9634734c1e3ebbea34861a/skills/swarm)
