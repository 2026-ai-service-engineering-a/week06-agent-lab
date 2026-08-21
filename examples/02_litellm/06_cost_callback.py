"""비용 콜백 — 호출마다 토큰·비용을 자동 집계한다.

  docker compose exec lab python examples/02_litellm/06_cost_callback.py

호출부에 지표 코드를 심지 않아도, 콜백 하나 등록하면 모든 completion의
비용이 흘러들어온다. 6주차의 budget guard가 정확히 이 자리에서
누적 비용을 지켜본다.
"""

import litellm
from litellm import completion

from examples._shared import h1, pick_model

ledger = {"calls": 0, "cost": 0.0}


def track_cost(kwargs, completion_response, start_time, end_time):
    """litellm이 성공한 호출마다 불러 주는 훅."""
    ledger["calls"] += 1
    ledger["cost"] += kwargs.get("response_cost") or 0.0


litellm.success_callback = [track_cost]

model = pick_model()
questions = ["1+1은?", "오사카는 어느 나라?", "라멘 한 그릇 평균 가격은?"]

for q in questions:
    completion(model=model, messages=[{"role": "user", "content": q}])
    print(f"  호출: {q!r}")

h1("장부")
print(f"  호출 {ledger['calls']}건, 누적 비용 ${ledger['cost']:.6f}")
print("  호출부는 비용을 몰라도 된다. 장부는 콜백이 쓴다 — 관심사의 분리")
