"""Installer regression tests. Run from the repository root: python -I -m pytest tests -q"""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
_spec = importlib.util.spec_from_file_location("art_install", ROOT / "install.py")
art = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(art)

CLIENTS = list(art.CLIENTS)
TEMPLATE_AGENTS = (ROOT / "templates/AGENTS.md").read_bytes()
# Immutable copies of every recorded version of the toolkit's root AGENTS.md and CLAUDE.md.
BOOTSTRAP_FILES = sorted((FIXTURES / "bootstrap").glob("*.md"))
LATEST_AGENTS = FIXTURES / "bootstrap/AGENTS.75d0ae9.md"
BOOTSTRAP_CLAUDE = FIXTURES / "bootstrap/CLAUDE.bb5bb39.md"
HAS_GIT = shutil.which("git") is not None


def run(capsys, monkeypatch, *args):
    """Run the installer in this process and return (exit code, stdout, stderr)."""
    monkeypatch.setattr(sys, "argv", ["install.py", *map(str, args)])
    try:
        art.main()
        code = 0
    except SystemExit as stop:
        code = stop.code if isinstance(stop.code, int) else 1
    out, err = capsys.readouterr()
    return code, out, err


def run_cli(*args, cwd=None, script=ROOT / "install.py"):
    """Run the installer as a separate process, as a user would."""
    result = subprocess.run([sys.executable, "-I", str(script), *map(str, args)], cwd=cwd, capture_output=True)
    return result.returncode, result.stdout.decode("utf-8", "replace"), result.stderr.decode("utf-8", "replace")


def snapshot(folder):
    return {p.relative_to(folder): p.read_bytes() if p.is_file() else None for p in sorted(folder.rglob("*"))}


def swap_line_endings(data):
    lf = data.replace(b"\r\n", b"\n")
    return lf.replace(b"\n", b"\r\n") if lf == data else lf


def staged_leftovers(folder):
    """Staging files and folders the installer names .<name>-<32 hex digits>."""
    return [p.name for p in folder.rglob(".*") if re.fullmatch(r"\..+-[0-9a-f]{32}", p.name)]


def git(project, *args):
    return subprocess.run(["git", "-C", str(project), *args], capture_output=True)


# Files a research run could leave behind, including some the installer never probes.
OUTPUT_FILES = [".agent-runs/report.md", ".agent-runs/review.md", ".agent-runs/nested/notes.md",
                ".agent-runs/critic/verdict.json", ".agent-runs/keep.txt", ".playwright-mcp/page.yml",
                ".playwright-mcp/shot.png", ".playwright-mcp/deep/trace.zip"]


def git_would_track(project):
    """Ground truth: the run output files git status offers to commit, created and then removed."""
    created = [project / name for name in OUTPUT_FILES]
    for path in created:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("output")
    try:
        result = git(project, "status", "--porcelain", "--untracked-files=all", "--", ".agent-runs", ".playwright-mcp")
        assert result.returncode == 0, result.stderr
        return result.stdout.decode().splitlines()
    finally:
        for folder in (".agent-runs", ".playwright-mcp"):
            shutil.rmtree(project / folder)


def make_dir_link(link, target):
    """A junction on Windows (no extra rights needed), a symbolic link elsewhere. Never skipped."""
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)
    assert art.is_link(link)


@pytest.fixture
def project(tmp_path):
    folder = tmp_path / "project"
    folder.mkdir()
    return folder


@pytest.fixture
def no_git(monkeypatch):
    """Read .gitignore rules directly, as for a project that is not a git work tree."""
    monkeypatch.setattr(art, "git_root", lambda project: None)


def skill_path(project, client, name):
    return project / art.CLIENTS[client][0] / name


def servers_in(project, client):
    config = project / art.CLIENTS[client][1]
    if client == "codex":
        return tomllib.loads(config.read_text(encoding="utf-8"))["mcp_servers"]
    return json.loads(config.read_text(encoding="utf-8"))["mcpServers"]


def catalog(client):
    return tomllib.loads((ROOT / "mcp/codex.toml").read_text())["mcp_servers"] if client == "codex" else art.SERVERS


def test_version():
    code, out, _ = run_cli("--version")
    assert code == 0
    assert out.strip() == f"ART {art.VERSION}"


