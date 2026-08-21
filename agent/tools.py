"""여행 플래너의 도구들.

인자 정의는 전부 pydantic 모델이다. 모델 하나가
  ① 모델에게 보여줄 JSON 스키마 (model_json_schema)
  ② 도착한 인자의 타입·범위 검증 (model_validate)
두 가지를 겸한다. 데이터는 결정적 목데이터 — 시연·테스트가 항상 같은
결과를 내고, 외부 API 장애와 무관하게 돈다.
"""

import json
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

# ── 목데이터 ──────────────────────────────────────────────────────────

PLACES: dict[str, list[dict]] = {
    "오사카": [
        {"name": "오사카성", "category": "관광", "fee_yen": 600, "area": "주오구"},
        {"name": "도톤보리", "category": "관광", "fee_yen": 0, "area": "난바"},
        {"name": "우메다 공중정원", "category": "관광", "fee_yen": 1500, "area": "우메다"},
        {"name": "가이유칸 수족관", "category": "관광", "fee_yen": 2400, "area": "베이에리어"},
        {"name": "구로몬 시장", "category": "식당", "fee_yen": 0, "area": "난바"},
        {"name": "이치란 라멘 도톤보리", "category": "식당", "fee_yen": 0, "area": "난바"},
        {"name": "리쿠로 오지상 치즈케이크", "category": "카페", "fee_yen": 0, "area": "난바"},
    ],
    "교토": [
        {"name": "후시미 이나리", "category": "관광", "fee_yen": 0, "area": "후시미"},
        {"name": "기요미즈데라", "category": "관광", "fee_yen": 400, "area": "히가시야마"},
        {"name": "아라시야마 대나무숲", "category": "관광", "fee_yen": 0, "area": "아라시야마"},
        {"name": "니시키 시장", "category": "식당", "fee_yen": 0, "area": "나카교구"},
    ],
}

# 지역(area) 사이의 대략적 이동 시간(분). 표에 없으면 기본 35분.
TRAVEL_MINUTES: dict[frozenset, int] = {
    frozenset({"난바", "주오구"}): 15,
    frozenset({"난바", "우메다"}): 20,
    frozenset({"난바", "베이에리어"}): 30,
    frozenset({"주오구", "우메다"}): 15,
    frozenset({"오사카", "교토"}): 60,
}

# ── 도구 1: 장소 검색 ─────────────────────────────────────────────────


class SearchPlacesArgs(BaseModel):
    """도시의 관광지·식당·카페를 검색한다. 지원 도시: 오사카, 교토."""

    city: str = Field(description="도시 이름 (오사카 또는 교토)")
    category: Literal["관광", "식당", "카페"] | None = Field(
        default=None, description="장소 분류. 생략하면 전체"
    )


def search_places(args: SearchPlacesArgs) -> dict:
    places = PLACES.get(args.city)
    if places is None:
        return {"error": f"지원하지 않는 도시: {args.city}. 지원 목록: {list(PLACES)}"}
    if args.category:
        places = [p for p in places if p["category"] == args.category]
    return {"city": args.city, "places": places}


# ── 도구 2: 이동 시간 ─────────────────────────────────────────────────


class TravelTimeArgs(BaseModel):
    """두 지역 사이의 대략적 이동 시간(분)을 조회한다."""

    from_area: str = Field(description="출발 지역 (예: 난바)")
    to_area: str = Field(description="도착 지역 (예: 우메다)")


def estimate_travel_time(args: TravelTimeArgs) -> dict:
    if args.from_area == args.to_area:
        minutes = 5
    else:
        minutes = TRAVEL_MINUTES.get(frozenset({args.from_area, args.to_area}), 35)
    return {"from": args.from_area, "to": args.to_area, "minutes": minutes}


# ── 도구 3: 예산 계산 ─────────────────────────────────────────────────


class BudgetArgs(BaseModel):
    """숙박·식비·항공을 합쳐 여행 예산(원)을 계산한다."""

    nights: int = Field(ge=0, le=30, description="숙박 일수")
    people: int = Field(ge=1, le=10, description="인원 수")
    style: Literal["절약", "보통", "고급"] = Field(
        default="보통", description="여행 스타일 — 숙박·식비 단가를 가른다"
    )
    include_flight: bool = Field(default=True, description="항공권 포함 여부")


# 스타일별 1박 숙박비 / 1인 1일 식비 (원)
_STYLE_RATES = {"절약": (60_000, 30_000), "보통": (120_000, 50_000), "고급": (250_000, 90_000)}
_FLIGHT_PER_PERSON = 350_000


def calc_budget(args: BudgetArgs) -> dict:
    lodging_rate, food_rate = _STYLE_RATES[args.style]
    lodging = lodging_rate * args.nights
    food = food_rate * args.people * (args.nights + 1)  # 일수 = 박 + 1
    flight = _FLIGHT_PER_PERSON * args.people if args.include_flight else 0
    return {
        "숙박": lodging,
        "식비": food,
        "항공": flight,
        "합계": lodging + food + flight,
        "기준": f"{args.style} 스타일, {args.nights}박 {args.nights + 1}일, {args.people}명",
    }


# ── 레지스트리: 이름 → (인자 모델, 함수) ─────────────────────────────

REGISTRY: dict[str, tuple[type[BaseModel], object]] = {
    "search_places": (SearchPlacesArgs, search_places),
    "estimate_travel_time": (TravelTimeArgs, estimate_travel_time),
    "calc_budget": (BudgetArgs, calc_budget),
}


def tool_schemas() -> list[dict]:
    """모델에게 보여줄 도구 명세 — pydantic 모델에서 자동 생성한다."""
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": (model.__doc__ or "").strip(),
                "parameters": model.model_json_schema(),
            },
        }
        for name, (model, _fn) in REGISTRY.items()
    ]


def run_tool(name: str, raw_arguments: str) -> str:
    """도구 실행의 단일 관문: 검증 → 실행 → JSON 문자열.

    검증 실패·미등록 도구도 예외를 올리지 않고 에러를 '결과'로 돌려준다.
    모델이 그것을 읽고 스스로 고치는 것이 tool calling의 복구 패턴이다
    (examples/03_tools/07_tool_error.py).
    """
    entry = REGISTRY.get(name)
    if entry is None:
        return json.dumps({"error": f"없는 도구: {name}"}, ensure_ascii=False)
    args_model, fn = entry
    try:
        args = args_model.model_validate(json.loads(raw_arguments or "{}"))
    except (ValidationError, json.JSONDecodeError) as e:
        return json.dumps({"error": f"인자 검증 실패: {e}"}, ensure_ascii=False)
    return json.dumps(fn(args), ensure_ascii=False)
