"""Install a selection of agent skills and MCP servers. Requires Python 3.11+."""
import argparse
import json
import os
from pathlib import Path
import shutil
from tempfile import NamedTemporaryFile
from uuid import uuid4
import tomllib

VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parent
SKILLS = {p.parent.name: p.parent for p in sorted(ROOT.glob("skills/*/*/SKILL.md"))}
SERVERS = json.loads((ROOT / "mcp/servers.json").read_text())["mcpServers"]
DEPENDS = json.loads((ROOT / "skills/dependencies.json").read_text())
CLIENTS = {
    "codex": (".agents/skills", ".codex/config.toml"),
    "claude": (".claude/skills", ".mcp.json"),
    "cursor": (".cursor/skills", ".cursor/mcp.json"),
}
# Project rules: every client reads AGENTS.md; Claude Code reaches it through CLAUDE.md.
RULES = {"codex": ["AGENTS.md"], "claude": ["AGENTS.md", "CLAUDE.md"], "cursor": ["AGENTS.md"]}


def selected(value, available):
    if value == "*":
        return list(available)
    if not isinstance(value, list) or not all(isinstance(x, str) and x in available for x in value):
        raise ValueError(f"Choose names from {', '.join(available)}, or use the string '*'")
    return list(dict.fromkeys(value))


def with_dependencies(names):
    return list(dict.fromkeys(d for name in names for d in [*DEPENDS.get(name, []), name]))


def files_in(folder):
    return {p.relative_to(folder): p.read_bytes() for p in folder.rglob("*") if p.is_file()}


def merged_config(client, original, names):
    if client == "codex":
        template = (ROOT / "mcp/codex.toml").read_text()
        catalog = tomllib.loads(template)["mcp_servers"]
        data = tomllib.loads(original)
        key = "mcp_servers"
    else:
        catalog = SERVERS
        data = json.loads(original) if original.strip() else {}
        key = "mcpServers"
    entries = data.setdefault(key, {})
    missing = []
    for name in names:
        if name not in entries:
            missing.append(name)
        elif entries[name] != catalog[name]:
            raise ValueError(f"Existing settings for {name} differ. Review them before installation.")
    if not missing:
        return original
    entries.update({name: catalog[name] for name in missing})
    if client != "codex":
        return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    blocks = template.strip().split("\n\n")
    additions = [b for b in blocks if b.splitlines()[0] in {f"[mcp_servers.{n}]" for n in missing}]
    output = (original.rstrip() + "\n\n" if original.strip() else "") + "\n\n".join(additions) + "\n"
    if tomllib.loads(output) != data:
        raise ValueError("Cannot safely extend this TOML configuration.")
    return output


def install(args, skills, servers, rules=False):
    project = args.project.resolve(strict=True)
    if not project.is_dir():
        raise ValueError("Choose an existing project directory.")
    skill_dir, config = CLIENTS[args.client]
    pending = []
    for name in skills:
        src, dest = SKILLS[name], project / skill_dir / name
        if dest.exists():
            if not dest.is_dir() or files_in(src) != files_in(dest):
                raise ValueError(f"Existing skill differs at {dest}. Review it before installation.")
        else:
            pending.append((src, dest))
    rule_files = RULES[args.client] if rules else []
    pending_rules = []
    for name in rule_files:
        src, dest = ROOT / "templates" / name, project / name
        if dest.exists():
            if dest.read_bytes() != src.read_bytes():
                raise ValueError(f"Existing {name} differs at {dest}. Review it before installation.")
        else:
            pending_rules.append((src, dest))
    path = project / config
    original = path.read_text(encoding="utf-8-sig") if servers and path.exists() else ""
    output = merged_config(args.client, original, servers) if servers else original
    print(f"Project: {project}\nClient: {args.client}\nSkills: {', '.join(skills) or 'none'}\nMCP: {', '.join(servers) or 'none'}\nRules: {', '.join(rule_files) or 'none'}")
    if args.dry_run:
        return
    for src, dest in pending_rules:
        shutil.copyfile(src, dest)
    for src, dest in pending:
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Inherit project permissions. Private temp directories on Windows
        # prevent sandboxed project agents from reading the installed skill.
        staged = dest.parent / f".{src.name}-{uuid4().hex}"
        try:
            shutil.copytree(src, staged)
            staged.rename(dest)
        finally:
            if staged.exists():
                shutil.rmtree(staged)
    if output != original:
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
            tmp.write(output)
        staged = Path(tmp.name)
        try:
            if path.exists() and path.read_text(encoding="utf-8-sig") != original:
                raise ValueError("Configuration changed during installation. Run again.")
            os.replace(staged, path)
        finally:
            staged.unlink(missing_ok=True)
    print("Selected items are installed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"ART {VERSION}")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--client", choices=CLIENTS)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--skill", choices=SKILLS, action="append", default=[])
    parser.add_argument("--server", choices=SERVERS, action="append", default=[])
    parser.add_argument("--mcp", action="store_true", help="select all MCP servers")
    parser.add_argument("--profile", type=Path, help="project selection JSON")
    parser.add_argument("--all", action="store_true", help="select every skill and all MCP servers")
    parser.add_argument("--rules", action="store_true", help="add the project rules (AGENTS.md, and CLAUDE.md for Claude Code)")
    parser.add_argument("--dry-run", action="store_true", help="check without writing")
    args = parser.parse_args()
    if args.list:
        for name, path in SKILLS.items():
            needs = f" (installs with {', '.join(DEPENDS[name])})" if name in DEPENDS else ""
            print(f"{path.parent.name}/{name}{needs}")
        print("MCP:", ", ".join(SERVERS))
        return
    if not args.client or not args.project:
        parser.error("supply --client and --project")
    try:
        profile = json.loads(args.profile.read_text(encoding="utf-8-sig")) if args.profile else {}
        if not isinstance(profile, dict) or profile.keys() - {"skills", "mcp", "rules"}:
            raise ValueError("A profile accepts only skills, mcp and rules fields.")
        if not isinstance(profile.get("rules", False), bool):
            raise ValueError("The rules field must be true or false.")
        skills = selected(profile.get("skills", []), SKILLS) + args.skill
        servers = selected(profile.get("mcp", []), SERVERS) + args.server
        skills = with_dependencies(list(SKILLS) if args.all else skills)
        servers = list(SERVERS) if args.all or args.mcp else list(dict.fromkeys(servers))
        rules = args.rules or profile.get("rules", False)
        if not skills and not servers and not rules:
            raise ValueError("Select a profile, a skill, a server, --rules, or --all.")
        install(args, skills, servers, rules)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