@pytest.mark.parametrize("client", CLIENTS)
def test_fresh_install(capsys, monkeypatch, project, client):
    code, out, err = run(capsys, monkeypatch, "--client", client, "--project", project,
                         "--skill", "scout", "--skill", "critic", "--mcp", "--rules")
    assert code == 0, err
    assert "Selected items are installed." in out
    for name in ("scout", "critic"):
        assert art.files_in(skill_path(project, client, name)) == art.files_in(art.SKILLS[name])
    assert servers_in(project, client) == catalog(client)
    assert (project / "AGENTS.md").read_bytes() == TEMPLATE_AGENTS
    assert (project / "CLAUDE.md").exists() == (client == "claude")
    assert (project / ".gitignore").read_text().splitlines()[-2:] == art.IGNORED


@pytest.mark.parametrize("client", CLIENTS)
def test_unchanged_rerun(capsys, monkeypatch, project, client):
    args = ("--client", client, "--project", project, "--skill", "scout", "--mcp", "--rules")
    assert run(capsys, monkeypatch, *args)[0] == 0
    before = snapshot(project)
    code, out, err = run(capsys, monkeypatch, *args)
    assert code == 0, err
    assert "already ignores" in out
    assert snapshot(project) == before


def test_modified_skill_refused(capsys, monkeypatch, project):
    args = ("--client", "claude", "--project", project, "--skill", "scout")
    assert run(capsys, monkeypatch, *args)[0] == 0
    skill_file = skill_path(project, "claude", "scout") / "SKILL.md"
    skill_file.write_bytes(skill_file.read_bytes() + b"\nLocal note.\n")
    edited = skill_file.read_bytes()
    code, _, err = run(capsys, monkeypatch, *args)
    assert code == 2
    assert "Existing skill differs" in err
    assert skill_file.read_bytes() == edited


def test_differing_server_settings_refused(capsys, monkeypatch, project):
    config = project / ".mcp.json"
    config.write_text(json.dumps({"mcpServers": {"arxiv": {"type": "http", "url": "https://example.com/mcp"}}}))
    before = config.read_bytes()
    code, _, err = run(capsys, monkeypatch, "--client", "claude", "--project", project, "--server", "arxiv")
    assert code == 2
    assert "Existing settings for arxiv differ" in err
    assert config.read_bytes() == before


@pytest.mark.parametrize("client", ["claude", "cursor"])
def test_json_merge_keeps_unrelated_settings(capsys, monkeypatch, project, client):
    config = project / art.CLIENTS[client][1]
    config.parent.mkdir(parents=True, exist_ok=True)
    local = {"command": "db-mcp", "args": ["--read-only"], "env": {"DB": "notes"}}
    config.write_text(json.dumps({"theme": "dark", "mcpServers": {"local-db": local, "arxiv": art.SERVERS["arxiv"]}}))
    args = ("--client", client, "--project", project, "--mcp")
    code, _, err = run(capsys, monkeypatch, *args)
    assert code == 0, err
    data = json.loads(config.read_text(encoding="utf-8"))
    assert data["theme"] == "dark"
    assert data["mcpServers"] == {"local-db": local, **art.SERVERS}
    before = config.read_bytes()
    assert run(capsys, monkeypatch, *args)[0] == 0
    assert config.read_bytes() == before


def test_toml_merge_keeps_unrelated_settings(capsys, monkeypatch, project):
    config = project / ".codex/config.toml"
    config.parent.mkdir()
    original = (
        'model = "gpt-5"\n\n[mcp_servers.local-db]\ncommand = "db-mcp"\nargs = ["--read-only"]\n\n'
        "[projects.'/work/study']\ntrust_level = \"trusted\"\n"
    )
    config.write_text(original, encoding="utf-8")
    args = ("--client", "codex", "--project", project, "--mcp")
    code, _, err = run(capsys, monkeypatch, *args)
    assert code == 0, err
    text = config.read_text(encoding="utf-8")
    assert text.startswith(original.rstrip())
    data = tomllib.loads(text)
    assert data["model"] == "gpt-5"
    assert data["projects"] == {"/work/study": {"trust_level": "trusted"}}
    assert data["mcp_servers"] == {"local-db": {"command": "db-mcp", "args": ["--read-only"]}, **catalog("codex")}
    before = config.read_bytes()
    assert run(capsys, monkeypatch, *args)[0] == 0
    assert config.read_bytes() == before


