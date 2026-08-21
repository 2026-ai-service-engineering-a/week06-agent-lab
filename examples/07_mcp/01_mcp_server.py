"""여행 도구를 MCP 서버로 내어놓는다 — 세션 8의 시연 서버.

  docker compose exec lab python examples/07_mcp/01_mcp_server.py          # stdio
  docker compose exec lab python examples/07_mcp/01_mcp_server.py --http   # 상주 서버

전송이 두 가지다. 오해하기 쉬운 지점이니 구분해 둔다.

  · stdio(기본): 클라이언트가 이 파일을 자기 하위 프로세스로 띄워 표준입출력으로
    대화한다. 그래서 02·03을 돌리기 전에 서버를 미리 띄울 필요가 없고, 미리
    띄워 둔 서버에는 아무도 접속하지 않는다(그 프로세스의 stdio는 터미널에
    물려 있다). 단독 실행하면 그저 침묵한다 — 종료는 Ctrl+C
  · --http: 진짜 상주 서버. 포트 8000에서 접속을 기다리고, 여러 클라이언트가
    붙을 수 있으며, 요청 로그가 이 터미널에 찍힌다. 04 예제가 여기 접속한다.
    Day 3의 "에이전트를 MCP로 내어주기"가 이 형태다

도구 구현은 4세션에서 손으로 등록하던 것과 같은 평범한 함수다. 달라진 것은
노출 방식뿐 — 데코레이터 하나로 함수 시그니처·docstring이 MCP 프로토콜의
도구 명세가 된다.

이 파일은 일부러 self-contained다: stdio 클라이언트는 서버 하위 프로세스에
최소 환경만 넘기므로(PYTHONPATH 없음), 서버는 어디서 띄워도 도는 독립
실행체로 쓰는 것이 실전 형태다.
"""

import sys
import warnings

# mcp 1.29가 pydantic-settings 최신 검사와 어긋나며 내는 소음을 가린다 (동작 무관)
warnings.filterwarnings("ignore", message="Field 'lifespan' has an incomplete definition.*")

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("travel-tools")

RATES = {"JPY": 9.1, "USD": 1385.0, "EUR": 1490.0}

PLACES = {
    "오사카": [
        {"name": "오사카성", "category": "관광", "fee_yen": 600},
        {"name": "도톤보리", "category": "관광", "fee_yen": 0},
        {"name": "구로몬 시장", "category": "식당", "fee_yen": 0},
    ],
    "교토": [
        {"name": "후시미 이나리", "category": "관광", "fee_yen": 0},
        {"name": "기요미즈데라", "category": "관광", "fee_yen": 400},
    ],
}


@mcp.tool()
def get_exchange_rate(currency: str) -> dict:
    """통화 코드(JPY, USD, EUR)의 원화 환율을 돌려준다."""
    if currency not in RATES:
        return {"error": f"지원하지 않는 통화: {currency}. 지원 목록: {list(RATES)}"}
    return {"currency": currency, "krw": RATES[currency]}


@mcp.tool()
def search_places(city: str) -> list[dict]:
    """도시의 관광지·식당을 검색한다. 지원 도시: 오사카, 교토."""
    return PLACES.get(city, [])


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")  # 상주 서버: http://127.0.0.1:8000/mcp
    else:
        mcp.run()  # stdio: 클라이언트가 이 프로세스를 직접 띄웠을 때의 전송
