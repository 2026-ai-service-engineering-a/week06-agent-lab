"""tool call의 JSON 원문 — 모델이 보내는 것의 실체를 해부한다.

  docker compose exec lab python examples/03_tools/02_roundtrip_raw.py

01번과 같은 왕복이지만, 이번엔 각 단계의 JSON 원문을 그대로 찍는다.
"모델이 함수를 호출한다"는 말의 실체가 assistant 메시지 안의
tool_calls 필드 하나라는 것, 그리고 우리가 되돌려주는 것도 role=tool인
평범한 메시지 하나라는 것을 눈으로 확인한다.
"""

import json

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "도시의 오늘 날씨를 돌려준다",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    }
]
messages = [{"role": "user", "content": "오사카 오늘 날씨 어때요?"}]

resp = completion(model=model, messages=messages, tools=tools)
assistant_msg = resp.choices[0].message

h1("① 모델이 보낸 assistant 메시지 원문")
print(json.dumps(assistant_msg.model_dump(), ensure_ascii=False, indent=2)[:600])

call = assistant_msg.tool_calls[0]
tool_msg = {
    "role": "tool",
    "tool_call_id": call.id,
    "content": json.dumps({"city": "오사카", "weather": "맑음", "temp_c": 21}),
}

h1("② 우리가 돌려줄 tool 메시지 원문")
print(json.dumps(tool_msg, ensure_ascii=False, indent=2))

h1("③ 이 시점의 messages 배열 전체 구조")
messages += [assistant_msg.model_dump(), tool_msg]
for i, m in enumerate(messages):
    kind = "tool_calls" if m.get("tool_calls") else "content"
    print(f"  [{i}] role={m['role']:<9} {kind}")

final = completion(model=model, messages=messages, tools=tools)
h1("④ 최종 답")
print("  " + final.choices[0].message.content.strip()[:150])
