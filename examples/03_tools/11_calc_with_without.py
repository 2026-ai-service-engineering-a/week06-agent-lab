"""도구가 있을 때와 없을 때 — 같은 계산 요청을 두 방식으로 처리한다.

  docker compose exec lab python examples/03_tools/11_calc_with_without.py

같은 질문("3+4+(5 곱하기 2) 를 계산해줘")을 두 번 보낸다. 한 번은 도구 없이,
한 번은 계산기 도구를 쥐여주고. 답이 같더라도 **답을 만든 방법**이 다르다.
도구 없는 쪽은 모델이 머릿속으로 이어 붙인 확률이고, 도구 쪽은 파이썬이
실제로 계산한 값이다.

관전 포인트 셋:
  ① 자연어 "5 곱하기 2"가 인자 "5*2"로 번역되는 자리 (번역이 모델의 몫)
  ② 쉬운 식에서는 두 답이 같다는 것 — 그래서 도구 없는 쪽이 안전해 보인다
  ③ 자릿수를 키우면 그 착시가 깨진다는 것 (두 번째 질문)
"""

import json

from litellm import completion

from examples._shared import h1, pick_model, show

model = pick_model()

ALLOWED = set("0123456789+-*/(). ")


def calculator(expression: str) -> dict:
    """사칙연산 식을 정확히 계산한다. 허용 문자만 통과시킨다."""
    if set(expression) - ALLOWED:
        return {"error": f"허용되지 않는 문자가 있다: {expression!r}"}
    return {"expression": expression, "result": eval(expression)}  # noqa: S307


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "사칙연산 식을 정확히 계산한다. 예: '3+4+(5*2)'",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "파이썬 문법의 산술식. 숫자와 + - * / ( ) 만",
                    }
                },
                "required": ["expression"],
            },
        },
    }
]

SYSTEM = "당신은 사용자를 돕는 어시스턴트입니다. 계산 결과는 숫자로 분명히 밝히세요."


def ask_plain(question: str) -> str:
    """① 도구 없이 — 모델이 스스로 센다."""
    resp = completion(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
        ],
    )
    return (resp.choices[0].message.content or "").strip()


def ask_with_tool(question: str) -> tuple[str, list[dict]]:
    """② 계산기를 쥐여주고 — 모델이 요청하면 우리가 실행한다."""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    calls = []
    for _ in range(4):  # 도구를 몇 번 부르든 받아 준다
        resp = completion(model=model, messages=messages, tools=tools)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return (msg.content or "").strip(), calls
        messages.append(msg.model_dump())
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = calculator(**args)
            calls.append({"name": call.function.name, "args": args, "result": result})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )
    return "(도구 호출이 끝나지 않았다)", calls


def verdict(answer: str, truth: int) -> str:
    """답 문장 안에 정답 숫자가 들어 있는지로 채점한다 (쉼표는 무시)."""
    return "○ 맞음" if str(truth) in answer.replace(",", "") else "✗ 틀림"


CASES = [
    ("3+4+(5 곱하기 2) 를 계산해줘", 3 + 4 + (5 * 2)),
    ("48627 곱하기 9314에 1250을 더하면? 숫자로 답해줘", 48627 * 9314 + 1250),
]

for question, truth in CASES:
    h1(f"질문: {question}")
    show("정답 (파이썬이 계산)", f"{truth:,}")

    plain = ask_plain(question)
    h1("① 도구 없이 — 모델이 스스로 센다")
    print(f"  {plain[:220]}")
    show("판정", verdict(plain, truth))

    tooled, calls = ask_with_tool(question)
    h1("② 계산기를 쥐여주고 — 모델은 요청만, 실행은 우리 코드")
    for c in calls:
        print(f"  모델의 요청  → {c['name']}({json.dumps(c['args'], ensure_ascii=False)})")
        print(f"  우리의 실행  → {json.dumps(c['result'], ensure_ascii=False)}")
    if not calls:
        print("  (모델이 도구를 부르지 않았다)")
    print(f"  최종 답: {tooled[:220]}")
    show("판정", verdict(tooled, truth))

h1("정리")
print("  자연어 '5 곱하기 2'를 '5*2'로 옮긴 것은 모델이고, 그 식을 실제로 센 것은 파이썬이다.")
print("  쉬운 식에서는 두 답이 같아서 도구 없는 쪽도 멀쩡해 보인다. 그 착시가 위험하다.")
print("  자릿수를 키우면 갈린다. 도구는 답을 바꾸는 장치가 아니라 답의 근거를 바꾸는 장치다.")
