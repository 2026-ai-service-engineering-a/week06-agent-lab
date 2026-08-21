"""tool_choice — 도구 사용을 강제하거나 금지하는 제어.

  docker compose exec lab python examples/03_tools/06_tool_choice.py

기본값 auto는 쓸지 말지를 모델이 판단한다. required는 반드시 어떤 도구든
부르게, none은 절대 못 부르게, 특정 함수 지정은 그 도구만 부르게 강제한다.
분기가 코드 손에 있어야 하는 자리(라우팅·검증)에서 쓴다.
"""

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()
tools = [
    {
        "type": "function",
        "function": {
            "name": "calc_budget",
            "description": "여행 예산을 계산한다",
            "parameters": {
                "type": "object",
                "properties": {"nights": {"type": "integer"}},
                "required": ["nights"],
            },
        },
    }
]
question = [{"role": "user", "content": "안녕하세요! 좋은 아침입니다."}]  # 도구가 필요 없는 인사

cases = {
    "auto (기본)": "auto",
    "none (금지)": "none",
    "required (강제)": "required",
}
for name, choice in cases.items():
    resp = completion(model=model, messages=question, tools=tools, tool_choice=choice)
    msg = resp.choices[0].message
    used = f"도구 요청 {msg.tool_calls[0].function.name}" if msg.tool_calls else "그냥 답변"
    h1(f"tool_choice = {name}")
    print(f"  인사말에 대한 반응: {used}")

h1("정리")
print("  required가 인사에도 예산 도구를 부르게 만든 것을 보라. 강제는 강력하지만")
print("  질문과 무관한 호출도 만든다 — 제어권을 가져올 자리를 골라 쓰는 이유다.")
