"""사전 비용 추정 — 실행 전에 예상 토큰·비용을 계산해 본다.

  docker compose exec lab python examples/06_harness/08_budget_estimate.py

키 없이 동작한다. 입력은 토크나이저로 세고, 출력은 스텝 수 × 스텝당 예상
출력으로 잡아 상한 시나리오를 만든다. Day 3 coding-agent의 "실행 전 비용
리포트 → 승인 게이트"가 정확히 이 계산이다.
"""

from litellm import get_model_info, token_counter

from agent.config import PROVIDERS
from examples._shared import h1

question = "3박 4일 오사카 여행, 예산 80만원으로 일정 짜줘."
system = "당신은 여행 플래너다. 검색·이동시간·예산 도구를 사용해 근거 있는 일정을 만든다."

# 에이전트 루프의 가정: 최대 8스텝, 스텝당 출력 400토큰, 히스토리는 스텝마다 커진다
MAX_STEPS = 8
OUT_PER_STEP = 400

base_in = token_counter(model="gpt-4o", text=system + question)

h1("모델별 상한 시나리오 (8스텝을 다 쓴 경우)")
print(f"  {'모델':<32} {'입력tk(누적)':>12} {'출력tk':>8} {'예상 상한':>12}")
for _env, model in PROVIDERS:
    info = get_model_info(model)
    total_in = 0
    context = base_in
    for _step in range(MAX_STEPS):
        total_in += context
        context += OUT_PER_STEP + 200  # 이번 스텝의 출력 + 도구 결과가 다음 컨텍스트에 쌓인다
    total_out = OUT_PER_STEP * MAX_STEPS
    cost = total_in * info["input_cost_per_token"] + total_out * info["output_cost_per_token"]
    print(f"  {model:<32} {total_in:>12,} {total_out:>8,} ${cost:>11.4f}")

h1("읽는 법")
print("  실제로는 더 일찍 끝나는 일이 많다 — 이것은 '최악에 얼마까지 나가는가'다.")
print("  상한이 계산되면 게이트를 세울 수 있다: 다음 예제(09_budget_guard).")
