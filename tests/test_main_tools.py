"""agent.main v0.2 — 도구 1왕복이 정확히 한 번만 도는지."""

import json

from agent import main
from tests.conftest import ScriptedLLM, fake_response, fake_tool_call


def test_tool_round_trip(monkeypatch):
    llm = ScriptedLLM([
        fake_response(tool_calls=[fake_tool_call("calc_budget", '{"nights": 3, "people": 2}')]),
        fake_response(content="예산은 약 156만원입니다."),
    ])
    monkeypatch.setattr(main, "completion", llm)

    answer = main.run("3박 4일 오사카 2명 예산?", model="fake-model")

    assert answer == "예산은 약 156만원입니다."
    assert len(llm.calls) == 2  # 요청 + 결과 회신, 정확히 1왕복
    # 2번째 호출의 messages에 실제 도구 실행 결과가 실려 갔다
    tool_msg = [m for m in llm.calls[1]["messages"] if m.get("role") == "tool"][0]
    assert json.loads(tool_msg["content"])["합계"] == 360_000 + 400_000 + 700_000


def test_no_tools_needed_single_call(monkeypatch):
    llm = ScriptedLLM([fake_response(content="안녕하세요!")])
    monkeypatch.setattr(main, "completion", llm)
    assert main.run("안녕", model="fake-model") == "안녕하세요!"
    assert len(llm.calls) == 1
