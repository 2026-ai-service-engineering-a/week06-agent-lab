"""도구 선택 — 10개 중 맞는 것을 고르게 하기. 설명 문구가 품질을 가른다.

  docker compose exec lab python examples/03_tools/10_tool_selection.py

같은 10개 도구를 ① 성의 있는 이름·설명과 ② 익명 이름·무성의한 설명
(tool_7 / "도구7") 두 벌로 등록하고, 같은 질문에서 무엇이 선택되는지
비교한다. 이름만 남겨도 모델은 이름에서 유추한다 — 그래서 이름까지 지워야
설명 문구의 몫이 드러난다. 모델이 보는 것은 코드가 아니라 문자열뿐이다.
"""

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()

SPECS = [
    ("search_places", "도시의 관광지·식당을 검색한다"),
    ("get_exchange_rate", "통화 코드의 원화 환율을 조회한다"),
    ("calc_budget", "숙박·식비·항공을 합쳐 여행 예산을 계산한다"),
    ("get_weather", "도시의 오늘 날씨를 조회한다"),
    ("translate", "문장을 다른 언어로 번역한다"),
    ("book_hotel", "호텔을 예약한다"),
    ("find_route", "두 장소 사이의 이동 경로와 시간을 찾는다"),
    ("visa_check", "국적·목적지의 비자 필요 여부를 확인한다"),
    ("event_calendar", "도시의 축제·행사 일정을 조회한다"),
    ("luggage_rules", "항공사 수하물 규정을 조회한다"),
]


def build_tools(good_descriptions: bool) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": name if good_descriptions else f"tool_{i}",
                "description": desc if good_descriptions else f"도구{i}",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
        }
        for i, (name, desc) in enumerate(SPECS)
    ]


question = [{"role": "user", "content": "이번 주말 오사카에 뭔가 축제 같은 거 하나요?"}]

for label, good in [("성의 있는 이름·설명", True), ("익명 이름·무성의한 설명", False)]:
    resp = completion(model=model, messages=question, tools=build_tools(good))
    msg = resp.choices[0].message
    picked = msg.tool_calls[0].function.name if msg.tool_calls else "(도구 안 씀)"
    answer = "tool_8" if not good else "event_calendar"
    h1(label)
    print(f"  선택된 도구: {picked}  (정답: {answer})")

h1("정리")
print("  실행 코드는 한 줄도 안 바꿨다. 이름과 설명, 문자열이 곧 선택 품질이다.")
