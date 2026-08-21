"""Plan-and-Execute — 계획을 먼저 세우고, 그다음 순차 실행한다.

  docker compose exec lab python examples/05_loops/01_plan_execute.py

ReAct가 한 스텝씩 더듬는다면, 이 루프는 LLM 호출 1번으로 전체 계획을 뽑고
도구 실행은 LLM 없이 돌린 뒤, 마지막에 1번 더 불러 종합한다.
LLM 호출 2번 고정 — 컨텍스트 팽창 곡선이 아예 생기지 않는다.
"""

import json

from litellm import completion

from examples._shared import h1, mock_budget, mock_search, pick_model

model = pick_model()
question = "1박 2일 오사카, 2명, 관광지랑 예산 정리해줘."

# ① 계획: 사용할 도구 호출 목록을 JSON으로 한 번에 뽑는다
plan_prompt = f"""다음 요청을 처리할 도구 호출 계획을 JSON으로 세워라.
사용 가능한 도구:
- search(city, category): 장소 검색. category는 관광|식당|null
- budget(nights, people): 예산 계산

요청: {question}
형식: {{"steps": [{{"tool": "search", "args": {{...}}}}, ...]}}"""

resp = completion(
    model=model,
    messages=[{"role": "user", "content": plan_prompt}],
    response_format={"type": "json_object"},
)
plan = json.loads(resp.choices[0].message.content)["steps"]

h1("① 계획 (LLM 호출 1번)")
for i, step in enumerate(plan, 1):
    print(f"  {i}. {step['tool']}({step['args']})")

# ② 실행: LLM 없이 도구만 돈다
h1("② 실행 (LLM 호출 0번)")
observations = []
for step in plan:
    if step["tool"] == "search":
        out = mock_search(step["args"].get("city", ""), step["args"].get("category"))
    else:
        out = mock_budget(int(step["args"].get("nights", 1)), int(step["args"].get("people", 1)))
    observations.append({"step": step, "result": out})
    print(f"  {step['tool']} → {json.dumps(out, ensure_ascii=False)[:80]}…")

# ③ 종합: 결과를 모아 한 번에 답을 만든다
final = completion(
    model=model,
    messages=[
        {
            "role": "user",
            "content": f"요청: {question}\n도구 결과: {json.dumps(observations, ensure_ascii=False)}\n"
            "이 결과만 근거로 최종 답을 정리해라.",
        }
    ],
)
h1("③ 종합 (LLM 호출 1번)")
print("  " + final.choices[0].message.content.strip()[:300].replace("\n", "\n  "))

h1("정리")
print(f"  LLM 호출 총 2번 (ReAct였다면 도구 {len(plan)}개 + 최종답 = {len(plan) + 1}번 이상)")