def test_bootstrap_fixtures_match_recorded_hashes():
    recorded = {name: set() for name in art.BOOTSTRAP}
    for fixture in BOOTSTRAP_FILES:
        recorded[fixture.name.split(".")[0] + ".md"].add(art.digest(fixture.read_bytes()))
    assert recorded == art.BOOTSTRAP, "Each BOOTSTRAP hash needs a copy in tests/fixtures/bootstrap/, and the reverse"


def test_root_rules_are_recorded_unless_initialised():
    # In the toolkit itself, an edited root AGENTS.md must be recorded in BOOTSTRAP, or
    # repositories made from the template could not be initialised. A project initialised
    # from the template keeps its own rules there instead, which need no record.
    data = (ROOT / "AGENTS.md").read_bytes()
    toolkit_heading = LATEST_AGENTS.read_bytes().splitlines()[0]
    if art.digest(data) in art.BOOTSTRAP["AGENTS.md"] or data.splitlines()[:1] != [toolkit_heading]:
        return
    pytest.fail(f"Add {art.digest(data)} to BOOTSTRAP['AGENTS.md'] in install.py and a copy to tests/fixtures/bootstrap/")


@pytest.mark.parametrize("fixture", [f for f in BOOTSTRAP_FILES if f.name.startswith("AGENTS")], ids=lambda f: f.name)
def test_template_bootstrap_rules_replaced(capsys, monkeypatch, project, fixture):
    # A repository made with "Use this template" holds the toolkit's own root files,
    # possibly with other line endings after a checkout on another system.
    (project / "AGENTS.md").write_bytes(swap_line_endings(fixture.read_bytes()))
    (project / "CLAUDE.md").write_bytes(BOOTSTRAP_CLAUDE.read_bytes())
    code, out, err = run(capsys, monkeypatch, "--client", "claude", "--project", project, "--rules")
    assert code == 0, err
    assert "replaces the toolkit's own AGENTS.md" in out
    assert (project / "AGENTS.md").read_bytes() == TEMPLATE_AGENTS
    assert art.normalised((project / "CLAUDE.md").read_bytes()) == art.normalised((ROOT / "templates/CLAUDE.md").read_bytes())


@pytest.mark.parametrize("base", [LATEST_AGENTS, ROOT / "templates/AGENTS.md", ROOT / "AGENTS.md"], ids=["bootstrap", "template", "root"])
def test_edited_rules_refused(capsys, monkeypatch, project, base):
    rules = project / "AGENTS.md"
    rules.write_bytes(base.read_bytes() + b"\nProject: my study\n")
    before = rules.read_bytes()
    code, _, err = run(capsys, monkeypatch, "--client", "codex", "--project", project, "--rules")
    assert code == 2
    assert "Existing AGENTS.md differs" in err
    assert rules.read_bytes() == before


