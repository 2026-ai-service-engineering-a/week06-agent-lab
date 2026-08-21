"""모델 선택: 환경 변수에 채워진 API 키를 보고 사용할 모델을 고른다.

세 플랫폼 중 하나만 있어도 과정 전체가 동작한다. 순서는 사전 준비 가이드의
권장 순서(Google → OpenAI → Anthropic)를 따른다. 모델 문자열만 바꾸면
프로바이더가 교체되는 것이 LiteLLM의 핵심이므로, 모델 이름은 이 파일
한 곳에만 둔다.
"""

import os

# (환경 변수 이름, litellm 모델 문자열)
PROVIDERS: list[tuple[str, str]] = [
    ("GEMINI_API_KEY", "gemini/gemini-3.5-flash-lite"),
    ("OPENAI_API_KEY", "openai/gpt-5.4-nano"),
    ("ANTHROPIC_API_KEY", "anthropic/claude-haiku-4-5"),
]

# 의미 검색 예제용 임베딩 모델 (Google 키 필요)
EMBEDDING_MODEL = "gemini/gemini-embedding-001"

NO_KEY_MESSAGE = (
    "API 키가 없습니다. 저장소 루트에서:\n"
    "  cp .env.sample .env\n"
    "  (편집기로 .env를 열어 셋 중 하나 이상 채우기)\n"
    "  docker compose up -d --force-recreate\n"
    "자세한 절차는 README의 시작하기 참고"
)


def available_models() -> list[str]:
    """키가 채워진 프로바이더의 모델 문자열 목록 (권장 순서)."""
    return [model for env_var, model in PROVIDERS if os.environ.get(env_var)]


def pick_model() -> str:
    """사용할 기본 모델 하나. 키가 하나도 없으면 안내와 함께 종료."""
    models = available_models()
    if not models:
        raise SystemExit(NO_KEY_MESSAGE)
    return models[0]
