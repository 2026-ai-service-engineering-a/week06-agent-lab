"""인자 제약 — 선택 인자·기본값·enum이 스키마에 실리는 모양.

  docker compose exec lab python examples/03_tools/05_arg_constraints.py

스키마 출력은 키 없이도 동작한다. "이 인자는 이 셋 중 하나"(enum),
"없으면 이 값"(default), "안 줘도 됨"(optional)을 스키마가 말해 주면,
모델은 그 안에서만 고른다. 제약은 프롬프트보다 강하다.
"""

import json
from typing import Literal

from pydantic import BaseModel, Field

from examples._shared import h1

class SearchArgs(BaseModel):
    """장소 검색 인자."""

    city: str = Field(description="도시 이름")
    category: Literal["관광", "식당", "카페"] | None = Field(
        default=None, description="장소 분류. 없으면 전체"
    )
    max_results: int = Field(default=5, ge=1, le=20, description="최대 결과 수")


h1("스키마에 실린 제약")
schema = SearchArgs.model_json_schema()
print(json.dumps(schema, ensure_ascii=False, indent=2))

h1("읽는 법")
print("  category의 enum: 모델은 셋 중 하나(또는 생략)만 고를 수 있다")
print("  max_results의 default+범위: 안 주면 5, 줘도 1~20을 벗어나면 검증에서 잡힌다")
print("  required에 city만 있는 것: 나머지는 선택 인자라는 뜻")
