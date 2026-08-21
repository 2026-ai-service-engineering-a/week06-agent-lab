"""프롬프트 절제 실험 — 시스템 프롬프트를 한 부분씩 빼면 루프가 어떻게 무너지는가.

  docker compose exec lab python examples/04_react/03_prompt_ablation.py

같은 질문을 ① 온전한 프롬프트 ② 도구 사용 지침을 뺀 것 ③ 빈 프롬프트로
돌려 비교한다. 시스템 프롬프트의 각 문단은 장식이 아니라 루프를 지탱하는
부품임을 확인한다.
"""

try:
    from agent import react
    from agent.react import SYSTEM_PROMPT
except ImportError:
    raise SystemExit("이 예제는 에이전트 본체(agent/react.py)가 있어야 동작합니다.")

from examples._shared import h1

question = "1박 2일 오사카, 예산 30만원. 일정 짜줘."

variants = {
    "① 온전한 프롬프트": SYSTEM_PROMPT,
    "② 도구 지침 문단 제거": SYSTEM_PROMPT.split("## 도구 사용")[0].strip(),
    "③ 빈 프롬프트": "당신은 도우미입니다.",
}

for name, system in variants.items():
    result = react.run(question, system=system, verbose=False)
    tools_used = [s.tool for s in result.steps if s.tool]
    h1(name)
    print(f"  스텝 {len(result.steps)}, 도구 사용 {len(tools_used)}회: {tools_used}")
    print(f"  답 미리보기: {(result.answer or '')[:120]}…")
