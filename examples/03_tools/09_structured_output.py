"""구조화 출력 — 도구 호출을 응용해 LLM을 '타입 있는 함수'처럼 쓴다.

  docker compose exec lab python examples/03_tools/09_structured_output.py

도구를 실행할 생각이 없어도 된다. 원하는 출력 구조를 pydantic 모델로 쓰고
그 스키마의 도구 호출을 강제하면, 모델의 답이 항상 그 타입으로 온다.
자유 문장 → 검증된 객체. 09_json_mode보다 한 단계 단단한 계약이다.
"""

import json

from litellm import completion
from pydantic import BaseModel, Field

from examples._shared import h1, pick_model

model = pick_model()

class DayPlan(BaseModel):
    day: int = Field(description="며칠째")
    morning: str
    lunch: str
    evening: str


class TripPlan(BaseModel):
    """여행 일정 — 이 구조가 곧 응답 타입이다."""

    city: str
    days: list[DayPlan]
    budget_krw: int = Field(description="총예산(원)")


tool = {
    "type": "function",
    "function": {
        "name": "emit_trip_plan",
        "description": "완성된 여행 일정을 이 구조로 출력한다",
        "parameters": TripPlan.model_json_schema(),
    },
}

resp = completion(
    model=model,
    messages=[{"role": "user", "content": "1박 2일 교토, 예산 40만원으로 일정 짜줘."}],
    tools=[tool],
    tool_choice={"type": "function", "function": {"name": "emit_trip_plan"}},  # 강제
)
raw = resp.choices[0].message.tool_calls[0].function.arguments
plan = TripPlan.model_validate(json.loads(raw))  # 여기서부터는 그냥 파이썬 객체

h1("검증까지 통과한 타입 있는 결과")
print(f"  city = {plan.city}, budget = {plan.budget_krw:,}원, days = {len(plan.days)}일")
for d in plan.days:
    print(f"  {d.day}일차: 아침 {d.morning} / 점심 {d.lunch} / 저녁 {d.evening}")

h1("정리")
print("  plan.days[0].lunch 처럼 필드로 접근한다. 문자열 파싱은 없다.")
