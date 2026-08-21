"""Reflexion — 생성 결과를 평가자가 채점하고, 미달이면 피드백과 함께 재시도.

  docker compose exec lab python examples/05_loops/03_reflexion.py

생성자와 평가자를 분리한다. 평가자는 루브릭(기준표)으로 점수와 피드백을
JSON으로 내고, 기준 미달이면 피드백을 붙여 다시 생성한다.
"한 번에 잘 쓰기"보다 "고칠 점을 알고 다시 쓰기"가 쉽다는 사실을 이용한다.
"""

import json

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()
task = "오사카 여행을 다녀와서 가족 단톡방에 올릴 후기 3문장을 써줘."

RUBRIC = """다음 기준으로 채점하라 (각 0~10, JSON으로만 답):
- specific: 구체적 장소·음식 이름이 들어갔는가
- tone: 가족 단톡방에 맞는 말투인가
- length: 정확히 3문장인가
형식: {"specific": n, "tone": n, "length": n, "feedback": "한 줄 개선점"}"""


def generate(feedback: str | None) -> str:
    prompt = task if not feedback else f"{task}\n직전 시도에 대한 평가: {feedback}\n이를 반영해 다시."
    return completion(model=model, messages=[{"role": "user", "content": prompt}]).choices[0].message.content.strip()


def evaluate(text: str) -> dict:
    resp = completion(
        model=model,
        messages=[{"role": "user", "content": f"글: {text}\n\n{RUBRIC}"}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)


feedback = None
for attempt in range(1, 4):
    draft = generate(feedback)
    score = evaluate(draft)
    total = score["specific"] + score["tone"] + score["length"]
    h1(f"시도 {attempt} — 평가 {total}/30")
    print("  " + draft[:200].replace("\n", "\n  "))
    print(f"  채점: {score}")
    if total >= 24:
        print("  → 통과 기준(24) 도달, 종료")
        break
    feedback = score["feedback"]
    print(f"  → 미달. 피드백을 들고 재시도: {feedback!r}")
