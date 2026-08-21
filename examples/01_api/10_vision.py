"""멀티모달 맛보기 — 이미지 한 장을 입력에 싣는다.

  docker compose exec lab python examples/01_api/10_vision.py

이미지도 결국 messages 안의 content 조각 하나이고, 실체는 base64 문자열이다.
공개 이미지를 직접 내려받아 data URL로 싣는다 (일부 호스트는 브라우저가 아닌
접근을 막으므로, User-Agent를 밝히고 받는 것까지가 실전이다).
"""

import base64
import urllib.request

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()

# 공개 위키미디어 이미지 (오사카성). Special:FilePath가 안정적인 진입점이다.
# UA 없는 요청·임의 썸네일 크기는 거절되므로, UA를 밝히고 표준 경로로 받는다.
image_url = (
    "https://commons.wikimedia.org/wiki/Special:FilePath/"
    "Osaka_Castle_02bs3200.jpg?width=500"
)
req = urllib.request.Request(image_url, headers={"User-Agent": "week06-agent-lab/1.0"})
with urllib.request.urlopen(req, timeout=30) as r:
    image_b64 = base64.b64encode(r.read()).decode()

h1("이미지 입력의 모양")
print(f"  원본 {len(image_b64) // 1024}KB(base64)가 data URL로 content 배열에 들어간다")
print("  content = [text 조각, image_url 조각] — 문자열이 아니라 배열이 된다")

messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "이 사진의 건물이 무엇인지 한 문장으로 답해 주세요."},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
            },
        ],
    }
]

h1("응답")
answer = completion(model=model, messages=messages).choices[0].message.content
print("  " + answer.strip()[:200])
