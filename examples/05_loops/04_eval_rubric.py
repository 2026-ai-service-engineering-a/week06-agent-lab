"""루브릭 실험 — 평가 기준을 바꾸면 '좋은 결과'가 달라진다.

  docker compose exec lab python examples/05_loops/04_eval_rubric.py

같은 초안 2개를 두 루브릭(정보 밀도 우선 vs 감성 우선)으로 채점해 승자가
뒤집히는 것을 본다. Reflexion의 품질은 생성자가 아니라 평가 기준 설계에서
나온다 — 무엇을 좋다고 정의할 것인가가 엔지니어링의 몫이다.
"""

import json

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()

drafts = {
    "초안 A (정보형)": "오사카성 입장료는 600엔, 도톤보리까지 지하철 12분. 구로몬 시장 회덮밥이 1500엔으로 가성비가 좋았다. 숙소는 난바역 도보 5분 거리를 추천한다.",
    "초안 B (감성형)": "노을 지는 오사카성 앞에서 한참을 서 있었다. 도톤보리의 불빛이 강물에 번지고, 낯선 도시의 소음마저 다정하게 느껴지는 밤이었다.",
}

rubrics = {
    "루브릭 ①: 정보 밀도": "여행 정보(가격·시간·위치)가 구체적일수록 높은 점수. 0~10점.",
    "루브릭 ②: 감성 전달": "장면이 그려지고 여운이 남을수록 높은 점수. 0~10점.",
}

for rubric_name, rubric in rubrics.items():
    h1(rubric_name)
    for draft_name, draft in drafts.items():
        resp = completion(
            model=model,
            messages=[{
                "role": "user",
                "content": f"글: {draft}\n기준: {rubric}\nJSON으로만: {{\"score\": n, \"reason\": \"한 줄\"}}",
            }],
            response_format={"type": "json_object"},
            temperature=0,
        )
        result = json.loads(resp.choices[0].message.content)
        print(f"  {draft_name}: {result['score']}점 — {result['reason']}")

h1("정리")
print("  같은 글의 점수가 루브릭에 따라 뒤집힌다. 평가자를 두는 순간,")
print("  '무엇이 좋은 결과인가'의 정의가 코드에 박제된다. 신중하게 쓸 것.")
