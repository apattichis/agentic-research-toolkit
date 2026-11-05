"""Install a selection of agent skills and MCP servers. Requires Python 3.11+."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
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
# Worker output and browser snapshots, which the rules say git ignores.
IGNORED = [".agent-runs/", ".playwright-mcp/"]
# Paths git is asked about after writing, to confirm both folders and files in them are ignored.
VERIFY = [".agent-runs/", ".agent-runs/report.md", ".agent-runs/review.md", ".agent-runs/nested/notes.md",
          ".playwright-mcp/", ".playwright-mcp/page.yml"]
# SHA-256 of every released version of the toolkit's own root AGENTS.md and CLAUDE.md, with
# CRLF read as LF. A repository made with "Use this template" starts with these files, and
# --rules replaces an untouched copy with the rules template; any other content is kept.
# When a root copy changes, add its hash here and a copy to tests/fixtures/bootstrap/;
# tests/test_install.py fails until you do.
BOOTSTRAP = {
    "AGENTS.md": {
        "9543ffd8a3b7b4ee7641f6bff05477f271f4978db3baf143cd8856f364edcdee",
        "3971b2538a9dd90e344e252b2ba3a79d23ad25553b0168df7f9f9eb287ccd38d",
        "57f0b2d3ce54abd4f556fe9254f6a43c18cd269f54a5713fc6e97c2a9327f3ba",
    },
    "CLAUDE.md": {
        "336cc4fbf19beaada7ccf9986414fa91851a8d7a07dfb3ccbe800a69eed0ab49",
    },
}


class PartialInstall(Exception):
    """A write failed after earlier writes succeeded."""


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


def normalised(data):
    return data.replace(b"\r\n", b"\n")


def digest(data):
    return hashlib.sha256(normalised(data)).hexdigest()


def is_bootstrap(name, data):
    """True when data is an untouched copy of a recorded version of the toolkit's root file."""
    return digest(data) in BOOTSTRAP.get(name, ())


def is_link(path):
    """True for a symbolic link, or a Windows junction (mount point reparse tag)."""
    try:
        info = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0) == 0xA0000003


def check_inside(project, dest):
    """Return where dest really is, refusing a broken link or a link that leads outside the project.

    The installer then writes to that real location, so it never creates files through a link
    inside the project (some sandboxes refuse that even when the target is allowed).
    """
    current = project
    for part in dest.relative_to(project).parts:
        current = current / part
        if is_link(current) and not current.exists():
            raise ValueError(f"{current} is a broken link. Fix or remove it before installation.")
    resolved = dest.resolve()
    if not resolved.is_relative_to(project):
        raise ValueError(f"{dest} leads outside the project, to {resolved}. Remove the link before installation.")
    return resolved


def server_table(data, key, path):
    if not isinstance(data, dict):
        raise ValueError(f"{path} must hold an object at the top level.")
    entries = data.setdefault(key, {})
    if not isinstance(entries, dict):
        raise ValueError(f"{key} in {path} must be a table of servers, not {type(entries).__name__}.")
    for name, entry in entries.items():
        if not isinstance(entry, dict):
            raise ValueError(f"Server '{name}' in {path} must be a table of settings. Fix it before installation.")
    return entries


def merged_config(client, original, names, path):
    if client == "codex":
        template = (ROOT / "mcp/codex.toml").read_text()
        catalog = tomllib.loads(template)["mcp_servers"]
        key = "mcp_servers"
        try:
            data = tomllib.loads(original)
        except tomllib.TOMLDecodeError as error:
            raise ValueError(f"Cannot read {path} as TOML: {error}") from None
    else:
        catalog = SERVERS
        key = "mcpServers"
        try:
            data = json.loads(original) if original.strip() else {}
        except json.JSONDecodeError as error:
            raise ValueError(f"Cannot read {path} as JSON: {error}") from None
    entries = server_table(data, key, path)
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
    try:
        safe = tomllib.loads(output) == data
    except tomllib.TOMLDecodeError:
        safe = False
    if not safe:
        raise ValueError(f"Cannot safely extend the TOML configuration at {path}.")
    return output


