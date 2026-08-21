# week06-agent-lab — 루프와 하네스로 에이전트를 완성하는 실습 랩

AI 서비스 엔지니어링 Track A **6주차**의 교재 저장소입니다. 5주차에서 도구를
든 여행 플래너에 **루프**를 달아 처음으로 동작시키고, ReAct 너머의 루프들을
견준 뒤, **하네스**(인젝션 방어·권한·비용 가드)까지 얹어 완성합니다. 마지막에
도구를 표준 프로토콜로 주고받는 MCP를 맛봅니다.

- 강의 사이트: [6주차 교안](https://2026-ai-service-engineering-a.github.io/ai_service_engineering-track_a/course/session-06/)
- 앞선 랩: [week05-agent-lab](https://github.com/2026-ai-service-engineering-a/week05-agent-lab)
- 5주차 랩의 예제 31종이 그대로 들어 있고, 에이전트는 루프·하네스까지 실린
  완성본입니다. 중간 버전을 오갈 필요 없이 `main` 하나로 전부 실행합니다
- GPU 불필요, 로컬 Python 환경 불필요. Docker만 있으면 됩니다

## 시작하기

플랫폼 3사(Google AI Studio · OpenAI · Anthropic) 중 **키 하나만 있으면** 됩니다.
5주차에 쓰던 키를 그대로 쓰면 됩니다.

```bash
git clone https://github.com/2026-ai-service-engineering-a/week06-agent-lab.git
cd week06-agent-lab
cp .env.sample .env        # 편집기로 열어 키 채우기 (셋 중 하나면 됨)
docker compose up --build -d
docker compose exec lab python check_env.py    # 전부 ✓면 준비 끝
```

예제 실행과 테스트:

```bash
docker compose exec lab python examples/04_react/01_react_trace.py
docker compose exec lab python -m agent.main "3박 4일 오사카, 예산 80만원"
docker compose exec lab pytest                 # 유닛 테스트 (키 불필요)
```

## 예제 55종

`examples/` 아래 7개 폴더. 각 파일 상단 docstring에 "무엇을 보는가"와 실행
명령이 있습니다. 앞의 3폴더 31종은 5주차 몫이라 그대로 두었고(복습·참조용),
**이번 주에 수업에서 실행하는 것은 뒤의 4폴더 24종**입니다. 각 예제의 실행
결과와 해설은 강의 사이트의 6주차 교안에 있습니다.

| 폴더 | 주제 | 개수 | 주차 |
| --- | --- | --- | --- |
| `01_api/` | LLM API의 본질: 역할·토큰·스트리밍·무상태·비용 | 11종 | 5주차 |
| `02_litellm/` | 통합 레이어: 교체·폴백·캐시·라우터·임베딩 | 10종 | 5주차 |
| `03_tools/` | tool calling 심화: 스키마·검증·구조화 출력 | 10종 | 5주차 |
| `04_react/` | ReAct 루프: 트레이스·한도·절제·컨텍스트 팽창 | 4종 | **6주차** |
| `05_loops/` | ReAct 너머: Plan-Execute·재계획·Reflexion·ReWOO | 6종 | **6주차** |
| `06_harness/` | 하네스: 인젝션 방어·권한·경로 감금·budget guard | 10종 | **6주차** |
| `07_mcp/` | MCP 맛보기: 서버로 내어놓기(stdio·HTTP)·프로토콜 수신·루프 연결 | 4종 | **6주차** |

- 키 없이도 도는 예제: 경로 감금, 출력 필터, 비용 추정, budget guard,
  트레이스 로그, MCP 도구 목록 수신
- `04_react/` 4종은 에이전트 본체(`agent/react.py`)를 직접 사용합니다

## 여행 플래너 에이전트

`agent/` 패키지가 이번 주 예제에서 익힌 것을 실제로 조립한 결과물입니다.
5주차의 도구 위에 루프·평가·하네스가 차례로 물려 있습니다.

```bash
docker compose exec lab python -m agent.main --verbose "3박 4일 오사카, 예산 80만원"
docker compose exec lab python -m agent.main --max-cost 0.10 "3박 4일 오사카, 예산 80만원"
docker compose exec lab pytest        # 유닛 테스트 33개 (키 불필요)
```

## 저장소 구조

```plaintext
week06-agent-lab/
├── examples/            # 예제 55종 (7개 폴더, self-contained)
│   └── _shared.py       # 모델 선택 재노출 + 출력 헬퍼 + 여행 목데이터
├── agent/               # 여행 플래너 에이전트 본체
│   ├── config.py        # 모델 문자열이 사는 유일한 곳
│   ├── tools.py         # 검색·이동시간·예산 (pydantic 스키마, 5주차 몫)
│   ├── react.py         # ReAct 루프 + 트레이스
│   ├── reflexion.py     # 평가·재시도
│   ├── harness.py       # 경계 방어·budget guard·JSONL 트레이스
│   └── main.py          # CLI
├── tests/               # 유닛 테스트 — LLM은 각본(mock), 키·네트워크 불필요
├── check_env.py         # 키 유효성 + 패키지 버전 점검
├── docker-compose.yml   # lab 컨테이너 (bind mount, sleep infinity)
└── Dockerfile
```

## git 워크플로

git flow를 따릅니다: `develop`에서 `feature/*` 분기 → `develop` 머지.
`main`에 직접 커밋하지 않습니다. 커밋 메시지 제목은 영어 명령형 한 줄

## 문제 해결

| 증상 | 확인 |
| --- | --- |
| `docker: command not found` | Docker Desktop 실행 여부 |
| check_env 키 인증 실패 | `.env` 키 앞뒤 공백·따옴표, 충전 여부 |
| `.env` 수정이 반영 안 됨 | `docker compose up -d --force-recreate` |
| 모델 호출이 404 (NotFoundError) | 신규 키에서 구세대 모델이 막힌 경우. `agent/config.py`의 모델 문자열을 살아 있는 것으로 바꿉니다 |
