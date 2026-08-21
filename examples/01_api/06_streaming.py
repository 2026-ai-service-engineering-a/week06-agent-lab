"""스트리밍 — 델타 청크가 오는 모양을 원문으로 관찰한다.

  docker compose exec lab python examples/01_api/06_streaming.py

stream=True면 완성된 답 대신 조각(delta)이 흘러온다. 채팅 UI가 글자를
한 글자씩 찍는 것의 실체다. 각 청크의 원문 몇 개를 그대로 보고,
조각을 이어붙여 전체 답을 복원한다.
"""

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()

stream = completion(
    model=model,
    messages=[{"role": "user", "content": "오사카를 한 문장으로 소개해 주세요."}],
    stream=True,
)

h1("처음 5개 청크 원문")
collected = []
for i, chunk in enumerate(stream):
    delta = chunk.choices[0].delta.content or ""
    collected.append(delta)
    if i < 5:
        print(f"  chunk[{i}] delta={delta!r}")

h1("조각을 이어붙인 전체 답")
print("  " + "".join(collected).strip())
print(f"  (총 {len(collected)}개 청크)")
