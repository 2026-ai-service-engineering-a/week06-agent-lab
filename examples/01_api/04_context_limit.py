"""컨텍스트 한도 — 일부러 초과시켜 어떤 에러가 나는지 재현한다.

  docker compose exec lab python examples/01_api/04_context_limit.py

모델마다 입력 토큰 상한이 있다. 초과분은 "잘리는" 것이 아니라 요청 자체가
거부된다. 에이전트 루프에서 히스토리가 무한히 자라면 정확히 이 에러를 만난다
(6주차 랩의 04_react/04_context_growth.py에서 다시 본다).

채워진 키 중 한도가 가장 작은 모델을 고른다. 토크나이저 근사 오차가 있어도
확실히 넘도록 한도의 1.5배를 보낸다 (요청은 거부되므로 과금되지 않는다).
"""

from litellm import completion, get_model_info, token_counter

from examples._shared import available_models, h1

# 한도가 작은 모델일수록 재현이 싸고 빠르다
model = min(available_models(), key=lambda m: get_model_info(m)["max_input_tokens"])
limit = get_model_info(model)["max_input_tokens"]

h1(f"{model}의 입력 한도")
print(f"  max_input_tokens = {limit:,}")

# 한도의 1.5배를 만든다 (근사 토크나이저 오차를 감안한 여유)
chunk = "오사카 여행 계획. " * 1000
chunk_tokens = token_counter(model=model, text=chunk)
text = chunk * (int(limit * 1.5) // chunk_tokens + 1)
n_tokens = token_counter(model=model, text=text)

h1("일부러 초과 요청")
print(f"  보내는 입력: 약 {n_tokens:,} 토큰 (한도의 {n_tokens / limit:.1f}배)")

try:
    completion(model=model, messages=[{"role": "user", "content": text}], max_tokens=10)
    print("  !? 통과했습니다 — 프로바이더가 조용히 잘랐을 수 있습니다 (더 위험)")
except Exception as e:
    h1("에러 원문")
    print(f"  {type(e).__name__}")
    print(f"  {str(e)[:300]}")
