"""rate limit — 일부러 한도를 맞고, 백오프로 살아나는 과정을 본다.

  docker compose exec lab python examples/02_litellm/07_rate_limit.py

무료 티어에서 빠른 연속 호출은 금방 429(RateLimitError)를 맞는다.
맞으면 잠시 기다렸다가(지수 백오프) 다시 시도하는 것이 표준 대응이다.
유료 티어라 한도를 못 맞으면, 백오프 코드가 그냥 통과하는 것을 확인하면 된다.
"""

import time

import litellm
from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()


def with_backoff(messages, max_attempts=4):
    """429를 만나면 1초 → 2초 → 4초 … 기다렸다가 재시도한다."""
    for attempt in range(max_attempts):
        try:
            return completion(model=model, messages=messages, num_retries=0)
        except litellm.RateLimitError:
            wait = 2**attempt
            print(f"    429! {wait}초 백오프 후 재시도 ({attempt + 1}/{max_attempts})")
            time.sleep(wait)
    raise SystemExit("백오프로도 못 살아났습니다. 잠시 뒤 다시 실행해 보세요.")


h1("연속 15회 빠른 호출 (한도를 만나러 간다)")
for i in range(15):
    with_backoff([{"role": "user", "content": f"{i}+1은? 숫자만."}])
    print(f"  {i + 1}회 성공")

h1("정리")
print("  한도는 장애가 아니라 일상이다. 백오프는 에이전트 루프의 기본 장비다.")
