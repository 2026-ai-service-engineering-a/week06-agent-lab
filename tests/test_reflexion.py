"""agent.reflexion — 평가 파싱과 재시도 분기를 검증한다."""

import json

from agent import react, reflexion
from tests.conftest import ScriptedLLM, fake_response


def test_evaluate_parses_scores(monkeypatch):
    verdict = {"schedule": 9, "budget": 8, "grounded": 8, "feedback": "예산 근거 보강"}
    llm = ScriptedLLM([fake_response(content=json.dumps(verdict))])
    monkeypatch.setattr(reflexion, "completion", llm)

    ev = reflexion.evaluate("질문", "답안", model="fake-model")

    assert ev.total == 25 and ev.passed
    assert ev.feedback == "예산 근거 보강"
    assert llm.calls[0]["temperature"] == 0  # 채점은 재현되어야 한다


def test_fail_then_pass_retries_once(monkeypatch):
    # 생성자(react)는 호출마다 다른 답을 낸다
    answers = iter(["엉성한 초안", "고친 답안"])
    monkeypatch.setattr(
        react, "run",
        lambda q, **kw: react.ReactResult(answer=next(answers), stopped_by="final"),
    )
    # 평가자는 1회차 미달(20) → 2회차 통과(27)
    verdicts = [
        {"schedule": 6, "budget": 7, "grounded": 7, "feedback": "일정이 하루 빠졌다"},
        {"schedule": 9, "budget": 9, "grounded": 9, "feedback": ""},
    ]
    llm = ScriptedLLM([fake_response(content=json.dumps(v)) for v in verdicts])
    monkeypatch.setattr(reflexion, "completion", llm)

    result = reflexion.run_with_reflexion("2박 3일 오사카", model="fake-model")

    assert result.attempts == 2
    assert result.answer == "고친 답안"
    assert [e.passed for e in result.evaluations] == [False, True]
    # 2회차 평가 요청… 이 아니라 2회차 '생성' 프롬프트에 피드백이 실렸는지는
    # react.run 대역이 받은 질문으로 확인할 수 없으니, 평가 이력으로 판정한다
    assert result.evaluations[0].feedback == "일정이 하루 빠졌다"


def test_retry_budget_exhausts(monkeypatch):
    monkeypatch.setattr(
        react, "run",
        lambda q, **kw: react.ReactResult(answer="늘 같은 답", stopped_by="final"),
    )
    bad = {"schedule": 3, "budget": 3, "grounded": 3, "feedback": "전면 재작성"}
    llm = ScriptedLLM([fake_response(content=json.dumps(bad)) for _ in range(3)])
    monkeypatch.setattr(reflexion, "completion", llm)

    result = reflexion.run_with_reflexion("질문", model="fake-model", max_retries=2)

    # 최초 1회 + 재시도 2회 = 3번 시도하고 멈춘다 (무한 재시도 금지)
    assert result.attempts == 3
    assert not result.evaluations[-1].passed
    assert result.answer == "늘 같은 답"  # 실패해도 마지막 답은 돌려준다


def test_feedback_lands_in_retry_prompt(monkeypatch):
    seen_questions = []

    def spy_run(question, **kw):
        seen_questions.append(question)
        return react.ReactResult(answer="답", stopped_by="final")

    monkeypatch.setattr(react, "run", spy_run)
    verdicts = [
        {"schedule": 5, "budget": 5, "grounded": 5, "feedback": "예산 상한 초과"},
        {"schedule": 9, "budget": 9, "grounded": 9, "feedback": ""},
    ]
    llm = ScriptedLLM([fake_response(content=json.dumps(v)) for v in verdicts])
    monkeypatch.setattr(reflexion, "completion", llm)

    reflexion.run_with_reflexion("1박 2일", model="fake-model")

    assert "예산 상한 초과" in seen_questions[1]  # 재시도 프롬프트에 피드백이 박힌다
    assert "1박 2일" in seen_questions[1]  # 원 질문도 유지된다
