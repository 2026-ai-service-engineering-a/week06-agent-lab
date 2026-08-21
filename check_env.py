"""환경 점검: 채워진 키로 실제 호출 1회씩 해 보고 결과를 표로 보여준다.

  docker compose exec lab python check_env.py

확인하는 것 3가지:
  1) 키 유효성 — 프로바이더별로 아주 짧은 호출 1회 (통과하면 그 키는 준비 끝)
  2) 사용 가능한 모델 — 이 랩이 기본으로 쓰는 모델 문자열
  3) 컨테이너 내 패키지 버전 — 재현 문의 때 첨부할 정보
"""

import platform
import sys
from importlib.metadata import version

import litellm
import pydantic
import pytest

from agent.config import NO_KEY_MESSAGE, PROVIDERS, available_models


def try_call(model: str) -> tuple[bool, str]:
    """1토큰짜리 호출로 키가 실제로 동작하는지 확인한다."""
    try:
        litellm.completion(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        return True, "OK"
    except Exception as e:  # 어떤 프로바이더 에러든 한 줄로 요약해 보여준다
        return False, f"{type(e).__name__}: {str(e)[:80]}"


def main() -> int:
    print("=== 패키지 버전 ===")
    print(f"  python   {platform.python_version()}")
    print(f"  litellm  {version('litellm')}")
    print(f"  pydantic {pydantic.VERSION}")
    print(f"  pytest   {pytest.__version__}")
    print()

    if not available_models():
        print(NO_KEY_MESSAGE)
        return 1

    print("=== 키 점검 (채워진 키만, 프로바이더별 1회 호출) ===")
    import os

    ok_any = False
    for env_var, model in PROVIDERS:
        if not os.environ.get(env_var):
            print(f"  {env_var:<20} (비어 있음 — 건너뜀)")
            continue
        ok, detail = try_call(model)
        ok_any = ok_any or ok
        mark = "✓" if ok else "✗"
        print(f"  {env_var:<20} {mark} {model} — {detail}")

    print()
    if ok_any:
        print("준비 끝. 예제 실행: docker compose exec lab python examples/01_api/01_hello_completion.py")
        return 0
    print("호출에 전부 실패했습니다. .env의 키 앞뒤 공백·따옴표, 충전 여부를 확인하세요.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
