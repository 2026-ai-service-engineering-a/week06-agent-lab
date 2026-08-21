"""3사 나란히 — 같은 프롬프트의 응답·지연·비용을 표로 비교한다.

  docker compose exec lab python examples/02_litellm/02_three_way_compare.py

"어느 모델을 쓸까"는 감이 아니라 측정의 문제다. 응답 품질은 눈으로,
지연과 비용은 숫자로 나란히 놓는다. (채워진 키의 프로바이더만 참여)
"""

import time

from litellm import completion, completion_cost

from examples._shared import available_models, h1

prompt = "오사카 1일 코스를 아침·점심·저녁 세 줄로만 짜 주세요."

h1("비교 표")
print(f"  {'모델':<32} {'지연':>6} {'입력tk':>7} {'출력tk':>7} {'비용':>11}")

answers = {}
for model in available_models():
    t0 = time.perf_counter()
    resp = completion(model=model, messages=[{"role": "user", "content": prompt}])
    dt = time.perf_counter() - t0
    cost = completion_cost(completion_response=resp)
    answers[model] = resp.choices[0].message.content.strip()
    print(
        f"  {model:<32} {dt:>5.1f}s {resp.usage.prompt_tokens:>7} "
        f"{resp.usage.completion_tokens:>7} ${cost:>10.6f}"
    )

for model, answer in answers.items():
    h1(f"{model}의 답")
    print("  " + answer[:250].replace("\n", "\n  "))
