"""agent.react — 루프의 구조를 각본 LLM으로 검증한다.

도구 실행은 진짜(결정적 목데이터), LLM만 가짜다. 루프가
① 도구를 실제로 실행해 결과를 되먹이는지 ② 최종 답에서 멈추는지
③ 한도에서 강제 종료되는지를 본다.
"""

import json

from agent import react
from tests.conftest import ScriptedLLM, fake_response, fake_tool_call


def test_tool_then_final(monkeypatch):
    llm = ScriptedLLM([
        fake_response(tool_calls=[fake_tool_call("search_places", '{"city": "오사카"}')], prompt_tokens=200),
        fake_response(content="일정: 도톤보리와 오사카성.", prompt_tokens=450),
    ])
    monkeypatch.setattr(react, "completion", llm)

    result = react.run("오사카 일정 짜줘", model="fake-model")

    assert result.stopped_by == "final"
    assert result.answer == "일정: 도톤보리와 오사카성."
    assert [s.tool for s in result.steps] == ["search_places", None]
    # 도구가 진짜로 실행되어 observation에 목데이터가 담겼다
    assert "오사카성" in result.steps[0].observation
    # 2번째 LLM 호출에 tool 메시지가 실려 갔다
    roles = [m.get("role") for m in llm.calls[1]["messages"]]
    assert roles == ["system", "user", "assistant", "tool"]


def test_error_observation_fed_back(monkeypatch):
    llm = ScriptedLLM([
        fake_response(tool_calls=[fake_tool_call("search_places", '{"city": "파리"}')]),
        fake_response(tool_calls=[fake_tool_call("search_places", '{"city": "오사카"}', "call_2")]),
        fake_response(content="오사카로 안내합니다."),
    ])
    monkeypatch.setattr(react, "completion", llm)

    result = react.run("파리 말고 간사이", model="fake-model")

    # 1스텝의 에러 결과가 그대로 되먹여졌고, 루프는 죽지 않고 복구했다
    assert "error" in json.loads(result.steps[0].observation)
    assert result.stopped_by == "final"
    assert len(result.steps) == 3


def test_max_steps_forces_wrap_up(monkeypatch):
    # 모델이 영원히 도구만 요청하는 각본 — 한도(2) + 마무리 호출 1번
    llm = ScriptedLLM([
        fake_response(tool_calls=[fake_tool_call("search_places", '{"city": "오사카"}')]),
        fake_response(tool_calls=[fake_tool_call("search_places", '{"city": "교토"}', "call_2")]),
        fake_response(content="여기까지 확인한 내용으로 정리합니다."),
    ])
    monkeypatch.setattr(react, "completion", llm)

    result = react.run("전부 다 검색해", model="fake-model", max_steps=2)

    assert result.stopped_by == "max_steps"
    assert result.answer.startswith("여기까지")
    assert len(llm.calls) == 3
    # 마무리 호출에는 tools가 실리지 않는다 (더 돌 수 없어야 보험이다)
    assert "tools" not in llm.calls[2]


def test_custom_system_prompt_used(monkeypatch):
    llm = ScriptedLLM([fake_response(content="ok")])
    monkeypatch.setattr(react, "completion", llm)
    react.run("질문", model="fake-model", system="커스텀 프롬프트")
    assert llm.calls[0]["messages"][0]["content"] == "커스텀 프롬프트"
