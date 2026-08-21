"""컨텍스트 팽창 — 스텝마다 히스토리가 부풀어 비용이 커지는 것을 그래프로.

  docker compose exec lab python examples/04_react/04_context_growth.py

ReAct는 매 스텝 지금까지의 모든 메시지를 다시 보낸다. 스텝별 입력 토큰을
막대로 그려 보면 우상향 계단이 나온다 — 느리고 비싼 이유의 실체이고,
05_loops의 Plan-and-Execute·ReWOO가 이 곡선을 공격한다.
"""

try:
    from agent import react
except ImportError:
    raise SystemExit("이 예제는 v0.3 이상에서 동작합니다: git checkout v0.3 (또는 main)")

from examples._shared import h1

result = react.run(
    "3박 4일 오사카, 예산 80만원. 관광지 검색하고 이동시간 보고 예산까지 계산해서 일정 짜줘.",
    max_steps=10,
    verbose=False,
)

h1("스텝별 입력(컨텍스트) 토큰")
peak = max(s.prompt_tokens for s in result.steps)
for i, s in enumerate(result.steps, 1):
    bar = "█" * max(1, round(s.prompt_tokens / peak * 40))
    what = s.tool or "최종답"
    print(f"  step{i:>2} {s.prompt_tokens:>6}tk {bar} {what}")

total = sum(s.prompt_tokens for s in result.steps)
h1("합계")
print(f"  이 한 번의 요청에 입력 토큰 총 {total:,}개 — 마지막 스텝 하나가 {peak:,}개")
print("  히스토리를 매번 다시 실어 나르는 값이다. 루프 설계가 곧 비용 설계다.")
