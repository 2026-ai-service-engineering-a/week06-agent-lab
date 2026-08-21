"""MCP 클라이언트 — 도구 목록이 표준 프로토콜로 배달된다.

  docker compose exec lab python examples/07_mcp/02_list_tools.py

키 없이 돈다. 서버를 미리 띄울 필요가 없다 — stdio 전송에서는 이 클라이언트가
01 서버를 자기 하위 프로세스로 직접 띄워 접속한다(서버 로그가 이 터미널에
섞여 나오는 이유). 도구 목록(이름·설명·입력 스키마)을 받아 출력하고, 도구
하나를 원격 호출해 본다.
4세션에서 손으로 쓰던 것과 같은 모양의 스키마가, 이번엔 코드가 아니라
프로토콜로 온다는 것이 요점이다.
"""

import asyncio
import json
import sys
import warnings

# mcp 1.29가 pydantic-settings 최신 검사와 어긋나며 내는 소음을 가린다 (동작 무관)
warnings.filterwarnings("ignore", message="Field 'lifespan' has an incomplete definition.*")

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from examples._shared import h1

SERVER = StdioServerParameters(
    command=sys.executable, args=["examples/07_mcp/01_mcp_server.py"]
)


async def main() -> None:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            h1("서버가 내어놓은 도구 목록 (프로토콜로 수신)")
            tools = (await session.list_tools()).tools
            for t in tools:
                print(f"  {t.name}: {t.description}")
                schema = json.dumps(t.inputSchema, ensure_ascii=False)
                print(f"    입력 스키마: {schema[:100]}…")

            h1("원격 도구 호출: get_exchange_rate(JPY)")
            result = await session.call_tool("get_exchange_rate", {"currency": "JPY"})
            print("  " + result.content[0].text)

            h1("정리")
            print("  우리 코드에는 도구 구현이 한 줄도 없다. 목록도 실행도 프로토콜 너머의 일이다.")


asyncio.run(main())
