"""재시도와 타임아웃 — 흔들리는 네트워크 위에서 호출을 지키는 두 손잡이.

  docker compose exec lab python examples/02_litellm/04_retry_timeout.py

timeout: 이 시간 안에 답이 없으면 끊는다. num_retries: 끊기면 몇 번 다시
시도할지. 먼저 0.001초라는 불가능한 타임아웃으로 Timeout 에러를 재현하고,
정상 타임아웃 + 재시도 설정으로 성공하는 것을 본다.
"""

import litellm
from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()
messages = [{"role": "user", "content": "1+1은? 숫자만."}]

h1("타임아웃 재현 (timeout=0.001초)")
try:
    completion(model=model, messages=messages, timeout=0.001, num_retries=0)
    print("  !? 이 속도로 답이 왔을 리가")
except litellm.Timeout as e:
    print(f"  litellm.Timeout: {str(e)[:120]}")

h1("정상 설정 (timeout=30초, num_retries=2)")
resp = completion(model=model, messages=messages, timeout=30, num_retries=2)
print(f"  답: {resp.choices[0].message.content.strip()[:50]}")
print("  실패하면 최대 2회까지 자동으로 다시 시도한 뒤에야 에러를 낸다")
