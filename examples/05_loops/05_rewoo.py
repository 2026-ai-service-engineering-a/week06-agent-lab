"""ReWOO — 관찰 없이 플랜 한 번, 도구는 병렬로. 토큰 절약 특화 루프.

  docker compose exec lab python examples/05_loops/05_rewoo.py

ReAct는 도구 결과(observation)를 볼 때마다 LLM을 다시 부른다. ReWOO는
결과 자리를 #E1, #E2 변수로 비워 둔 채 계획을 한 번에 세우고, 도구를
전부(병렬로) 실행한 뒤, 마지막에 변수를 채워 한 번에 푼다.
중간 관찰이 없으므로 히스토리 재전송도 없다.
"""

import json

from litellm import completion

from examples._shared import h1, mock_budget, mock_search, pick_model

model = pick_model()
question = "오사카 2명 1박 여행: 관광지 목록과 예산을 알려줘."

plan_prompt = f"""도구 결과를 #E1, #E2 … 변수로 참조하는 계획을 JSON으로 세워라.
도구: search(city, category) / budget(nights, people). category는 관광|식당|null
요청: {question}
형식: {{"plan": [{{"var": "#E1", "tool": "search", "args": {{...}}}}, ...],
       "solve": "#E1과 #E2를 사용해 최종 답을 만드는 지시문"}}"""

resp = completion(
    model=model,
    messages=[{"role": "user", "content": plan_prompt}],
    response_format={"type": "json_object"},
)
blueprint = json.loads(resp.choices[0].message.content)

h1("① 플랜 (변수 자리가 비어 있다)")
for p in blueprint["plan"]:
    print(f"  {p['var']} = {p['tool']}({p['args']})")
print(f"  solve: {blueprint['solve'][:80]}…")

h1("② 도구 일괄 실행 (서로 의존이 없으니 병렬 가능)")
evidence = {}
for p in blueprint["plan"]:
    if p["tool"] == "search":
        out = mock_search(p["args"].get("city", ""), p["args"].get("category"))
    else:
        out = mock_budget(int(p["args"].get("nights", 1)), int(p["args"].get("people", 1)))
    evidence[p["var"]] = out
    print(f"  {p['var']} ← {json.dumps(out, ensure_ascii=False)[:70]}…")

h1("③ 변수를 채워 한 번에 풀기")
final = completion(
    model=model,
    messages=[{
        "role": "user",
        "content": f"{blueprint['solve']}\n\n증거: {json.dumps(evidence, ensure_ascii=False)}",
    }],
)
print("  " + final.choices[0].message.content.strip()[:250].replace("\n", "\n  "))

h1("정리")
print("  LLM 호출 2번 고정 + 도구 병렬. 대신 중간 결과를 보고 방향을 트는 능력은 없다.")
print("  적응력(ReAct) vs 비용(ReWOO) — 과제 성격이 루프를 고른다.")
