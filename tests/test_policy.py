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
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")

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