def copy_toolkit(dest, skills=("research/scout",), tests=False):
    """A minimal toolkit copy, like a repository made with "Use this template"."""
    dest.mkdir()
    shutil.copyfile(ROOT / "install.py", dest / "install.py")
    shutil.copyfile(LATEST_AGENTS, dest / "AGENTS.md")
    shutil.copyfile(BOOTSTRAP_CLAUDE, dest / "CLAUDE.md")
    (dest / ".gitignore").write_text("__pycache__/\n.agent-runs/\n.playwright-mcp/\n")
    for folder in ("mcp", "templates", *(f"skills/{name}" for name in skills), *(["tests"] if tests else [])):
        shutil.copytree(ROOT / folder, dest / folder, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(ROOT / "skills/dependencies.json", dest / "skills/dependencies.json")
    return dest / "install.py"


def test_installing_inside_a_template_repository(tmp_path):
    # "Use this template" copies the toolkit, so the project and the toolkit are one folder.
    repo = tmp_path / "from template"
    script = copy_toolkit(repo)
    code, out, err = run_cli("--client", "claude", "--project", ".", "--skill", "scout", "--rules", cwd=repo, script=script)
    assert code == 0, err
    assert "replaces the toolkit's own AGENTS.md" in out
    assert (repo / "AGENTS.md").read_bytes() == TEMPLATE_AGENTS
    # Filling in the rules must not let a rerun mistake them for the toolkit's own file.
    (repo / "AGENTS.md").write_bytes(TEMPLATE_AGENTS + b"\nProject: my study\n")
    code, _, err = run_cli("--client", "claude", "--project", ".", "--rules", cwd=repo, script=script)
    assert code == 2
    assert "Existing AGENTS.md differs" in err
    assert (repo / "AGENTS.md").read_bytes().endswith(b"Project: my study\n")


def test_customised_toolkit_rules_are_not_bootstrap(capsys, monkeypatch, tmp_path, project):
    # A toolkit copy whose own rules were customised must not treat a copy of them as untouched.
    custom = TEMPLATE_AGENTS + b"\nProject: another study\n"
    toolkit = tmp_path / "toolkit"
    script = copy_toolkit(toolkit)
    (toolkit / "AGENTS.md").write_bytes(custom)
    (project / "AGENTS.md").write_bytes(custom)
    code, _, err = run_cli("--client", "codex", "--project", project, "--rules", script=script)
    assert code == 2
    assert "Existing AGENTS.md differs" in err
    assert (project / "AGENTS.md").read_bytes() == custom


@pytest.mark.skipif(os.environ.get("ART_NESTED_TEST") == "1", reason="already inside the nested run")
def test_suite_passes_after_template_initialisation(tmp_path):
    repo = tmp_path / "initialised"
    skills = ("research/scout", "research/critic", "research/parent", "visuals/nature-figure", "visuals/nature-shared")
    script = copy_toolkit(repo, skills=skills, tests=True)
    code, _, err = run_cli("--client", "claude", "--project", ".", "--rules", cwd=repo, script=script)
    assert code == 0, err
    (repo / "AGENTS.md").write_bytes(TEMPLATE_AGENTS + b"\nProject: my study\n")
    env = {**os.environ, "ART_NESTED_TEST": "1"}
    result = subprocess.run([sys.executable, "-I", "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
                            cwd=repo, env=env, capture_output=True, timeout=300)
    assert result.returncode == 0, result.stdout.decode("utf-8", "replace")[-3000:]


def test_gitignore_created(capsys, monkeypatch, project, no_git):
    code, out, err = run(capsys, monkeypatch, "--client", "claude", "--project", project, "--skill", "scout")
    assert code == 0, err
    assert "Added to .gitignore: .agent-runs/, .playwright-mcp/" in out
    assert (project / ".gitignore").read_bytes() == b"# Agent run output and browser snapshots\n.agent-runs/\n.playwright-mcp/\n"


def test_gitignore_appended(capsys, monkeypatch, project, no_git):
    ignore = project / ".gitignore"
    ignore.write_bytes(b"node_modules/\r\n/.agent-runs")
    code, out, err = run(capsys, monkeypatch, "--client", "codex", "--project", project, "--skill", "scout")
    assert code == 0, err
    # Only the exact folder lines count, so the anchored /.agent-runs gets a plain line too.
    assert "Added to .gitignore: .agent-runs/, .playwright-mcp/" in out
    assert ignore.read_bytes() == (
        b"node_modules/\r\n/.agent-runs\r\n\r\n# Agent run output and browser snapshots\r\n.agent-runs/\r\n.playwright-mcp/\r\n"
    )


A, P = ".agent-runs/", ".playwright-mcp/"
# (.gitignore before, entries the installer appends). A folder line counts only after the last ! line.
IGNORE_RULES = [
    pytest.param("", [A, P], id="empty"),
    pytest.param(".agent-runs/\n!.agent-runs/\n.playwright-mcp/\n", [A], id="folder-negated"),
    pytest.param("!.agent-runs/\n.agent-runs/\n.playwright-mcp/\n", [], id="negation-then-rules"),
    pytest.param(".agent-runs/*\n!.agent-runs/review.md\n.playwright-mcp/\n", [A], id="named-file-negated"),
    pytest.param(".agent-runs/\n.playwright-mcp/\n!**/\n", [A, P], id="all-folders-negated"),
    pytest.param(".agent-runs/*\n!*.md\n.playwright-mcp/\n", [A], id="markdown-negated-anywhere"),
    pytest.param(".agent-runs/*\n!.agent-runs/*.md\n.playwright-mcp/\n", [A], id="markdown-negated"),
    pytest.param(".agent-runs/*\n!.agent-runs/nested/\n.playwright-mcp/\n", [A], id="nested-negated"),
    pytest.param(".playwright-mcp/*\n!*.yml\n.agent-runs/\n", [P], id="yml-negated"),
    pytest.param("node_modules/\n!keep.txt\n.agent-runs/\n.playwright-mcp/\n", [], id="rules-already-last"),
    pytest.param(".agent-runs/\n.playwright-mcp/\n!keep.txt\n", [A, P], id="unrelated-negation-last"),
    pytest.param(".agent-runs/*\n.agent-*/\n", [A, P], id="patterns-are-not-the-rule"),
    # git keeps a trailing tab as part of the pattern, so only an exact line counts.
    pytest.param(".agent-runs/\t\n.playwright-mcp/ \n", [A, P], id="trailing-tab-and-space"),
]


@pytest.mark.parametrize("mode", ["git", "no git"])
@pytest.mark.parametrize("rules,added", IGNORE_RULES)
def test_gitignore_folder_rules_come_last(capsys, monkeypatch, project, rules, added, mode):
    if mode == "git":
        if not HAS_GIT:
            pytest.fail("git is needed for this test")
        git(project, "init", "-q")
    else:
        monkeypatch.setattr(art, "git_root", lambda folder: None)
    ignore = project / ".gitignore"
    ignore.write_text(rules)
    args = ("--client", "claude", "--project", project, "--skill", "scout")
    code, out, err = run(capsys, monkeypatch, *args)
    assert code == 0, err
    if added:
        assert "Added to .gitignore: " + ", ".join(added) in out
        assert ignore.read_text().splitlines()[-len(added):] == added
    else:
        assert "already ignores" in out
        assert ignore.read_text() == rules
    assert ("Checked with git check-ignore: .agent-runs/ and .playwright-mcp/ are ignored." in out) == (mode == "git")
    # A rerun appends nothing more.
    after = ignore.read_bytes()
    code, out, _ = run(capsys, monkeypatch, *args)
    assert code == 0 and "already ignores" in out
    assert ignore.read_bytes() == after
    if HAS_GIT:
        if mode == "no git":
            git(project, "init", "-q")
        assert git_would_track(project) == []


@pytest.mark.skipif(not HAS_GIT, reason="git is not installed")
@pytest.mark.parametrize("files,message,command", [
    ([".agent-runs/old.md"], "git already tracks 1 file in .agent-runs,", "git rm -r --cached .agent-runs"),
    ([".agent-runs/old.md", ".agent-runs/nested/x.md", ".playwright-mcp/page.yml"],
     "git already tracks 3 files in .agent-runs and .playwright-mcp,", "git rm -r --cached .agent-runs .playwright-mcp"),
])
def test_tracked_output_files_are_reported(capsys, monkeypatch, project, files, message, command):
    # .gitignore never untracks files git already tracks, so the installer must say so.
    git(project, "init", "-q")
    for name in files:
        (project / name).parent.mkdir(parents=True, exist_ok=True)
        (project / name).write_text("old output")
    assert git(project, "add", "--", *{name.split("/")[0] for name in files}).returncode == 0
    args = ("--client", "claude", "--project", project, "--skill", "scout")
    code, out, err = run(capsys, monkeypatch, *args)
    assert code == 0, err
    assert f"Warning: {message}" in out
    assert f"run: {command}" in out
    assert "Checked with git check-ignore" not in out
    assert git(project, *command.split()[1:]).returncode == 0
    code, out, _ = run(capsys, monkeypatch, *args)
    assert code == 0
    assert "already tracks" not in out
    assert "Checked with git check-ignore: .agent-runs/ and .playwright-mcp/ are ignored." in out


@pytest.mark.parametrize("failure", ["timeout", "exit code", "kept"])
def test_gitignore_verification_outcomes(capsys, monkeypatch, project, failure):
    (project / ".gitignore").write_text(".agent-runs/*\n!.agent-runs/review.md\n")
    real_run = subprocess.run

    def broken_git(command, *args, **options):
        if "check-ignore" in command:
            if failure == "timeout":
                raise subprocess.TimeoutExpired(command, 30)
            if failure == "kept":
                # git answers, but keeps every path (no matching rule).
                return subprocess.CompletedProcess(command, 1, b"".join(b"\0\0\0" + p.encode() + b"\0" for p in art.VERIFY), b"")
            return subprocess.CompletedProcess(command, 128, b"", b"fatal: simulated failure\n")
        return real_run(command, *args, **options)

    monkeypatch.setattr(art, "git_root", lambda folder: folder)
    monkeypatch.setattr(art.subprocess, "run", broken_git)
    code, out, err = run(capsys, monkeypatch, "--client", "claude", "--project", project, "--skill", "scout")
    monkeypatch.undo()
    assert code == 0, err
    assert "Added to .gitignore: .agent-runs/, .playwright-mcp/" in out
    assert "Checked with git check-ignore" not in out
    if failure == "kept":
        assert f"Warning: git does not ignore {', '.join(art.VERIFY)}." in out
    else:
        reason = "git check-ignore timed out" if failure == "timeout" else "git check-ignore failed: fatal: simulated failure"
        assert f"Warning: could not verify .gitignore because {reason}." in out
    if HAS_GIT:
        git(project, "init", "-q")
        assert git_would_track(project) == []


@pytest.mark.skipif(not HAS_GIT, reason="git is not installed")
def test_gitignore_written_even_when_only_local_excludes_ignore(capsys, monkeypatch, project):
    # .git/info/exclude is local to one clone, so the project's .gitignore still gets the entries.
    git(project, "init", "-q")
    (project / ".git/info").mkdir(parents=True, exist_ok=True)
    (project / ".git/info/exclude").write_text(".agent-runs/\n.playwright-mcp/\n")
    code, out, err = run(capsys, monkeypatch, "--client", "claude", "--project", project, "--skill", "scout")
    assert code == 0, err
    assert "Added to .gitignore: .agent-runs/, .playwright-mcp/" in out


@pytest.mark.skipif(not HAS_GIT, reason="git is not installed")
def test_gitignore_in_a_subfolder_of_a_repository(capsys, monkeypatch, tmp_path):
    git(tmp_path, "init", "-q")
    folder = tmp_path / "study"
    folder.mkdir()
    (folder / ".gitignore").write_text(".agent-runs/\n.playwright-mcp/\n")
    code, out, err = run(capsys, monkeypatch, "--client", "codex", "--project", folder, "--skill", "scout")
    assert code == 0, err
    assert "already ignores" in out
    assert (folder / ".gitignore").read_text() == ".agent-runs/\n.playwright-mcp/\n"


MALFORMED = [
    ("claude", "{", "Cannot read"),
    ("claude", "[]", "must hold an object"),
    ("claude", '{"mcpServers": null}', "mcpServers in"),
    ("claude", '{"mcpServers": {"broken": null}}', "Server 'broken'"),
    ("cursor", '{"mcpServers": []}', "mcpServers in"),
    ("cursor", '{"mcpServers": {"arxiv": "https://example.com"}}', "Server 'arxiv'"),
    ("cursor", '"text"', "must hold an object"),
    ("codex", "mcp_servers = [", "Cannot read"),
    ("codex", "mcp_servers = 5\n", "mcp_servers in"),
    ("codex", "[[mcp_servers]]\nname = 'x'\n", "mcp_servers in"),
    ("codex", "[mcp_servers]\nbroken = 5\n", "Server 'broken'"),
    ("codex", 'mcp_servers.arxiv = "https://example.com"\n', "Server 'arxiv'"),
    ("codex", "mcp_servers = {}\n", "Cannot safely extend"),
]


@pytest.mark.parametrize("client,content,message", MALFORMED)
def test_malformed_config_refused(capsys, monkeypatch, project, client, content, message):
    config = project / art.CLIENTS[client][1]
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(content, encoding="utf-8")
    before = snapshot(project)
    code, _, err = run(capsys, monkeypatch, "--client", client, "--project", project, "--skill", "scout", "--mcp", "--rules")
    assert code == 2
    assert message in err
    assert "Traceback" not in err
    assert snapshot(project) == before


@pytest.mark.parametrize("client,link", [("claude", ".claude"), ("claude", ".claude/skills"), ("codex", ".codex"), ("cursor", ".cursor")])
def test_link_outside_project_refused(capsys, monkeypatch, tmp_path, project, client, link):
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    (project / link).parent.mkdir(parents=True, exist_ok=True)
    make_dir_link(project / link, outside)
    code, _, err = run(capsys, monkeypatch, "--client", client, "--project", project, "--skill", "scout", "--mcp")
    assert code == 2
    assert "leads outside the project" in err
    assert list(outside.iterdir()) == []
    assert not (project / ".gitignore").exists()


def test_broken_link_refused(capsys, monkeypatch, tmp_path, project):
    gone = tmp_path / "gone"
    gone.mkdir()
    make_dir_link(project / ".claude", gone)
    gone.rmdir()
    code, _, err = run(capsys, monkeypatch, "--client", "claude", "--project", project, "--skill", "scout")
    assert code == 2
    assert "broken link" in err
    assert not gone.exists()


@pytest.mark.parametrize("client,link,installed", [
    ("claude", ".claude", "skills/scout/SKILL.md"),
    ("claude", ".claude/skills", "scout/SKILL.md"),
    ("codex", ".codex", "config.toml"),
    ("cursor", ".cursor", "mcp.json"),
])
def test_link_inside_project_allowed(capsys, monkeypatch, project, client, link, installed):
    shared = project / "shared"
    shared.mkdir()
    (project / link).parent.mkdir(parents=True, exist_ok=True)
    make_dir_link(project / link, shared)
    args = ("--client", client, "--project", project, "--skill", "scout", "--mcp")
    code, _, err = run(capsys, monkeypatch, *args)
    assert code == 0, err
    assert (shared / installed).is_file()
    assert art.is_link(project / link)
    assert set(servers_in(project, client)) == set(art.SERVERS)
    before = snapshot(shared)
    code, _, err = run(capsys, monkeypatch, *args)
    assert code == 0, err
    assert snapshot(shared) == before


def test_path_with_spaces_and_non_ascii(tmp_path):
    folder = tmp_path / "my project é α 研究"
    folder.mkdir()
    profile = folder / "toolkit é.json"
    profile.write_text(json.dumps({"skills": ["scout"], "mcp": ["arxiv"], "rules": True}), encoding="utf-8")
    code, out, err = run_cli("--client", "codex", "--project", folder, "--profile", profile)
    assert code == 0, err
    assert "Selected items are installed." in out
    assert (folder / ".agents/skills/scout/SKILL.md").is_file()
    assert set(servers_in(folder, "codex")) == {"arxiv"}
    assert (folder / "AGENTS.md").read_bytes() == TEMPLATE_AGENTS


def test_dependency_companion_installed(capsys, monkeypatch, project):
    code, out, err = run(capsys, monkeypatch, "--client", "claude", "--project", project, "--skill", "nature-figure")
    assert code == 0, err
    assert "Skills: nature-shared, nature-figure" in out
    for name in ("nature-figure", "nature-shared"):
        assert (skill_path(project, "claude", name) / "SKILL.md").is_file()


def test_dry_run_writes_nothing(capsys, monkeypatch, project):
    (project / "AGENTS.md").write_bytes(LATEST_AGENTS.read_bytes())
    (project / ".gitignore").write_text("build/\n")
    (project / ".mcp.json").write_text("{}\n")
    before = snapshot(project)
    code, out, err = run(capsys, monkeypatch, "--client", "claude", "--project", project, "--all", "--rules", "--dry-run")
    assert code == 0, err
    assert "Dry run: nothing was written." in out
    assert "Gitignore: add .agent-runs/, .playwright-mcp/" in out
    assert snapshot(project) == before


FULL = ("--client", "claude", "--skill", "scout", "--skill", "parent", "--mcp", "--rules")


def test_partial_install_is_reported_and_recoverable(capsys, monkeypatch, project):
    real_copy = art.copy_skill

    def failing_copy(src, dest):
        if src.name == "parent":
            raise OSError("No space left on device")
        real_copy(src, dest)

    monkeypatch.setattr(art, "copy_skill", failing_copy)
    code, _, err = run(capsys, monkeypatch, *FULL, "--project", project)
    assert code == 1
    assert "Installation stopped while writing skill parent: No space left on device" in err
    assert "Written before the error: AGENTS.md, CLAUDE.md, skill scout" in err
    assert "Not written: skill parent, MCP settings in .mcp.json, .gitignore entries" in err
    assert "Traceback" not in err
    assert (skill_path(project, "claude", "scout") / "SKILL.md").is_file()
    assert not skill_path(project, "claude", "parent").exists()
    assert not (project / ".mcp.json").exists()
    assert not (project / ".gitignore").exists()

    monkeypatch.setattr(art, "copy_skill", real_copy)
    code, _, err = run(capsys, monkeypatch, *FULL, "--project", project)
    assert code == 0, err
    assert art.files_in(skill_path(project, "claude", "parent")) == art.files_in(art.SKILLS["parent"])
    assert set(servers_in(project, "claude")) == set(art.SERVERS)
    assert staged_leftovers(project) == []


def test_failure_inside_skill_staging_cleans_up(capsys, monkeypatch, project):
    # Copy one file of a multi-file skill, then fail, leaving a half-filled staging folder.
    real_copytree = shutil.copytree

    def half_copytree(src, dst, *args, **options):
        # copytree calls itself for subfolders, through this patch, with positional options.
        if Path(src).name != "parent":
            return real_copytree(src, dst, *args, **options)
        copied = []

        def copy_once(a, b, **kw):
            if copied:
                raise OSError("Disk full")
            copied.append(b)
            return shutil.copy2(a, b, **kw)

        return real_copytree(src, dst, copy_function=copy_once, **options)

    monkeypatch.setattr(art.shutil, "copytree", half_copytree)
    code, _, err = run(capsys, monkeypatch, *FULL, "--project", project)
    assert code == 1
    assert "Installation stopped while writing skill parent" in err
    assert "Written before the error: AGENTS.md, CLAUDE.md, skill scout" in err
    assert not skill_path(project, "claude", "parent").exists()
    assert staged_leftovers(project) == []
    assert (skill_path(project, "claude", "scout") / "SKILL.md").is_file()


def test_skill_created_during_install_is_kept(capsys, monkeypatch, project):
    real_copytree = shutil.copytree
    dest = skill_path(project, "claude", "parent")

    def racing_copytree(src, dst, *args, **options):
        result = real_copytree(src, dst, *args, **options)
        if Path(src).name == "parent":
            dest.mkdir()
            (dest / "mine.md").write_text("someone else's file")
        return result

    monkeypatch.setattr(art.shutil, "copytree", racing_copytree)
    code, _, err = run(capsys, monkeypatch, *FULL, "--project", project)
    assert code == 1
    assert "Not written: skill parent" in err
    assert [p.name for p in dest.iterdir()] == ["mine.md"]
    assert staged_leftovers(project) == []


def test_replace_failure_keeps_original_file(capsys, monkeypatch, project):
    bootstrap = LATEST_AGENTS.read_bytes()
    (project / "AGENTS.md").write_bytes(bootstrap)

    def refuse(src, dst):
        raise PermissionError("File is open in another program")

    monkeypatch.setattr(art.os, "replace", refuse)
    code, _, err = run(capsys, monkeypatch, *FULL, "--project", project)
    assert code == 1
    assert "Installation stopped while writing AGENTS.md: File is open in another program" in err
    assert "Written before the error: nothing" in err
    assert (project / "AGENTS.md").read_bytes() == bootstrap
    assert staged_leftovers(project) == []


def test_config_changed_during_install_is_kept(capsys, monkeypatch, project):
    config = project / ".mcp.json"
    config.write_text('{"mcpServers": {}}\n')
    concurrent = '{"mcpServers": {"edited": {"command": "x"}}}\n'
    real_copy = art.copy_skill

    def copy_then_edit(src, dest):
        real_copy(src, dest)
        config.write_text(concurrent)

    monkeypatch.setattr(art, "copy_skill", copy_then_edit)
    code, _, err = run(capsys, monkeypatch, *FULL, "--project", project)
    assert code == 1
    assert "changed during installation" in err
    assert "Not written: MCP settings in .mcp.json, .gitignore entries" in err
    assert config.read_text() == concurrent
    assert staged_leftovers(project) == []
