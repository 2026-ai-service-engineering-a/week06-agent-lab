"""상주 MCP 서버에 접속한다 — 서버 먼저, 클라이언트는 나중에.

  # 터미널 1: 서버를 상주로 띄운다 (로그가 여기 찍힌다)
  docker compose exec lab python examples/07_mcp/01_mcp_server.py --http

  # 터미널 2: 접속해서 도구를 쓴다 (키 불필요)
  docker compose exec lab python examples/07_mcp/04_http_client.py

02와 똑같은 일을 하지만 전송이 다르다. stdio(02)는 클라이언트가 서버를 하위
프로세스로 소유하는 1:1 구조였고, HTTP는 먼저 떠 있는 서버에 여러
클라이언트가 붙는 구조다. Day 3에서 에이전트를 세상에 내어줄 때의 형태이며,
이번엔 서버 터미널에 요청 로그가 찍히는 것을 확인할 수 있다.
"""

import asyncio
import json
import warnings

# mcp 1.29가 pydantic-settings 최신 검사와 어긋나며 내는 소음을 가린다 (동작 무관)
warnings.filterwarnings("ignore", message="Field 'lifespan' has an incomplete definition.*")

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from examples._shared import h1

URL = "http://127.0.0.1:8000/mcp"


async def main() -> None:
    try:
        async with streamablehttp_client(URL) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()

                h1(f"상주 서버 접속: {URL}")
                tools = (await session.list_tools()).tools
                for t in tools:
                    print(f"  {t.name}: {t.description}")

                h1("원격 도구 호출: search_places(교토)")
                result = await session.call_tool("search_places", {"city": "교토"})
                for block in result.content:
                    print("  " + block.text)

                h1("정리")
                print("  같은 도구, 같은 프로토콜, 다른 전송. 서버 터미널의 요청 로그를 확인하라.")
    except Exception as e:
        raise SystemExit(
            f"접속 실패: {type(e).__name__}\n"
            "먼저 다른 터미널에서 서버를 상주로 띄우세요:\n"
            "  docker compose exec lab python examples/07_mcp/01_mcp_server.py --http"
        )


asyncio.run(main())
