"""agent.main v0.1 — 도구 없는 뼈대가 질문을 그대로 모델에 전달하는지."""

from agent import main
from tests.conftest import ScriptedLLM, fake_response


def test_run_returns_model_answer(monkeypatch):
    llm = ScriptedLLM([fake_response(content="1일차: 도톤보리")])
    monkeypatch.setattr(main, "completion", llm)

    answer = main.run("1박 2일 오사카", model="fake-model")

    assert answer == "1일차: 도톤보리"
    assert llm.calls[0]["model"] == "fake-model"
    # system + user 두 메시지, 사용자 질문이 그대로 실린다
    messages = llm.calls[0]["messages"]
    assert [m["role"] for m in messages] == ["system", "user"]
    assert messages[1]["content"] == "1박 2일 오사카"
