"""ReAct 루프 — v0.3에서 완성된다.

reasoning(다음 행동 판단) → action(도구 호출) → observation(결과 관찰)을
종료 조건까지 반복한다. 종료 조건은 두 가지뿐이다:
  ① 모델이 도구 없이 답을 내놓음 (final)
  ② 스텝 한도 도달 (max_steps) — 무한 루프에 대한 보험

트레이스(스텝 기록)를 데이터로 남긴다. 에이전트를 이해한다는 것은
트레이스를 읽을 줄 안다는 뜻이다 (examples/04_react/).
"""

from dataclasses import dataclass, field

from litellm import completion

from agent.config import pick_model
from agent.tools import run_tool, tool_schemas

SYSTEM_PROMPT = """당신은 여행 플래너다. 사용자의 조건(기간·인원·예산)을 존중해
하루 단위의 구체적인 일정을 제안한다.

## 도구 사용
- 장소·이동시간·예산은 지어내지 말고 반드시 도구로 확인한다.
- 한 번에 하나의 판단만 한다: 도구가 더 필요하면 도구를, 충분하면 최종 답을.
- 도구 결과에 error가 있으면 원인을 읽고 인자를 고쳐 다시 시도한다.

## 최종 답
- 하루 단위 일정 + 예산 내역 + 근거(도구로 확인한 수치)를 담는다.
- 확인하지 못한 것은 확인하지 못했다고 말한다."""


@dataclass
class StepRecord:
    """루프 한 바퀴의 기록 — 트레이스의 최소 단위."""

    tool: str | None  # None이면 최종 답 스텝
    args: str | None
    observation: str | None
    prompt_tokens: int
    completion_tokens: int


@dataclass
class ReactResult:
    answer: str | None
    stopped_by: str  # "final" | "max_steps"
    steps: list[StepRecord] = field(default_factory=list)
    messages: list[dict] = field(default_factory=list)


def run(
    question: str,
    *,
    model: str | None = None,
    max_steps: int = 8,
    system: str | None = None,
    verbose: bool = False,
) -> ReactResult:
    """질문 하나를 ReAct 루프로 푼다."""
    model = model or pick_model()
    messages: list[dict] = [
        {"role": "system", "content": system or SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    result = ReactResult(answer=None, stopped_by="max_steps", messages=messages)

    for step_no in range(1, max_steps + 1):
        response = completion(model=model, messages=messages, tools=tool_schemas())
        message = response.choices[0].message
        usage = response.usage

        if not message.tool_calls:
            # 종료 ①: 최종 답
            result.answer = message.content or ""
            result.stopped_by = "final"
            result.steps.append(
                StepRecord(None, None, None, usage.prompt_tokens, usage.completion_tokens)
            )
            if verbose:
                print(f"[step {step_no}] 최종 답 (컨텍스트 {usage.prompt_tokens}tk)")
            return result

        # action: 요청된 도구를 전부 실행하고 observation을 되먹인다
        messages.append(message.model_dump())
        for call in message.tool_calls:
            observation = run_tool(call.function.name, call.function.arguments)
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": observation}
            )
            result.steps.append(
                StepRecord(
                    call.function.name,
                    call.function.arguments,
                    observation,
                    usage.prompt_tokens,
                    usage.completion_tokens,
                )
            )
            if verbose:
                print(
                    f"[step {step_no}] {call.function.name}({call.function.arguments}) "
                    f"→ {observation[:80]}… (컨텍스트 {usage.prompt_tokens}tk)"
                )

    # 종료 ②: 스텝 한도 — 지금까지의 근거로 마무리 답변만 받는다
    messages.append(
        {
            "role": "user",
            "content": "스텝 한도에 도달했다. 지금까지 확인한 것만으로 최선의 답을 정리하라.",
        }
    )
    response = completion(model=model, messages=messages)  # 도구 없이 마무리
    result.answer = response.choices[0].message.content or ""
    if verbose:
        print(f"[한도 도달] max_steps={max_steps}, 지금까지의 근거로 마무리")
    return result
