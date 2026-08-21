"""도구 1개 — 환율 조회 도구의 요청~응답 왕복 전체.

  docker compose exec lab python examples/03_tools/01_single_tool.py

tool calling의 정체: 모델은 함수를 실행하지 못한다. "이 함수를 이 인자로
실행해 달라"고 요청할 뿐이고, 실행·결과 회신은 전부 우리 코드의 일이다.
왕복 한 번을 끝까지 손으로 밟는다.
"""

import json

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()

# ① 파이썬 함수 (모델은 이 코드를 모른다)
RATES = {"JPY": 9.1, "USD": 1385.0, "EUR": 1490.0}


def get_exchange_rate(currency: str) -> dict:
    """1 외화가 몇 원인지 (고정 표 — 시연용)."""
    return {"currency": currency, "krw": RATES[currency]}


# ② 모델에게 알려줄 도구 명세 (JSON 스키마)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "통화 코드(JPY, USD, EUR)를 받아 원화 환율을 돌려준다",
            "parameters": {
                "type": "object",
                "properties": {"currency": {"type": "string"}},
                "required": ["currency"],
            },
        },
    }
]

messages = [{"role": "user", "content": "지금 100엔이 한국 돈으로 얼마쯤이죠?"}]

h1("1왕복: 모델이 도구를 요청한다")
resp = completion(model=model, messages=messages, tools=tools)
call = resp.choices[0].message.tool_calls[0]
print(f"  요청된 함수: {call.function.name}")
print(f"  요청된 인자: {call.function.arguments}")

h1("2왕복: 우리가 실행하고, 결과를 되돌려준다")
args = json.loads(call.function.arguments)
result = get_exchange_rate(**args)
print(f"  실행 결과: {result}")

messages.append(resp.choices[0].message.model_dump())  # 모델의 도구 요청도 히스토리에
messages.append(
    {"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)}
)
final = completion(model=model, messages=messages, tools=tools)

h1("최종 답")
print("  " + final.choices[0].message.content.strip()[:200])
