# CLAUDE.md

AI 서비스 엔지니어링 Track A 6주차 실습 랩. 예제 55종과 루프·하네스·MCP까지
완성된 여행 플래너 에이전트가 들어 있는 저장소다. 수업은 중간 버전을 오가지
않고 `main` 하나로 진행한다. 이 문서는 여기서 작업하는 AI 도구를 위한 가이드다.

## 실행·검증 (전부 컨테이너에서)

```sh
docker compose up --build -d
docker compose exec lab python check_env.py   # 키 점검 (키 없으면 안내 후 종료 1)
docker compose exec lab pytest                # 유닛 테스트 — 키·네트워크 불필요
docker compose exec lab python -m compileall -q examples agent tests  # 문법 검사
```

로컬 파이썬으로 돌리지 않는다. 테스트는 litellm.completion을 각본(mock)으로
갈아끼우므로 키 없이 통과해야 정상이다. 키가 필요한 예제를 수정했으면 최소한
compileall은 통과시킨다.

## Git 워크플로: git flow

- `develop`에서 `feature/*` 분기 → `develop` 머지. `main` 직접 커밋 금지
- **`main`이 곧 교재다.** 수업은 최종 상태 하나로 진행하므로, 교안이 인용하는
  코드·출력은 항상 `main` 기준이다
- 커밋하면서 진행한다. 논리 단위가 완결되면 바로 커밋, 제목은 영어 명령형 한 줄

## 코드 규칙

- 모델 문자열은 `agent/config.py`에만 둔다. 예제·본체 어디에도 하드코딩 금지
- 예제는 self-contained: `examples/_shared.py`·litellm·pydantic만 import
  (예외: `04_react/`는 에이전트 본체를 쓰며, ImportError 시 checkout 안내를 낸다)
- 각 예제 상단 docstring: 한 줄 요약 → 실행 명령 → 무엇을 보는가. 주석은 한국어
- 도구 실행은 `agent/tools.py`의 `run_tool` 관문 하나로만. 에러도 예외가 아니라
  결과(JSON의 error 키)로 돌려준다
- 새 기능에는 테스트를 함께 커밋한다. 테스트는 `tests/conftest.py`의
  ScriptedLLM·fake_response를 쓴다
- `.env`는 절대 커밋하지 않는다. `.env.sample`에는 키 이름만

## 5주차 랩과의 관계

`examples/01_api`·`02_litellm`·`03_tools` 31종과 `agent/tools.py`·`config.py`는
`week05-agent-lab`과 같은 내용이다. 한쪽을 고치면 다른 쪽도 함께 고친다.

## 강의 사이트와의 동기화

이 저장소의 내용이 바뀌면 강의 사이트 저장소(`ai_service_engineering-track_a`)의
6주차 교안도 함께 고친다. 예제 파일명·개수·실행 명령·출력 예시가 문서에 그대로
실려 있다.
