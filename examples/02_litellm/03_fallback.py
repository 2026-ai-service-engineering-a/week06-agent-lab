"""폴백 체인 — 주 모델이 죽으면 다음 모델이 이어받는 것을 관찰한다.

  docker compose exec lab python examples/02_litellm/03_fallback.py

일부러 존재하지 않는 모델을 1순위로 두고, 실제 모델을 폴백으로 단다.
1순위 실패 → 폴백 성공이 한 번의 completion() 안에서 일어난다.
프로덕션에서 장애·rate limit에 살아남는 기본기다.
"""

from litellm import completion

from examples._shared import h1, pick_model

real_model = pick_model()
broken_model = "openai/gpt-없는-모델"  # 반드시 실패하는 1순위

h1("시도 순서")
print(f"  1순위: {broken_model} (일부러 고장)")
print(f"  폴백 : {real_model}")

resp = completion(
    model=broken_model,
    messages=[{"role": "user", "content": "폴백으로 살아났다면 '폴백 성공'이라고만 답하세요."}],
    fallbacks=[real_model],
    num_retries=0,
)

h1("결과")
print(f"  실제 응답한 모델: {resp.model}")
print(f"  답: {resp.choices[0].message.content.strip()[:100]}")