def git_root(project):
    """The root of the git work tree that holds project, or None outside git or without git."""
    git = shutil.which("git")
    if not git:
        return None
    try:
        result = subprocess.run([git, "-C", str(project), "rev-parse", "--show-toplevel"], capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    top = result.stdout.decode("utf-8", "replace").strip()
    return Path(top) if result.returncode == 0 and top else None


def git_verify(project):
    """Ask git about VERIFY: (True, []) if it ignores them all, (False, kept paths), or (None, reason)."""
    command = [shutil.which("git") or "git", "-C", str(project), "check-ignore", "-v", "-n", "-z", "--no-index", "--stdin"]
    try:
        result = subprocess.run(command, input="\0".join(VERIFY).encode() + b"\0", capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None, "git check-ignore timed out"
    except (OSError, subprocess.SubprocessError) as error:
        return None, f"git check-ignore did not run: {error}"
    fields = result.stdout.split(b"\0")[:-1]
    if result.returncode not in (0, 1) or len(fields) != 4 * len(VERIFY):
        detail = result.stderr.decode("utf-8", "replace").strip().splitlines()
        return None, f"git check-ignore failed{': ' + detail[-1] if detail else ''}"
    # Each record is source, line, pattern, path; no source or a ! pattern means git keeps it.
    kept = [name for index, name in enumerate(VERIFY)
            if not fields[4 * index] or fields[4 * index + 2].startswith(b"!")]
    return not kept, kept


def git_tracked(project):
    """Files git already tracks in the IGNORED folders, which no .gitignore line untracks; None if git fails."""
    command = [shutil.which("git") or "git", "-C", str(project), "ls-files", "-z", "--", *(e.rstrip("/") for e in IGNORED)]
    try:
        result = subprocess.run(command, capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return [name.decode("utf-8", "replace") for name in result.stdout.split(b"\0") if name]


def ignore_update(path):
    """Plan the .gitignore at path: (current bytes or None, new contents, added entries).

    Git never re-includes anything inside a folder that a rule excludes as a whole, and only
    lines starting with ! re-include. So each IGNORED folder is safe exactly when its own line
    (.agent-runs/ or .playwright-mcp/) comes after the last ! line; otherwise it goes at the end.
    This needs no git and no reading of patterns.
    """
    if path.exists() and not path.is_file():
        raise ValueError(f"{path} is not a file.")
    original = path.read_bytes() if path.exists() else None
    head = original or b""
    # Split as git does: on \n, dropping one \r before it. Spaces and tabs stay part of the line.
    lines = [line.removesuffix("\r") for line in head.decode("utf-8", errors="replace").split("\n")]
    last_negation = max((index for index, line in enumerate(lines) if line.startswith("!")), default=-1)
    last_rule = {entry: max((index for index, line in enumerate(lines) if line == entry), default=-1) for entry in IGNORED}
    missing = [entry for entry in IGNORED if last_rule[entry] <= last_negation]
    if not missing:
        return original, head, []
    newline = b"\r\n" if b"\r\n" in head else b"\n"
    if head and not head.endswith(b"\n"):
        head += newline
    if head.strip():
        head += newline
    block = ["# Agent run output and browser snapshots", *missing]
    return original, head + newline.join(line.encode() for line in block) + newline, missing


def write_file(dest, data, expected):
    """Write data to dest in one step, provided dest still holds expected (None: absent)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    staged = dest.parent / f".{dest.name}-{uuid4().hex}"
    try:
        with open(staged, "xb") as handle:
            handle.write(data)
        current = dest.read_bytes() if dest.exists() else None
        if current != expected:
            raise ValueError(f"{dest} changed during installation. Run again.")
        if current is not None:
            shutil.copymode(dest, staged)
        os.replace(staged, dest)
    finally:
        staged.unlink(missing_ok=True)


def copy_skill(src, dest):
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


def install(args, skills, servers, rules=False):
    project = args.project.resolve(strict=True)
    if not project.is_dir():
        raise ValueError("Choose an existing project directory.")
    skill_dir, config = CLIENTS[args.client]
    rule_files = RULES[args.client] if rules else []
    # Every write stays inside the project: no link may lead elsewhere or nowhere. Writes go to
    # each destination's real location, so an allowed link inside the project is written through.
    skill_dests = {name: check_inside(project, project / skill_dir / name) for name in skills}
    rule_dests = {name: check_inside(project, project / name) for name in rule_files}
    path = check_inside(project, project / config) if servers else project / config
    ignore_path = check_inside(project, project / ".gitignore")
    pending = []
    for name in skills:
        src, dest = SKILLS[name], skill_dests[name]
        if dest.exists():
            if not dest.is_dir() or files_in(src) != files_in(dest):
                raise ValueError(f"Existing skill differs at {dest}. Review it before installation.")
        else:
            pending.append((src, dest))
    pending_rules, rule_notes = [], []
    for name in rule_files:
        src, dest = ROOT / "templates" / name, rule_dests[name]
        if not dest.exists():
            pending_rules.append((src, dest, None))
            rule_notes.append(name)
            continue
        current = dest.read_bytes() if dest.is_file() else None
        if current is not None and normalised(current) == normalised(src.read_bytes()):
            rule_notes.append(f"{name} (already installed)")
        elif current is not None and is_bootstrap(name, current):
            pending_rules.append((src, dest, current))
            rule_notes.append(f"{name} (replaces the toolkit's own {name} from the template)")
        else:
            raise ValueError(f"Existing {name} differs at {dest}. Review it before installation.")
    original_bytes = path.read_bytes() if servers and path.exists() else None
    try:
        original = original_bytes.decode("utf-8-sig") if original_bytes is not None else ""
    except UnicodeDecodeError:
        raise ValueError(f"Cannot read {path} as UTF-8 text.") from None
    output = merged_config(args.client, original, servers, path) if servers else original
    ignore_bytes, ignore_output, ignore_added = ignore_update(ignore_path)
    ignore_note = f"add {', '.join(ignore_added)}" if ignore_added else f"already ignores {' and '.join(IGNORED)}"
    print(
        f"Project: {project}\nClient: {args.client}\nSkills: {', '.join(skills) or 'none'}\n"
        f"MCP: {', '.join(servers) or 'none'}\nRules: {', '.join(rule_notes) or 'none'}\n"
        f"Gitignore: {ignore_note}"
    )
    if args.dry_run:
        print("Dry run: nothing was written.")
        return
    steps = [(dest.name, lambda s=src, d=dest, e=expected: write_file(d, s.read_bytes(), e))
             for src, dest, expected in pending_rules]
    steps += [(f"skill {src.name}", lambda s=src, d=dest: copy_skill(s, d)) for src, dest in pending]
    if output != original:
        steps.append((f"MCP settings in {config}", lambda: write_file(path, output.encode("utf-8"), original_bytes)))
    if ignore_added:
        steps.append((".gitignore entries", lambda: write_file(ignore_path, ignore_output, ignore_bytes)))
    for done, (label, step) in enumerate(steps):
        try:
            step()
        except (OSError, ValueError) as error:
            written = ", ".join(name for name, _ in steps[:done]) or "nothing"
            raise PartialInstall(
                f"Installation stopped while writing {label}: {error}\n"
                f"Written before the error: {written}\n"
                f"Not written: {', '.join(name for name, _ in steps[done:])}\n"
                "Fix the cause and run the same command again; it keeps what was written and adds the rest."
            ) from None
    if ignore_added:
        print(f"Added to .gitignore: {', '.join(ignore_added)}")
    if git_root(project):
        ignored, detail = git_verify(project)
        tracked = git_tracked(project)
        if ignored is None:
            print(f"Warning: could not verify .gitignore because {detail}. "
                  "Check by hand with: git check-ignore -v .agent-runs/report.md .playwright-mcp/page.yml")
        elif not ignored:
            print(f"Warning: git does not ignore {', '.join(detail)}. Check the project's ignore files.")
        if tracked is None:
            print("Warning: could not list files git already tracks. Check by hand with: git ls-files -- .agent-runs .playwright-mcp")
        elif tracked:
            folders = [e.rstrip("/") for e in IGNORED if any(name.startswith(e) or name == e.rstrip("/") for name in tracked)]
            print(f"Warning: git already tracks {len(tracked)} file{'s' if len(tracked) != 1 else ''} in "
                  f"{' and '.join(folders)}, and .gitignore does not change that. To stop tracking them and keep "
                  f"the files, run: git rm -r --cached {' '.join(folders)}")
        if ignored and tracked == []:
            print(f"Checked with git check-ignore: {' and '.join(IGNORED)} are ignored.")
    print("Selected items are installed.")


def main():
    for stream in (sys.stdout, sys.stderr):
        # Print project paths that the console encoding cannot show instead of failing.
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
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
    except PartialInstall as error:
        parser.exit(1, f"{parser.prog}: error: {error}\n")
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
