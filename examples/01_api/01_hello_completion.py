"""최소 호출 — 요청에 무엇이 실려 가고, 응답에 무엇이 담겨 오는가.

  docker compose exec lab python examples/01_api/01_hello_completion.py

LLM API의 전부는 이것이다: messages 리스트를 보내면 choices가 돌아온다.
응답 JSON 원문을 그대로 보면, 이후 모든 개념(role·토큰·비용·tool call)이
이 구조 위의 변주임을 알 수 있다.
"""

import json

from litellm import completion

from examples._shared import h1, pick_model

model = pick_model()

request = {
    "model": model,
    "messages": [{"role": "user", "content": "안녕하세요! 한 문장으로 인사해 주세요."}],
}

h1("요청 (우리가 보내는 것)")
print(json.dumps(request, ensure_ascii=False, indent=2))

response = completion(**request)

h1("응답 원문 (모델이 돌려주는 것 전체)")
print(response.model_dump_json(indent=2))

h1("그중 실제로 쓰는 것")
print(f"  choices[0].message.content = {response.choices[0].message.content!r}")
print(f"  usage = 입력 {response.usage.prompt_tokens} 토큰 + 출력 {response.usage.completion_tokens} 토큰")
