"""루프 비용 비교 — 같은 과제를 ReAct 방식 vs Plan-and-Execute로 풀어 계산서를 나란히.

  docker compose exec lab python examples/05_loops/06_loop_cost_compare.py

미니 ReAct(히스토리 누적·매 스텝 재전송)와 Plan-and-Execute(호출 2번)를
같은 여행 과제에 돌리고 호출 수·토큰·비용을 표로 비교한다.
"""

import json

from litellm import completion, completion_cost

from examples._shared import h1, mock_budget, mock_search, pick_model

model = pick_model()
question = "오사카 1박 2명: 관광지 찾고 예산 계산해서 정리해줘."

TOOLS = [
    {"type": "function", "function": {"name": "search", "description": "장소 검색",
     "parameters": {"type": "object", "properties": {"city": {"type": "string"}, "category": {"type": "string"}}, "required": ["city"]}}},
    {"type": "function", "function": {"name": "budget", "description": "예산 계산",
     "parameters": {"type": "object", "properties": {"nights": {"type": "integer"}, "people": {"type": "integer"}}, "required": ["nights", "people"]}}},
]


def run_tool(name: str, args: dict):
    if name == "search":
        return mock_search(args.get("city", ""), args.get("category"))
    return mock_budget(int(args.get("nights", 1)), int(args.get("people", 1)))


def tally(resp, ledger):
    ledger["calls"] += 1
    ledger["in"] += resp.usage.prompt_tokens
    ledger["out"] += resp.usage.completion_tokens
    ledger["cost"] += completion_cost(completion_response=resp)


# ── A. 미니 ReAct ──
react_ledger = {"calls": 0, "in": 0, "out": 0, "cost": 0.0}
messages = [{"role": "user", "content": question}]
for _ in range(8):
    resp = completion(model=model, messages=messages, tools=TOOLS)
    tally(resp, react_ledger)
    msg = resp.choices[0].message
    if not msg.tool_calls:
        break
    messages.append(msg.model_dump())
    for c in msg.tool_calls:
        out = run_tool(c.function.name, json.loads(c.function.arguments))
        messages.append({"role": "tool", "tool_call_id": c.id, "content": json.dumps(out, ensure_ascii=False)})

# ── B. Plan-and-Execute ──
pe_ledger = {"calls": 0, "in": 0, "out": 0, "cost": 0.0}
resp = completion(
    model=model,
    messages=[{"role": "user", "content": f"도구 호출 계획 JSON: search(city,category)/budget(nights,people)\n요청: {question}\n형식: {{\"steps\":[{{\"tool\":...,\"args\":{{...}}}}]}}"}],
    response_format={"type": "json_object"},
)
tally(resp, pe_ledger)
observations = [
    {"step": s, "result": run_tool(s["tool"], s["args"])}
    for s in json.loads(resp.choices[0].message.content)["steps"]
]
resp = completion(
    model=model,
    messages=[{"role": "user", "content": f"요청: {question}\n결과: {json.dumps(observations, ensure_ascii=False)}\n정리해줘."}],
)
tally(resp, pe_ledger)

h1("계산서")
print(f"  {'루프':<20} {'LLM호출':>7} {'입력tk':>8} {'출력tk':>8} {'비용':>11}")
for name, ledger in [("ReAct", react_ledger), ("Plan-and-Execute", pe_ledger)]:
    print(f"  {name:<20} {ledger['calls']:>7} {ledger['in']:>8,} {ledger['out']:>8,} ${ledger['cost']:>10.6f}")

h1("정리")
print("  같은 과제, 같은 모델, 같은 도구 — 루프 설계만 달랐다.")
