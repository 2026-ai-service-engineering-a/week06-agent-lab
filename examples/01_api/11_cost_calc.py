"""비용 계산 — 토큰 단가표로 호출 비용을 직접 계산해 본다.

  docker compose exec lab python examples/01_api/11_cost_calc.py

API 호출 없이 동작한다 (키 불필요). 비용 = 입력 토큰 × 입력 단가 + 출력 토큰
× 출력 단가. 단가표는 litellm이 내장하고 있다. 이 산수가 6주차 마지막의
budget guard(실행 전 추정·실행 중 상한)의 전부다.
"""

from litellm import get_model_info, token_counter

from agent.config import PROVIDERS
from examples._shared import h1

# 가상의 호출 1건: 여행 계획 요청 → 500토큰짜리 답
prompt = "3박 4일 오사카 여행 일정을 짜 주세요. 예산은 80만원입니다."
output_tokens = 500

h1("가정")
print(f"  입력: {prompt!r}")
print(f"  출력: {output_tokens} 토큰짜리 일정표라고 가정")

h1("모델별 비용 (litellm 내장 단가표)")
print(f"  {'모델':<32} {'입력단가/1M':>12} {'출력단가/1M':>12} {'이 호출':>12}")
for _env, model in PROVIDERS:
    info = get_model_info(model)
    in_price = info["input_cost_per_token"]
    out_price = info["output_cost_per_token"]
    in_tokens = token_counter(model="gpt-4o", text=prompt)  # 근사 토크나이저
    cost = in_tokens * in_price + output_tokens * out_price
    print(
        f"  {model:<32} ${in_price * 1e6:>10.2f} ${out_price * 1e6:>10.2f} ${cost:>11.6f}"
    )

h1("감각")
print("  호출 한 번은 티끌이지만, 에이전트는 루프다. 스텝 10번 × 부푸는 히스토리 ×")
print("  멀티 에이전트 N명이면 자릿수가 달라진다. 그래서 하네스에 지갑의 보험을 단다.")
