"""병렬 도구 호출 — 항공과 숙소를 한 턴에 동시에 요청한다.

  docker compose exec lab python examples/03_tools/04_parallel_tools.py

독립적인 조회 2건이면 모델은 tool_calls 배열에 두 요청을 함께 실어 보낼
수 있다. 왕복 횟수가 줄어 그만큼 싸고 빠르다.
"""

import json

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()


def make_tool(name: str, desc: str) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    }


tools = [
    make_tool("search_flights", "도시행 항공권 최저가를 조회한다"),
    make_tool("search_hotels", "도시의 숙소 시세를 조회한다"),
]
FAKE = {
    "search_flights": {"price_krw": 310_000, "airline": "LCC"},
    "search_hotels": {"per_night_krw": 120_000, "area": "난바"},
}

messages = [{"role": "user", "content": "오사카 항공권이랑 숙소 시세를 같이 알아봐 주세요."}]
resp = completion(model=model, messages=messages, tools=tools)
calls = resp.choices[0].message.tool_calls

h1(f"한 턴에 실려 온 도구 요청: {len(calls)}건")
for c in calls:
    print(f"  {c.function.name}({c.function.arguments})")

messages.append(resp.choices[0].message.model_dump())
for c in calls:
    messages.append(
        {"role": "tool", "tool_call_id": c.id, "content": json.dumps(FAKE[c.function.name])}
    )

final = completion(model=model, messages=messages, tools=tools)
h1("두 결과를 함께 반영한 답")
print("  " + final.choices[0].message.content.strip()[:250])
