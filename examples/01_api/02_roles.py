"""system/user/assistant 역할 — 같은 질문, 다른 system이 답을 어떻게 바꾸는가.

  docker compose exec lab python examples/01_api/02_roles.py

system은 "누구로서 답할 것인가"를 정한다. 에이전트의 성격·규칙·말투는
전부 이 자리에 실린다 (6주차의 하네스에서 이 자리가 핵심이 된다).
"""

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()
question = "오사카 여행에서 꼭 먹어야 할 것 하나만 추천해 주세요."

personas = {
    "(system 없음)": None,
    "미슐랭 심사위원": "당신은 미슐랭 심사위원입니다. 미식가의 기준으로 깐깐하게 답하세요.",
    "초등학생 눈높이": "당신은 초등학생에게 설명하는 선생님입니다. 아주 쉬운 말로 답하세요.",
    "JSON 응답기": "반드시 {\"추천\": ..., \"이유\": ...} 형태의 JSON으로만 답하세요.",
}

for name, system in personas.items():
    messages = [{"role": "user", "content": question}]
    if system:
        messages.insert(0, {"role": "system", "content": system})
    answer = completion(model=model, messages=messages).choices[0].message.content
    h1(f"system = {name}")
    print(answer.strip()[:300])
