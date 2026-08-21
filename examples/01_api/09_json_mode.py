"""JSON 강제 — 응답을 JSON으로 받는 방법과, 그냥 부탁했을 때 깨지는 케이스.

  docker compose exec lab python examples/01_api/09_json_mode.py

서비스 코드는 문장이 아니라 구조를 원한다. "JSON으로 답해줘"라는 부탁은
마크다운 코드펜스·사족이 섞여 파싱이 깨지기 일쑤다. response_format으로
강제하는 것이 첫걸음이고, 더 단단한 방법(도구 호출 응용)은
03_tools/09_structured_output.py에서 잇는다.
"""

import json

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()
ask = "오사카 명소 2곳을 이름(name)과 입장료(fee)를 가진 JSON 배열로 알려 주세요."

h1("그냥 부탁만 한 경우")
raw = completion(model=model, messages=[{"role": "user", "content": ask}])
text = raw.choices[0].message.content
print("  응답 원문 (앞 200자):")
print("  " + text[:200].replace("\n", "\n  "))
try:
    json.loads(text)
    print("  → 운 좋게 파싱 성공 (매번 성공한다는 보장이 없다)")
except json.JSONDecodeError as e:
    print(f"  → json.loads 실패: {e}")

h1("response_format으로 강제한 경우")
forced = completion(
    model=model,
    messages=[{"role": "user", "content": ask}],
    response_format={"type": "json_object"},
)
text = forced.choices[0].message.content
data = json.loads(text)  # 이제 파싱이 계약이다
print("  " + json.dumps(data, ensure_ascii=False)[:200])
print("  → json.loads 통과. 이 위에 pydantic 검증을 얹으면 타입까지 계약이 된다")
