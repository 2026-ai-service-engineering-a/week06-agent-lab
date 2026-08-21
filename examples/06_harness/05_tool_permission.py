"""도구 권한 분리 — 위험한 도구에는 사람의 확인을 끼운다.

  docker compose exec lab python examples/06_harness/05_tool_permission.py

조회 도구(환율·검색)는 자유롭게, 돈이 나가거나 되돌릴 수 없는 도구(결제·
취소)는 확인 게이트 뒤에 둔다. 게이트는 프롬프트가 아니라 코드다 —
모델이 아무리 강하게 요청해도 코드가 승인 없이는 실행하지 않는다.
"""

import json

from examples._shared import h1

# 도구 레지스트리에 위험 등급을 박는다
REGISTRY = {
    "get_exchange_rate": {"risk": "safe"},
    "search_places": {"risk": "safe"},
    "pay_deposit": {"risk": "dangerous"},      # 돈이 나간다
    "cancel_booking": {"risk": "dangerous"},   # 되돌릴 수 없다
}


def execute(name: str, args: dict, approved: bool = False) -> str:
    """모든 도구 실행이 지나는 단 하나의 관문."""
    risk = REGISTRY[name]["risk"]
    if risk == "dangerous" and not approved:
        return json.dumps({"blocked": f"{name}은 승인 필요. 사용자에게 확인을 받아라."}, ensure_ascii=False)
    return json.dumps({"ok": f"{name}({args}) 실행됨"}, ensure_ascii=False)


h1("모델이 요청했다고 가정한 실행들")
calls = [
    ("search_places", {"city": "오사카"}, False),
    ("pay_deposit", {"amount": 120000}, False),   # 승인 없이 결제 시도
    ("pay_deposit", {"amount": 120000}, True),    # 사용자 승인 후
]
for name, args, approved in calls:
    result = execute(name, args, approved)
    mark = "승인 후 " if approved else ""
    print(f"  {mark}{name} → {result}")

h1("정리")
print("  '결제 전에 꼭 물어봐'라는 프롬프트는 부탁이고, 게이트는 물리 법칙이다.")
print("  Day 2 booking-agent의 interrupt가 이 게이트의 제품판이다.")
