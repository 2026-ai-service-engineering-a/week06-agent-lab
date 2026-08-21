"""여행 플래너 에이전트 CLI — v0.4: Reflexion 재시도 장착.

  docker compose exec lab python -m agent.main "3박 4일 오사카, 예산 80만원"
  docker compose exec lab python -m agent.main --verbose "..."       # 트레이스
  docker compose exec lab python -m agent.main --no-reflexion "..."  # 평가 없이

기본 동작: ReAct로 일정을 만들고, 평가자가 루브릭으로 채점해 미달이면
피드백과 함께 재시도한다 (agent/reflexion.py). 평가·재시도 없이 한 번만
돌리려면 --no-reflexion.
"""

import argparse

from agent import react, reflexion


def main() -> None:
    parser = argparse.ArgumentParser(description="여행 플래너 에이전트")
    parser.add_argument("question", help="여행 요청 (예: '3박 4일 오사카, 예산 80만원')")
    parser.add_argument("--max-steps", type=int, default=8, help="루프 스텝 한도 (기본 8)")
    parser.add_argument("--verbose", action="store_true", help="트레이스·평가 출력")
    parser.add_argument("--no-reflexion", action="store_true", help="평가·재시도 없이 1회만")
    args = parser.parse_args()

    if args.no_reflexion:
        result = react.run(args.question, max_steps=args.max_steps, verbose=args.verbose)
        print(result.answer)
    else:
        result = reflexion.run_with_reflexion(args.question, verbose=args.verbose)
        print(result.answer)


if __name__ == "__main__":
    main()
