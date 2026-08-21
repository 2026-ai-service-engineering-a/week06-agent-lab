"""라우터 — 여러 모델(배포)에 요청을 분산한다.

  docker compose exec lab python examples/02_litellm/08_router.py

Router에 배포 목록을 주면, 같은 별명(alias)으로 호출해도 뒤에서 요청이
분산된다. 채워진 키가 2개 이상이면 프로바이더 사이에서, 1개면 같은 모델
2벌 사이에서 도는 것을 관찰한다. Day 3 coding-agent의 난이도별 모델
배정이 이 위에 선다.
"""

from litellm import Router

from examples._shared import available_models, h1

models = available_models()
# 배포 목록: 같은 별명 "travel-llm"에 여러 실모델을 단다
deployments = [
    {"model_name": "travel-llm", "litellm_params": {"model": m}}
    for m in (models if len(models) >= 2 else models * 2)
]

router = Router(model_list=deployments, routing_strategy="simple-shuffle")

h1(f"배포 {len(deployments)}개에 요청 6건 분산")
for i in range(6):
    resp = router.completion(
        model="travel-llm",
        messages=[{"role": "user", "content": f"{i}+1은? 숫자만."}],
    )
    print(f"  요청 {i + 1} → 처리한 모델: {resp.model}")

h1("정리")
print("  호출부는 'travel-llm' 하나만 안다. 어떤 실모델이 받을지는 라우터의 일이다.")
