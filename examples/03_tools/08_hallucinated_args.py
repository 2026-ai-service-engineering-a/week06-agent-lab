"""인자 환각 — 모델이 인자를 지어내는 사고와, 검증 코드가 잡는 방식.

  docker compose exec lab python examples/03_tools/08_hallucinated_args.py

스키마는 형태만 강제한다. 값이 실재하는지(그런 호텔이 있는지, 그 날짜가
말이 되는지)는 모른다. pydantic 검증 + 존재 확인을 실행 앞에 세워,
지어낸 값이 실행되기 전에 걸리는 것을 본다.
"""

import json

from litellm import completion
from pydantic import BaseModel, ValidationError, field_validator

from examples._shared import h1, pick_model

model = pick_model()

HOTELS = ["난바 그랜드", "우메다 스카이", "신사이바시 인"]  # 실재하는 호텔 목록


class BookArgs(BaseModel):
    hotel: str
    nights: int

    @field_validator("hotel")
    @classmethod
    def hotel_must_exist(cls, v: str) -> str:
        if v not in HOTELS:
            raise ValueError(f"존재하지 않는 호텔: {v!r}. 목록: {HOTELS}")
        return v


tools = [
    {
        "type": "function",
        "function": {
            "name": "book_hotel",
            "description": "호텔을 예약한다",
            "parameters": {
                "type": "object",
                "properties": {
                    "hotel": {"type": "string"},
                    "nights": {"type": "integer"},
                },
                "required": ["hotel", "nights"],
            },
        },
    }
]

# 목록을 알려주지 않고 예약을 시킨다 → 모델이 호텔 이름을 지어낼 확률이 높다
messages = [{"role": "user", "content": "오사카에서 오션뷰 좋은 호텔로 3박 예약해 주세요."}]
resp = completion(model=model, messages=messages, tools=tools)
call = resp.choices[0].message.tool_calls[0]
raw = json.loads(call.function.arguments)

h1("모델이 보낸 인자")
print(f"  {raw}")

h1("실행 전 검증")
try:
    args = BookArgs.model_validate(raw)
    print(f"  통과: {args} (목록에 있는 호텔이었다)")
except ValidationError as e:
    print(f"  차단: {e.errors()[0]['msg']}")
    print("  → 스키마는 통과했지만 값이 허구다. 검증이 없었다면 유령 예약이 실행됐다")

h1("규율")
print("  LLM이 만든 값은 실행 직전에 코드로 검증한다. 예외 없이.")
