"""temperature — 0과 1로 같은 질문을 5번씩. 산포가 어떻게 달라지는가.

  docker compose exec lab python examples/01_api/05_temperature.py

temperature는 다음 토큰을 고를 때의 무작위성이다. 0이면 매번 거의 같은 답,
1이면 답이 흩어진다. 에이전트의 도구 선택·검증처럼 재현성이 필요한 자리는
낮게, 아이디어 생성은 높게 쓴다.
"""

from litellm import completion

from examples._shared import available_models, h1

# Gemini 3+는 temperature를 시스템 지침으로 옮기는 중이라(호출마다 경고),
# 이 파라미터의 시연은 다른 프로바이더를 우선한다. 같은 파라미터도
# 프로바이더마다 지원 상태가 다르다는 것 자체가 이 세션의 관찰거리다.
models = available_models()
model = next((m for m in models if not m.startswith("gemini/")), models[0])
print(f"(시연 모델: {model})")
question = "여행지 하나를 도시 이름만으로 추천해 주세요."

for temp in (0.0, 1.0):
    h1(f"temperature = {temp}")
    answers = []
    for i in range(5):
        answer = completion(
            model=model,
            messages=[{"role": "user", "content": question}],
            temperature=temp,
        ).choices[0].message.content.strip()
        answers.append(answer)
        print(f"  {i + 1}회: {answer[:60]}")
    print(f"  → 서로 다른 답 {len(set(answers))}종")
