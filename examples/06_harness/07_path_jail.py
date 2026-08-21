"""경로 감금 — 파일 도구를 작업 폴더 안에 가둔다 (경로 탈출 차단).

  docker compose exec lab python examples/06_harness/07_path_jail.py

키 없이 동작한다. 파일을 읽고 쓰는 도구를 에이전트에게 주는 순간,
"../../.env 읽어줘" 한 줄이 위협이 된다. 모든 경로를 작업 폴더 기준으로
정규화하고, 폴더 밖이면 실행 전에 거부한다.
"""

from pathlib import Path

from examples._shared import h1

JAIL = Path("workspace").resolve()  # 에이전트에게 허락된 유일한 영역
JAIL.mkdir(exist_ok=True)


def safe_path(requested: str) -> Path:
    """감금 검사: 정규화 결과가 JAIL 밖이면 거부한다."""
    resolved = (JAIL / requested).resolve()
    if not resolved.is_relative_to(JAIL):
        raise PermissionError(f"경로 탈출 차단: {requested!r} → {resolved}")
    return resolved


def write_file(path: str, content: str) -> str:
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"저장됨: {p.relative_to(JAIL)}"


def read_file(path: str) -> str:
    return safe_path(path).read_text(encoding="utf-8")


h1("정상 사용")
print("  " + write_file("plans/osaka.md", "# 오사카 일정\n1일차: 도톤보리"))
print("  읽기 → " + read_file("plans/osaka.md").splitlines()[0])

h1("탈출 시도들")
for attack in ["../.env", "../../etc/passwd", "plans/../../secret.txt"]:
    try:
        read_file(attack)
        print(f"  !? {attack} 이 읽혔다 (있어서는 안 될 일)")
    except (PermissionError, FileNotFoundError) as e:
        print(f"  차단: {attack!r} → {type(e).__name__}")

h1("정리")
print("  resolve() 후 is_relative_to() — 두 줄의 결정적 코드가 프롬프트 백 줄보다 세다.")
