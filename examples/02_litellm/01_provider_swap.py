"""프로바이더 교체 — 모델 문자열만 바꿔 3사를 오간다.

  docker compose exec lab python examples/02_litellm/01_provider_swap.py

호출 코드는 한 글자도 바뀌지 않는다. 바뀌는 것은 model= 문자열뿐.
이것이 LiteLLM을 쓰는 이유의 전부이고, 이후 모든 예제·에이전트가
이 통일 인터페이스 위에 선다. (.env에 채운 키의 프로바이더만 시도한다)
"""

from litellm import completion

from examples._shared import available_models, h1

models = available_models()
question = "당신은 어느 회사의 어떤 모델입니까? 한 문장으로."

if len(models) < 2:
    print(f"키가 {len(models)}개뿐이라 교체 시연은 한 칸짜리입니다. (그래도 코드는 같다)")

for model in models:
    h1(model)
    answer = completion(
        model=model, messages=[{"role": "user", "content": question}]
    ).choices[0].message.content
    print("  " + answer.strip()[:200])
