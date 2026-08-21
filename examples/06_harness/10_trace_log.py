"""구조화 트레이스 로그 — 모든 호출·도구 실행을 JSONL로 남긴다.

  docker compose exec lab python examples/06_harness/10_trace_log.py

키 없이 동작한다 (이벤트를 시뮬레이션). 사고가 난 뒤에 "무슨 일이 있었나"를
답할 수 있으려면, 사람이 읽는 print가 아니라 기계가 다시 읽을 수 있는
구조화 로그가 필요하다. 한 줄 = 한 이벤트인 JSONL이 표준적인 시작점이다.
"""

import json
from pathlib import Path

from examples._shared import h1

class TraceLogger:
    """한 실행(run)의 이벤트를 JSONL 파일에 append한다."""

    def __init__(self, run_id: str):
        Path("traces").mkdir(exist_ok=True)
        self.path = Path("traces") / f"{run_id}.jsonl"
        self.seq = 0

    def log(self, kind: str, **fields) -> None:
        self.seq += 1
        record = {"seq": self.seq, "kind": kind, **fields}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


logger = TraceLogger("demo-run")

# 에이전트 한 바퀴를 시뮬레이션해 이벤트를 흘려 넣는다
logger.log("llm_call", model="gemini/gemini-3.5-flash-lite", prompt_tokens=812, completion_tokens=64, cost_usd=0.0004)
logger.log("tool_call", tool="search_places", args={"city": "오사카"}, ok=True, elapsed_ms=3)
logger.log("guard", check="injection_scan", findings=[])
logger.log("llm_call", model="gemini/gemini-3.5-flash-lite", prompt_tokens=1240, completion_tokens=420, cost_usd=0.0014)
logger.log("final", answer_chars=980, total_cost_usd=0.0018)

h1(f"기록된 트레이스: {logger.path}")
for line in logger.path.read_text(encoding="utf-8").splitlines():
    print("  " + line)

h1("이 로그로 답할 수 있는 질문들")
print("  어느 스텝에서 비용이 튀었나 / 어떤 도구가 무슨 인자로 불렸나 /")
print("  인젝션 검사는 통과했나 — 트레이스 없는 에이전트는 블랙박스다.")
