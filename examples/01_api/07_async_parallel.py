"""비동기 병렬 — 도시 5곳 동시 호출 vs 순차 호출의 소요 시간 비교.

  docker compose exec lab python examples/01_api/07_async_parallel.py

LLM 호출은 네트워크 대기가 대부분이라 병렬화 효과가 크다. asyncio를 몰라도
된다: acompletion + gather 패턴 하나면 멀티 에이전트의 "동시에 물어보기"가
전부 이 모양이다 (Day 3 coding-agent의 병렬 worker가 이 확장판).
"""

import asyncio
import time

from litellm import acompletion, completion

from examples._shared import h1, pick_model

model = pick_model()
cities = ["오사카", "교토", "도쿄", "삿포로", "후쿠오카"]


def ask(city: str) -> str:
    return f"{city}의 대표 음식 하나만 답해 주세요."


h1("순차 호출 (5회)")
t0 = time.perf_counter()
for city in cities:
    completion(model=model, messages=[{"role": "user", "content": ask(city)}])
seq = time.perf_counter() - t0
print(f"  {seq:.1f}초")


async def parallel() -> None:
    tasks = [
        acompletion(model=model, messages=[{"role": "user", "content": ask(city)}])
        for city in cities
    ]
    await asyncio.gather(*tasks)


h1("병렬 호출 (5회 동시)")
t0 = time.perf_counter()
asyncio.run(parallel())
par = time.perf_counter() - t0
print(f"  {par:.1f}초")

h1("비교")
print(f"  순차 {seq:.1f}초 → 병렬 {par:.1f}초 (약 {seq / par:.1f}배)")
