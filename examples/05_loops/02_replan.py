"""재계획 — 실행 중 막히면 실패 내용을 들고 계획으로 돌아간다.

  docker compose exec lab python examples/05_loops/02_replan.py

Plan-and-Execute의 약점은 계획이 틀렸을 때다. 실행 단계에서 도구가
실패하면(모르는 도시), 실패 기록을 첨부해 계획을 다시 세운다.
"계획 → 실행 → 막히면 재계획"이 Day 3 coding-agent의 복구 루프 원형이다.
"""

import json

from litellm import completion

from examples._shared import h1, mock_search, pick_model

model = pick_model()
question = "나라(奈良)의 관광지 알려줘."  # 나라는 목DB에 없는 도시 — 검색이 빈 결과를 낸다

def make_plan(extra: str = "") -> list[dict]:
    prompt = f"""도구 호출 계획을 JSON으로 세워라.
도구: search(city, category) — city는 반드시 실제 도시 이름 하나.
요청: {question}{extra}
형식: {{"steps": [{{"tool": "search", "args": {{"city": ..., "category": "관광"}}}}]}}"""
    resp = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)["steps"]


for attempt in range(1, 4):
    h1(f"계획 시도 {attempt}")
    extra = ""
    if attempt > 1:
        extra = f"\n주의: 직전 계획의 {failed!r} 검색이 빈 결과였다. 검색 가능한 도시: 오사카, 교토"
    plan = make_plan(extra)
    for s in plan:
        print(f"  계획: search({s['args']})")

    results = [(s, mock_search(s["args"].get("city", ""), s["args"].get("category"))) for s in plan]
    empty = [s for s, r in results if not r]
    if not empty:
        h1("실행 성공")
        for s, r in results:
            print(f"  {s['args'].get('city')} → {len(r)}곳: {[p['name'] for p in r]}")
        break
    failed = empty[0]["args"].get("city")
    print(f"  실행 실패: {failed!r} 검색 결과 0건 → 재계획으로")
else:
    print("재계획 한도 초과 — 사람에게 넘긴다 (이것도 설계다)")
