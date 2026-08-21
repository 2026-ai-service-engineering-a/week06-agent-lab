"""도구 에러 되먹임 — 실패를 모델에 알려주면 스스로 복구한다.

  docker compose exec lab python examples/03_tools/07_tool_error.py

도구가 예외를 던졌을 때 프로그램을 죽이는 대신, 에러 메시지를 role=tool
결과로 되돌려준다. 모델은 그것을 읽고 방법을 바꾼다 (지원 통화로 재시도).
에이전트 루프가 예외에도 계속 도는 비결이 이 패턴이다.
"""

import json

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()

RATES = {"JPY": 9.1, "USD": 1385.0}


def get_exchange_rate(currency: str) -> dict:
    if currency not in RATES:
        raise ValueError(f"지원하지 않는 통화: {currency}. 지원 목록: {list(RATES)}")
    return {"currency": currency, "krw": RATES[currency]}


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "통화 코드의 원화 환율을 돌려준다",
            "parameters": {
                "type": "object",
                "properties": {"currency": {"type": "string"}},
                "required": ["currency"],
            },
        },
    }
]

# 태국 바트를 묻는다 — 도구는 THB를 모른다
messages = [{"role": "user", "content": "100바트가 원화로 얼마죠? 엔화 환율로 대신 감이라도 알려줘요."}]

for step in range(1, 5):
    resp = completion(model=model, messages=messages, tools=tools)
    msg = resp.choices[0].message
    if not msg.tool_calls:
        h1(f"[{step}] 최종 답")
        print("  " + (msg.content or "").strip()[:250])
        break
    messages.append(msg.model_dump())
    for call in msg.tool_calls:
        args = json.loads(call.function.arguments)
        try:
            result = json.dumps(get_exchange_rate(**args))
            h1(f"[{step}] {call.function.name}({args}) → 성공")
        except ValueError as e:
            result = json.dumps({"error": str(e)}, ensure_ascii=False)
            h1(f"[{step}] {call.function.name}({args}) → 실패를 되먹임")
            print(f"  {result}")
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
