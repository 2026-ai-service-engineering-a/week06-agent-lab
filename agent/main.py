"""여행 플래너 에이전트 CLI — v0.2: 도구 장착 (1왕복).

  docker compose exec lab python -m agent.main "3박 4일 오사카, 예산 80만원"

v0.2의 에이전트는 도구(검색·이동시간·예산)를 한 번 쓸 수 있다.
모델이 도구를 요청하면 실행해 결과를 되돌려주고 답을 받는다 — 딱 1왕복.
여러 도구를 오가며 반복하는 루프는 6주차 랩에서 완성된다.
"""

import argparse

from litellm import completion

from agent.config import pick_model
from agent.tools import run_tool, tool_schemas

SYSTEM_PROMPT = """당신은 여행 플래너다. 사용자의 조건(기간·인원·예산)을 존중해
하루 단위의 구체적인 일정을 제안한다. 장소·이동시간·예산은 지어내지 말고
도구로 확인한다. 모르는 것은 모른다고 말한다."""


def run(question: str, model: str | None = None) -> str:
    """질문 하나 → (필요하면 도구 1왕복) → 답 하나."""
    model = model or pick_model()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    response = completion(model=model, messages=messages, tools=tool_schemas())
    message = response.choices[0].message

    if message.tool_calls:
        # 도구 실행 → 결과 회신 → 최종 답. 반복은 없다 (그것이 v0.3).
        messages.append(message.model_dump())
        for call in message.tool_calls:
            result = run_tool(call.function.name, call.function.arguments)
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )
        response = completion(model=model, messages=messages, tools=tool_schemas())
        message = response.choices[0].message

    return message.content or ""


def main() -> None:
    parser = argparse.ArgumentParser(description="여행 플래너 에이전트")
    parser.add_argument("question", help="여행 요청 (예: '3박 4일 오사카, 예산 80만원')")
    args = parser.parse_args()
    print(run(args.question))


if __name__ == "__main__":
    main()
