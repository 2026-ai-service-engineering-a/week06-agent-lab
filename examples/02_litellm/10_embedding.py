"""임베딩 — 텍스트를 벡터로. 같은 인터페이스의 다른 출구.

  docker compose exec lab python examples/02_litellm/10_embedding.py

completion이 문장을 돌려준다면 embedding은 숫자 벡터를 돌려준다.
의미가 가까운 문장은 벡터도 가깝다 (코사인 유사도로 확인). Day 2
food-rag-agent의 의미 검색이 이 벡터 위에 선다. (Google 키 필요)
"""

import math
import os

from litellm import embedding

from examples._shared import EMBEDDING_MODEL, h1

if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit("임베딩 예제는 GEMINI_API_KEY가 필요합니다 (.env 참고)")

sentences = [
    "든든한 국물 요리가 먹고 싶다",
    "뜨끈한 탕이나 찌개가 당긴다",
    "오늘 주가가 크게 올랐다",
]

resp = embedding(model=EMBEDDING_MODEL, input=sentences)
vectors = [item["embedding"] for item in resp.data]

h1("벡터의 모양")
print(f"  문장 1개 → {len(vectors[0])}차원 벡터")
print(f"  앞 6개 값: {[round(v, 4) for v in vectors[0][:6]]}")


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


h1("코사인 유사도")
print(f"  '국물 요리' vs '탕이나 찌개' = {cosine(vectors[0], vectors[1]):.3f}  (의미가 가깝다)")
print(f"  '국물 요리' vs '주가 상승'   = {cosine(vectors[0], vectors[2]):.3f}  (멀다)")
