"""LLM은 무상태 — 히스토리를 매번 다 보내야 대화가 이어진다.

  docker compose exec lab python examples/01_api/08_multiturn_stateless.py

서버는 이전 대화를 기억하지 않는다. "이어지는 대화"는 클라이언트가 지금까지의
메시지 전체를 매번 다시 보내서 만드는 착시다. 에이전트 루프의 컨텍스트가
스텝마다 부풀어 비싸지는 이유가 바로 여기에 있다.
"""

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()

first = [{"role": "user", "content": "제 이름은 김철수이고, 오사카 여행을 계획 중입니다."}]
reply1 = completion(model=model, messages=first).choices[0].message.content

h1("1턴: 자기소개")
print("  " + reply1.strip()[:150])

h1("2턴 (히스토리 없이): 제 이름이 뭐라고 했죠?")
alone = [{"role": "user", "content": "제 이름이 뭐라고 했죠?"}]
print("  " + completion(model=model, messages=alone).choices[0].message.content.strip()[:150])

h1("2턴 (히스토리 포함): 같은 질문")
with_history = first + [
    {"role": "assistant", "content": reply1},
    {"role": "user", "content": "제 이름이 뭐라고 했죠?"},
]
print("  " + completion(model=model, messages=with_history).choices[0].message.content.strip()[:150])

h1("정리")
print("  기억은 서버가 아니라 messages 배열에 있다. 이 배열의 관리가 곧 컨텍스트 엔지니어링이다.")
