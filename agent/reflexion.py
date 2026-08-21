"""Reflexion — 생성 결과를 평가하고, 미달이면 재시도.

생성자(react 루프)와 평가자를 분리한다. 평가자는 루브릭으로 점수와
피드백을 JSON으로 내고, 통과 기준에 못 미치면 피드백을 질문에 붙여
루프를 다시 돌린다. "한 번에 잘 쓰기"보다 "고칠 점을 알고 다시 쓰기"가
쉽다는 사실을 구조로 만든 것이다 (examples/05_loops/03_reflexion.py).
"""

import json
from dataclasses import dataclass, field

from litellm import completion

from agent import react
from agent.config import pick_model

RUBRIC = """당신은 여행 일정 심사관이다. 다음 기준으로 채점하라 (각 0~10):
- schedule: 요청한 기간의 하루 단위 일정이 전부 있는가
- budget: 예산 내역과 합계가 있고, 요청 상한을 존중하는가
- grounded: 장소·수치가 도구 확인 결과에 근거하는가 (지어낸 흔적 감점)

JSON으로만 답하라:
{"schedule": n, "budget": n, "grounded": n, "feedback": "가장 큰 문제 한 줄"}"""

PASS_THRESHOLD = 24  # 30점 만점 기준 통과선


@dataclass
class Evaluation:
    scores: dict
    total: int
    passed: bool
    feedback: str


@dataclass
class ReflexionResult:
    answer: str | None
    attempts: int
    evaluations: list[Evaluation] = field(default_factory=list)


def evaluate(question: str, answer: str, *, model: str | None = None) -> Evaluation:
    """평가자: 답안을 루브릭으로 채점한다. temperature 0 — 채점은 재현되어야 한다."""
    model = model or pick_model()
    response = completion(
        model=model,
        messages=[
            {"role": "user", "content": f"요청: {question}\n\n답안:\n{answer}\n\n{RUBRIC}"}
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    data = json.loads(response.choices[0].message.content)
    total = int(data["schedule"]) + int(data["budget"]) + int(data["grounded"])
    return Evaluation(
        scores={k: data[k] for k in ("schedule", "budget", "grounded")},
        total=total,
        passed=total >= PASS_THRESHOLD,
        feedback=data.get("feedback", ""),
    )


def run_with_reflexion(
    question: str,
    *,
    model: str | None = None,
    max_retries: int = 2,
    verbose: bool = False,
) -> ReflexionResult:
    """생성 → 평가 → (미달이면 피드백과 함께) 재생성. 최대 max_retries회 재시도."""
    result = ReflexionResult(answer=None, attempts=0)
    feedback: str | None = None

    for attempt in range(1, max_retries + 2):  # 최초 1회 + 재시도 N회
        result.attempts = attempt
        prompt = question
        if feedback:
            prompt = f"{question}\n\n[직전 답안에 대한 평가] {feedback}\n이 문제를 고쳐 다시 작성하라."

        loop_result = react.run(prompt, model=model, verbose=verbose)
        result.answer = loop_result.answer

        evaluation = evaluate(question, result.answer or "", model=model)
        result.evaluations.append(evaluation)
        if verbose:
            print(f"[시도 {attempt}] 평가 {evaluation.total}/30 {evaluation.scores} — "
                  f"{'통과' if evaluation.passed else '재시도'}")

        if evaluation.passed:
            return result
        feedback = evaluation.feedback

    return result  # 재시도 소진 — 마지막 답과 평가 이력을 그대로 돌려준다
