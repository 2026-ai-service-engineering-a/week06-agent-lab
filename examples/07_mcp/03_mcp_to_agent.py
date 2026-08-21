"""MCP 도구를 루프에 꽂는다 — 코드 수정 없이 도구 목록이 늘어난다.

  docker compose exec lab python examples/07_mcp/03_mcp_to_agent.py

MCP로 받은 도구 목록을 litellm 도구 스키마로 변환해 미니 루프에 쥐여준다.
루프는 도구가 어디서 왔는지 모른다 — 손으로 등록했든 프로토콜로 받았든
같은 모양이기 때문이다. 실행만 원격(call_tool)으로 바뀐다.
"""

import asyncio
import json
import sys

from litellm import completion
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from examples._shared import h1, pick_model

SERVER = StdioServerParameters(
    command=sys.executable, args=["examples/07_mcp/01_mcp_server.py"]
)


def to_litellm_schema(tool) -> dict:
    """MCP 도구 명세 → litellm 도구 명세. 필드가 그대로 1:1로 옮겨진다."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


async def main() -> None:
    model = pick_model()
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = (await session.list_tools()).tools
            tools = [to_litellm_schema(t) for t in mcp_tools]
            h1(f"프로토콜로 받은 도구 {len(tools)}개를 루프에 장착")
            for t in tools:
                print(f"  {t['function']['name']}")

            messages = [
                {"role": "user", "content": "100달러가 원화로 얼마야? 그리고 교토 관광지도 하나만 추천해줘."}
            ]
            for step in range(1, 6):
                resp = completion(model=model, messages=messages, tools=tools)
                msg = resp.choices[0].message
                if not msg.tool_calls:
                    h1("최종 답")
                    print("  " + (msg.content or "").strip()[:250].replace("\n", "\n  "))
                    break
                messages.append(msg.model_dump())
                for call in msg.tool_calls:
                    result = await session.call_tool(
                        call.function.name, json.loads(call.function.arguments)
                    )
                    text = result.content[0].text if result.content else "{}"
                    print(f"  [step {step}] {call.function.name}({call.function.arguments}) → {text[:70]}…")
                    messages.append(
                        {"role": "tool", "tool_call_id": call.id, "content": text}
                    )

            h1("정리")
            print("  루프 코드는 4세션의 왕복 그대로다. 도구의 출처만 프로토콜로 바뀌었다.")


asyncio.run(main())
