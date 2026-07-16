import json

import pytest

from cyberdeck.models import (
    AgentRunResult,
    AgentStep,
    ErrorCategory,
    ToolRequest,
    ToolResult,
)


def test_tool_request_requires_name_and_mapping_arguments():
    request = ToolRequest.from_dict(
        {"request_id": "r1", "name": "file.read", "arguments": {"path": "README.md"}}
    )

    assert request.name == "file.read"
    assert request.to_dict() == {
        "request_id": "r1",
        "name": "file.read",
        "arguments": {"path": "README.md"},
        "rationale": "",
    }
    with pytest.raises(ValueError, match="requires name"):
        ToolRequest.from_dict({"request_id": "r2", "name": "", "arguments": {}})
    with pytest.raises(ValueError, match="must be an object"):
        ToolRequest.from_dict({"request_id": "r2", "name": "file.read", "arguments": []})


def test_tool_request_requires_non_empty_request_id():
    with pytest.raises(ValueError, match="requires request_id"):
        ToolRequest.from_dict({"request_id": "", "name": "file.read", "arguments": {}})


def test_agent_step_parses_fenced_json():
    step = AgentStep.from_model_text(
        '```json\n{"thought":"inspect","final_answer":"done"}\n```'
    )

    assert step.thought == "inspect"
    assert step.final_answer == "done"
    assert step.tool_request is None


def test_agent_step_rejects_tool_and_final_together():
    with pytest.raises(ValueError, match="cannot contain both"):
        AgentStep.from_model_text(
            '{"tool_request":{"request_id":"r","name":"file.read","arguments":{}},'
            '"final_answer":"ambiguous"}'
        )


@pytest.mark.parametrize(
    ("model_text", "message"),
    [
        ("not json", "valid JSON"),
        ("[]", "JSON object"),
        ('```json\n{"final_answer":"ok"}', "Markdown fence"),
        ('{"tool_request":"file.read"}', "tool_request must be an object"),
    ],
)
def test_agent_step_rejects_malformed_model_output(model_text, message):
    with pytest.raises(ValueError, match=message):
        AgentStep.from_model_text(model_text)


def test_error_category_is_stable_string_enum():
    assert ErrorCategory.POLICY.value == "policy"
    assert json.dumps({"category": ErrorCategory.POLICY}) == '{"category": "policy"}'


def test_result_records_are_json_serializable():
    tool_result = ToolResult(
        request_id="r1",
        tool_name="file.read",
        success=False,
        output="",
        error_category=ErrorCategory.TOOL,
        error_message="missing",
        duration_ms=3,
        metadata={"path": "README.md"},
    )
    run_result = AgentRunResult(
        run_id="run-1",
        success=False,
        answer="",
        steps=2,
        error_category=ErrorCategory.TOOL,
        error_message="missing",
        metadata={"tool_results": [tool_result.to_dict()]},
    )

    encoded = json.dumps(run_result.to_dict())
    decoded = AgentRunResult.from_dict(json.loads(encoded))

    assert decoded == run_result
    assert decoded.error_category is ErrorCategory.TOOL


def test_result_records_reject_invalid_values():
    with pytest.raises(ValueError, match="duration_ms"):
        ToolResult("r1", "file.read", True, duration_ms=-1)
    with pytest.raises(ValueError, match="steps"):
        AgentRunResult("run-1", True, "done", -1)
