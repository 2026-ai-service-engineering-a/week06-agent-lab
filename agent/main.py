"""여행 플래너 에이전트 CLI — 루프·평가·하네스가 모두 물린 완성본.

  docker compose exec lab python -m agent.main "3박 4일 오사카, 예산 80만원"
  docker compose exec lab python -m agent.main --verbose "..."        # 트레이스
  docker compose exec lab python -m agent.main --max-cost 0.10 "..."  # 지갑의 보험
  docker compose exec lab python -m agent.main --no-reflexion "..."   # 평가 없이

루프에는 하네스가 물려 있다: 모든 도구 결과가 데이터 경계로 감싸이고,
인젝션 흔적은 기록·경고되며, 누적 비용은 BudgetGuard가 지키고, 실행 전체가
traces/*.jsonl에 남는다.
"""

import argparse

from agent import react, reflexion
from agent.harness import BudgetGuard, TraceLogger


def main() -> None:
    parser = argparse.ArgumentParser(description="여행 플래너 에이전트")
    parser.add_argument("question", help="여행 요청 (예: '3박 4일 오사카, 예산 80만원')")
    parser.add_argument("--max-steps", type=int, default=8, help="루프 스텝 한도 (기본 8)")
    parser.add_argument("--max-cost", type=float, default=0.20, help="비용 중단 임계 USD (기본 0.20)")
    parser.add_argument("--verbose", action="store_true", help="트레이스·평가 출력")
    parser.add_argument("--no-reflexion", action="store_true", help="평가·재시도 없이 1회만")
    args = parser.parse_args()

    guard = BudgetGuard(warn_usd=args.max_cost / 4, stop_usd=args.max_cost)
    logger = TraceLogger()

    if args.no_reflexion:
        result = react.run(
            args.question, max_steps=args.max_steps, verbose=args.verbose,
            guard=guard, logger=logger,
        )
        print(result.answer)
    else:
        result = reflexion.run_with_reflexion(args.question, verbose=args.verbose)
        print(result.answer)

    print(f"
(누적 비용 ${guard.spent:.4f} · 트레이스 {logger.path})")


if __name__ == "__main__":
    main()
