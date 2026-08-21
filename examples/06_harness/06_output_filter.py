"""출력 필터 — 비밀(API 키 등)이 응답에 새는 것을 마지막에 차단한다.

  docker compose exec lab python examples/06_harness/06_output_filter.py

키 없이 동작한다. 모델 출력이 사용자에게 나가기 직전, 정규식으로 비밀
패턴을 검사해 가리는 최후의 방어선. 인젝션이 앞 단을 뚫었더라도 유출은
여기서 멈춘다.
"""

import re

from examples._shared import h1

SECRET_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9\-_]{16,}"), "OpenAI 계열 키"),
    (re.compile(r"AIza[A-Za-z0-9\-_]{20,}"), "Google API 키"),
    (re.compile(r"sk-ant-[A-Za-z0-9\-_]{16,}"), "Anthropic 키"),
    (re.compile(r"\b\d{3}-\d{2}-\d{6}\b"), "주민등록번호 형태"),
]


def filter_output(text: str) -> tuple[str, list[str]]:
    """유출 패턴을 [가림]으로 치환하고, 잡힌 항목을 보고한다."""
    findings = []
    for pattern, label in SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(label)
            text = pattern.sub(f"[{label} — 가림]", text)
    return text, findings


# 사고 시나리오: 인젝션에 넘어간 모델이 환경 정보를 답에 실었다고 가정
leaked = (
    "네, 오사카 좋아요! 참고로 서버 설정은 OPENAI_API_KEY=sk-proj-Abc123XyzExample789 "
    "이고 담당자 번호는 800-12-345678 입니다."
)

h1("필터 전 (사고 출력)")
print("  " + leaked)

safe, findings = filter_output(leaked)
h1("필터 후")
print("  " + safe)
print(f"  잡힌 항목: {findings}")

h1("정리")
print("  출력 필터는 확률이 아니라 정규식이다. 마지막 관문은 결정적이어야 한다.")
