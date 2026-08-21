"""ReAct 트레이스 — 완성본 에이전트를 돌리며 reasoning→action→observation을 읽는다.

  docker compose exec lab python examples/04_react/01_react_trace.py

여행 플래너 에이전트(agent/)를 verbose로 돌려, 루프의 한 바퀴 한 바퀴가
어떤 모양인지 트레이스로 관찰한다. 에이전트를 이해한다는 것은 코드가 아니라
트레이스를 읽을 줄 안다는 뜻이다.
"""

try:
    from agent import react
except ImportError:
    raise SystemExit(
        "이 예제는 에이전트 본체(agent/react.py)가 있어야 동작합니다."
    )

from examples._shared import h1

result = react.run("3박 4일 오사카 여행, 예산 80만원으로 일정 짜줘.", verbose=True)

h1("루프 요약")
print(f"  스텝 수: {len(result.steps)}, 종료 사유: {result.stopped_by}")
for i, s in enumerate(result.steps, 1):
    what = f"{s.tool}({s.args})" if s.tool else "최종 답변"
    print(f"  [{i}] {what}  (이 스텝의 컨텍스트: {s.prompt_tokens} 토큰)")

h1("최종 답 (앞부분)")
print("  " + (result.answer or "(없음)")[:300].replace("\n", "\n  "))
