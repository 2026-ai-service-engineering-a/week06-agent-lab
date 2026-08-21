"""스텝 한도 — 1, 3, 10으로 바꿔가며 에이전트의 행동 변화를 관찰한다.

  docker compose exec lab python examples/04_react/02_max_steps.py

한도 1이면 도구 한 번 쓰고 강제 종료, 10이면 여유 있게 돌고 스스로 멈춘다.
스텝 한도는 품질 설정이 아니라 무한 루프에 대한 보험이다 — 05_loops와
하네스에서 이 감각을 계속 잇는다.
"""

try:
    from agent import react
except ImportError:
    raise SystemExit("이 예제는 에이전트 본체(agent/react.py)가 있어야 동작합니다.")

from examples._shared import h1

question = "2박 3일 교토, 예산 50만원으로 일정과 예산 내역을 짜줘."

for limit in (1, 3, 10):
    result = react.run(question, max_steps=limit, verbose=False)
    h1(f"max_steps = {limit}")
    print(f"  사용한 스텝: {len(result.steps)}, 종료: {result.stopped_by}")
    tools_used = [s.tool for s in result.steps if s.tool]
    print(f"  쓴 도구: {tools_used or '(없음)'}")
    print(f"  답 길이: {len(result.answer or '')}자")
