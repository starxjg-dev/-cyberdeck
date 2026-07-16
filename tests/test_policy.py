import os

import pytest

from cyberdeck.models import ToolRequest
from cyberdeck.policy import PolicyAction, PolicyEngine


def request(name, **arguments):
    return ToolRequest("r1", name, arguments)


def test_read_inside_workspace_is_allowed(tmp_path):
    target = tmp_path / "README.md"
    target.write_text("ok", encoding="utf-8")

    decision = PolicyEngine(tmp_path).evaluate(request("file.read", path="README.md"))

    assert decision.action is PolicyAction.ALLOW


def test_parent_traversal_and_absolute_escape_are_denied(tmp_path):
    engine = PolicyEngine(tmp_path)

    parent = engine.evaluate(request("file.read", path="../secret.txt"))
    absolute = engine.evaluate(
        request("file.read", path=os.path.abspath(os.path.join(tmp_path, "..", "secret.txt")))
    )

    assert parent.action is PolicyAction.DENY
    assert absolute.action is PolicyAction.DENY


def test_nonexistent_path_inside_workspace_is_allowed(tmp_path):
    decision = PolicyEngine(tmp_path).evaluate(
        request("file.read", path="future/subdirectory/file.txt")
    )

    assert decision.action is PolicyAction.ALLOW


def test_symlink_escape_is_denied(tmp_path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    link = tmp_path / "escape"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        # Standard Windows users may lack symlink privileges. Linux CI exercises
        # the real symlink branch; this fallback keeps the local confinement
        # assertion deterministic without silently skipping the security suite.
        decision = PolicyEngine(tmp_path).evaluate(
            request("file.read", path=str(outside / "secret.txt"))
        )
        assert decision.action is PolicyAction.DENY
        return

    decision = PolicyEngine(tmp_path).evaluate(request("file.read", path="escape/secret.txt"))

    assert decision.action is PolicyAction.DENY


def test_read_only_process_is_allowed_but_mutation_needs_approval(tmp_path):
    engine = PolicyEngine(tmp_path)

    assert (
        engine.evaluate(request("process.run", argv=["git", "status"])).action
        is PolicyAction.ALLOW
    )
    assert (
        engine.evaluate(request("process.run", argv=["git", "add", "."])).action
        is PolicyAction.REQUIRE_APPROVAL
    )


@pytest.mark.parametrize(
    "argv",
    [
        "rm -rf .",
        [],
        ["powershell", "Remove-Item", "x"],
        ["git", "status", "&&", "whoami"],
        ["rg", "--pre", "malicious-command", "pattern"],
    ],
)
def test_shell_strings_unknown_commands_and_dangerous_arguments_are_denied(tmp_path, argv):
    decision = PolicyEngine(tmp_path).evaluate(request("process.run", argv=argv))

    assert decision.action is PolicyAction.DENY


def test_git_branch_mutation_requires_approval(tmp_path):
    engine = PolicyEngine(tmp_path)

    listing = engine.evaluate(request("process.run", argv=["git", "branch", "--list"]))
    creation = engine.evaluate(request("process.run", argv=["git", "branch", "new-branch"]))

    assert listing.action is PolicyAction.ALLOW
    assert creation.action is PolicyAction.REQUIRE_APPROVAL


@pytest.mark.parametrize(
    "argv",
    [
        ["rg", "needle", ".."],
        ["rg", "needle", "../outside"],
        ["git", "status", "-C", ".."],
        ["git", "status", "--git-dir=../outside/.git"],
        ["git", "status", "--work-tree", "../outside"],
    ],
)
def test_allowlisted_commands_cannot_escape_workspace_through_arguments(tmp_path, argv):
    decision = PolicyEngine(tmp_path).evaluate(request("process.run", argv=argv))

    assert decision.action is PolicyAction.DENY


def test_rg_rejects_absolute_path_outside_workspace(tmp_path):
    outside = (tmp_path.parent / "outside" / "secret.txt").resolve()

    decision = PolicyEngine(tmp_path).evaluate(
        request("process.run", argv=["rg", "needle", str(outside)])
    )

    assert decision.action is PolicyAction.DENY


@pytest.mark.parametrize(
    "argv",
    [
        ["git", "diff", "--output=../escaped.patch"],
        ["git", "diff", "--output", "../escaped.patch"],
        ["git", "diff", "--output=inside.patch"],
        ["git", "grep", "--open-files-in-pager=powershell", "needle"],
        ["git", "grep", "--open-files-in-pager", "powershell", "needle"],
        ["rg", "--file=../outside.patterns", "needle", "."],
        ["rg", "--file", "../outside.patterns", "needle", "."],
        ["rg", "-f", "../outside.patterns", "needle", "."],
        ["git", "status", "--unknown-option"],
        ["rg", "--unknown-option", "needle", "."],
    ],
)
def test_process_safe_grammar_rejects_side_effect_external_program_and_unknown_options(
    tmp_path, argv
):
    decision = PolicyEngine(tmp_path).evaluate(request("process.run", argv=argv))

    assert decision.action is PolicyAction.DENY


@pytest.mark.parametrize(
    "argv",
    [
        ["git", "status"],
        ["git", "status", "--short", "--branch"],
        ["git", "diff", "--", "README.md"],
        ["git", "log", "--oneline", "-n", "5"],
        ["git", "show", "--stat", "HEAD"],
        ["git", "grep", "-n", "needle", "--", "src"],
        ["git", "branch", "--list"],
        ["rg", "-n", "--glob", "*.py", "needle", "."],
        ["rg", "--file", "patterns.txt", "."],
    ],
)
def test_process_safe_grammar_keeps_minimal_read_only_happy_paths(tmp_path, argv):
    decision = PolicyEngine(tmp_path).evaluate(request("process.run", argv=argv))

    assert decision.action is PolicyAction.ALLOW


def test_http_defaults_to_https_and_public_hosts(tmp_path):
    engine = PolicyEngine(tmp_path)

    assert (
        engine.evaluate(request("http.get", url="http://example.com")).action
        is PolicyAction.DENY
    )
    assert (
        engine.evaluate(request("http.get", url="https://example.com")).action
        is PolicyAction.ALLOW
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://user:password@example.com",
        "https://localhost/path",
        "https://127.0.0.1/path",
        "https://[::1]/path",
        "https:///missing-host",
    ],
)
def test_http_rejects_credentials_local_hosts_and_literal_private_addresses(tmp_path, url):
    decision = PolicyEngine(tmp_path).evaluate(request("http.get", url=url))

    assert decision.action is PolicyAction.DENY


def test_unknown_tools_are_denied(tmp_path):
    decision = PolicyEngine(tmp_path).evaluate(request("system.delete", target="everything"))

    assert decision.action is PolicyAction.DENY
