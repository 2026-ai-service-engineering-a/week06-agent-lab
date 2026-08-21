"""하네스 켜고 끄기 — 같은 모델·같은 과제에서 하네스 요소가 성패를 가른다.

  docker compose exec lab python examples/06_harness/01_harness_onoff.py

하네스 = 모델을 감싸는 실행 환경 전체 (시스템 프롬프트, 도구 설명, 가드,
로깅). 여기서는 두 요소(시스템 프롬프트, 도구 설명)를 하나씩 끄며
같은 과제의 결과가 어떻게 달라지는지 본다.
"""

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()
task = [{"role": "user", "content": "이번 주말 오사카에 축제 하나요?"}]

SYSTEM = "당신은 여행 도우미다. 조회가 필요한 질문에는 반드시 알맞은 도구를 사용한다."


def tools(described: bool) -> list[dict]:
    """described=False면 이름·설명을 함께 지운다. 이름이 남으면 모델이
    이름에서 유추해 버려 절제 실험이 성립하지 않는다."""
    specs = [
        ("get_weather", "도시의 오늘 날씨를 조회한다"),
        ("calc_budget", "여행 예산을 계산한다"),
        ("event_calendar", "도시의 축제·행사 일정을 조회한다"),
        ("translate", "문장을 번역한다"),
        ("find_route", "이동 경로를 찾는다"),
    ]
    return [
        {"type": "function", "function": {
            "name": n if described else f"tool_{i}",
            "description": d if described else "도구",
            "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}}
        for i, (n, d) in enumerate(specs)
    ]


cases = [
    ("풀 하네스 (system + 도구 이름·설명)", SYSTEM, True),
    ("도구 이름·설명 제거", SYSTEM, False),
    ("system 제거", None, True),
    ("둘 다 제거", None, False),
]

for name, system, described in cases:
    messages = ([{"role": "system", "content": system}] if system else []) + task
    resp = completion(model=model, messages=messages, tools=tools(described))
    msg = resp.choices[0].message
    picked = msg.tool_calls[0].function.name if msg.tool_calls else "(도구 안 씀)"
    expected = "event_calendar" if described else "tool_2"
    h1(name)
    print(f"  결과: {picked}  (기대: {expected})")

h1("정리")
print("  모델은 그대로다. 잘 도는 에이전트와 헤매는 에이전트의 차이는 하네스에 있다.")
