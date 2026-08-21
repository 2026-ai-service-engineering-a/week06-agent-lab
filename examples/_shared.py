"""예제 공용 헬퍼: 모델 선택 재노출 + 출력 정리 + 여행 목데이터.

모든 예제는 이 파일과 litellm·pydantic만으로 self-contained하게 돈다.
(6주차 랩의 04_react/ 4종만 예외 — 에이전트 본체를 import한다)
"""

from agent.config import EMBEDDING_MODEL, available_models, pick_model  # noqa: F401


def h1(title: str) -> None:
    """섹션 구분 출력."""
    print()
    print(f"=== {title} ===")


def show(label: str, value: object) -> None:
    print(f"  {label}: {value}")


# ── 여행 목데이터 ──────────────────────────────────────────────────────
# 6주차 랩의 05_loops/·06_harness/ 예제들이 쓰는 결정적 도구. 실제 API를 부르지 않아
# 키 소모 없이 루프의 구조 자체를 관찰할 수 있다. (에이전트 본체의 도구는
# agent/tools.py — v0.2에서 실린다)

MOCK_PLACES: dict[str, list[dict]] = {
    "오사카": [
        {"name": "오사카성", "category": "관광", "fee": 600, "area": "주오구"},
        {"name": "도톤보리", "category": "관광", "fee": 0, "area": "난바"},
        {"name": "구로몬 시장", "category": "식당", "fee": 0, "area": "난바"},
        {"name": "우메다 공중정원", "category": "관광", "fee": 1500, "area": "우메다"},
        {"name": "이치란 라멘", "category": "식당", "fee": 0, "area": "난바"},
    ],
    "교토": [
        {"name": "후시미 이나리", "category": "관광", "fee": 0, "area": "후시미"},
        {"name": "기요미즈데라", "category": "관광", "fee": 400, "area": "히가시야마"},
    ],
}


def mock_search(city: str, category: str | None = None) -> list[dict]:
    """장소 검색 목업 — 조건에 맞는 장소 목록."""
    places = MOCK_PLACES.get(city, [])
    if category:
        places = [p for p in places if p["category"] == category]
    return places


def mock_budget(nights: int, people: int) -> dict:
    """예산 계산 목업 — 숙박 12만원/박, 식비 5만원/인/일, 항공 35만원/인."""
    lodging = 120_000 * nights
    food = 50_000 * people * (nights + 1)
    flight = 350_000 * people
    return {"숙박": lodging, "식비": food, "항공": flight, "합계": lodging + food + flight}
