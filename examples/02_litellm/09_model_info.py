"""모델 메타데이터 — 컨텍스트 한도·단가를 코드로 조회한다.

  docker compose exec lab python examples/02_litellm/09_model_info.py

API 호출 없이 동작한다 (키 불필요). litellm은 모델별 한도·단가표를
내장한다. "이 입력이 들어가는가", "이 호출은 얼마인가"를 코드가 미리
판단할 수 있다는 뜻이고, budget guard의 추정이 여기서 나온다.
"""

from litellm import get_model_info

from agent.config import EMBEDDING_MODEL, PROVIDERS
from examples._shared import h1

h1("이 랩이 쓰는 모델들")
print(f"  {'모델':<32} {'입력한도':>10} {'출력한도':>8} {'입력$/1M':>9} {'출력$/1M':>9}")
for _env, model in [*PROVIDERS, ("GEMINI_API_KEY", EMBEDDING_MODEL)]:
    info = get_model_info(model)
    print(
        f"  {model:<32} {info['max_input_tokens'] or 0:>10,} {info.get('max_output_tokens') or 0:>8,} "
        f"{(info['input_cost_per_token'] or 0) * 1e6:>9.2f} {(info['output_cost_per_token'] or 0) * 1e6:>9.2f}"
    )

h1("읽는 법")
print("  같은 '한 호출'이라도 모델에 따라 단가가 다르다. 싼 모델로 충분한 일과")
print("  비싼 모델이 필요한 일을 가르는 것 — 그것이 Day 3의 모델 라우팅이다.")
