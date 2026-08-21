"""응답 캐싱 — 같은 질문의 두 번째 호출은 공짜·즉시.

  docker compose exec lab python examples/02_litellm/05_cache.py

인메모리 캐시를 켜고 같은 요청을 두 번 보낸다. 두 번째는 API에 가지 않고
캐시에서 돌아온다 (지연 비교로 확인). FAQ·반복 질의가 많은 서비스에서
비용을 크게 줄이는 손잡이다.
"""

import time

import litellm
from litellm import completion
from litellm.caching.caching import Cache

from examples._shared import h1, pick_model

litellm.cache = Cache(type="local")  # 프로세스 안 인메모리 캐시

model = pick_model()
messages = [{"role": "user", "content": "오사카의 현재 인구를 아는 대로 답해 주세요."}]

h1("1회차 (API까지 다녀옴)")
t0 = time.perf_counter()
r1 = completion(model=model, messages=messages, caching=True)
t1 = time.perf_counter() - t0
print(f"  {t1:.2f}초")

h1("2회차 (같은 요청)")
t0 = time.perf_counter()
r2 = completion(model=model, messages=messages, caching=True)
t2 = time.perf_counter() - t0
print(f"  {t2:.3f}초")

h1("비교")
print(f"  {t1:.2f}초 → {t2:.3f}초. 같은 답인가: {r1.choices[0].message.content == r2.choices[0].message.content}")
