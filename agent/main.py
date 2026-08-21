"""여행 플래너 에이전트 CLI — v0.3: ReAct 루프 완성.

  docker compose exec lab python -m agent.main "3박 4일 오사카, 예산 80만원"
  docker compose exec lab python -m agent.main --verbose "..."   # 트레이스 보기

에이전트가 검색 → 이동시간 → 예산 도구를 필요한 만큼 오가며 일정을 만든다.
루프 본체는 agent/react.py — 종료 조건(최종 답 또는 스텝 한도)까지
reasoning → action → observation을 반복한다.
"""

import argparse

from agent import react


def main() -> None:
    parser = argparse.ArgumentParser(description="여행 플래너 에이전트")
    parser.add_argument("question", help="여행 요청 (예: '3박 4일 오사카, 예산 80만원')")
    parser.add_argument("--max-steps", type=int, default=8, help="루프 스텝 한도 (기본 8)")
    parser.add_argument("--verbose", action="store_true", help="ReAct 트레이스 출력")
    args = parser.parse_args()

    result = react.run(args.question, max_steps=args.max_steps, verbose=args.verbose)
    print(result.answer)


if __name__ == "__main__":
    main()
