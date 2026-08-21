"""Pydantic → 도구 스키마 — 손으로 쓰던 JSON 스키마를 모델 클래스에서 뽑는다.

  docker compose exec lab python examples/03_tools/03_pydantic_schema.py

스키마 출력은 키 없이도 동작한다. 인자 정의를 pydantic 모델로 쓰면
① 스키마 자동 생성 ② 도착한 인자의 타입 검증까지 한 번에 얻는다.
에이전트 본체(agent/tools.py)의 도구가 전부 이 방식이다.
"""

import json

from pydantic import BaseModel, Field

from examples._shared import h1

class BudgetArgs(BaseModel):
    """여행 예산 계산 인자 — 이 docstring이 그대로 설명이 된다."""

    nights: int = Field(ge=0, description="숙박 일수")
    people: int = Field(ge=1, description="인원 수")
    include_flight: bool = Field(default=True, description="항공권 포함 여부")


h1("pydantic 모델에서 뽑은 JSON 스키마")
schema = BudgetArgs.model_json_schema()
print(json.dumps(schema, ensure_ascii=False, indent=2))

h1("litellm 도구 명세로 조립")
tool = {
    "type": "function",
    "function": {
        "name": "calc_budget",
        "description": BudgetArgs.__doc__.strip(),
        "parameters": schema,
    },
}
print(json.dumps(tool, ensure_ascii=False, indent=2)[:400] + " …")

h1("도착한 인자의 검증도 같은 모델로")
good = BudgetArgs.model_validate({"nights": 3, "people": 2})
print(f"  정상 인자 → {good}")
try:
    BudgetArgs.model_validate({"nights": -1, "people": 0})
except Exception as e:
    print(f"  불량 인자 → {type(e).__name__} (ge 제약이 잡았다)")
