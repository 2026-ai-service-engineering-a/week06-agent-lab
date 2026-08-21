"""budget guard — 실행 중 누적 비용이 상한을 넘으면 중단한다.

  docker compose exec lab python examples/06_harness/09_budget_guard.py

키 없이 동작한다 (호출 비용을 시뮬레이션). 스텝 한도가 "루프의 보험"이라면
budget guard는 "지갑의 보험"이다. 경고 임계(계속 돌되 알림)와 중단 임계
(그 자리에서 멈춤)의 2단 판정을 관찰한다.
"""

from examples._shared import h1

class BudgetExceeded(Exception):
    pass


class BudgetGuard:
    """누적 비용 장부 + 2단 임계."""

    def __init__(self, warn_usd: float, stop_usd: float):
        self.warn_usd, self.stop_usd = warn_usd, stop_usd
        self.spent = 0.0
        self.warned = False

    def add(self, cost_usd: float) -> None:
        self.spent += cost_usd
        if self.spent >= self.stop_usd:
            raise BudgetExceeded(f"누적 ${self.spent:.4f} ≥ 중단 임계 ${self.stop_usd}")
        if self.spent >= self.warn_usd and not self.warned:
            self.warned = True
            print(f"    ⚠ 경고: 누적 ${self.spent:.4f}가 경고 임계 ${self.warn_usd}를 넘었다")


guard = BudgetGuard(warn_usd=0.05, stop_usd=0.10)

# 에이전트 루프를 시뮬레이션: 히스토리가 부풀어 스텝 비용이 점점 커진다
step_costs = [0.008, 0.012, 0.018, 0.025, 0.034, 0.045]

h1("루프 진행 (경고 $0.05 / 중단 $0.10)")
try:
    for i, cost in enumerate(step_costs, 1):
        guard.add(cost)
        print(f"  step{i}: 이번 스텝 ${cost:.3f}, 누적 ${guard.spent:.4f} — 계속")
except BudgetExceeded as e:
    print(f"  ⛔ 중단: {e}")

h1("정리")
print("  경고는 사람이 개입할 기회, 중단은 최후의 방어선이다. 에이전트 본체는")
print("  실제 completion 비용을 이 장부에 흘려 넣는다 — 코드는 완전히 같다.")
