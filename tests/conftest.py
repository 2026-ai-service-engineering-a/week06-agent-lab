"""테스트 공용 도구 — LLM을 부르지 않고 에이전트를 검증하기 위한 가짜들.

모든 테스트는 네트워크·API 키 없이 돈다. litellm.completion이 돌려주는
객체와 같은 속성 구조(choices[0].message…)를 가진 가짜 응답을 만들고,
정해진 순서로 그것을 돌려주는 ScriptedLLM으로 completion을 갈아끼운다.
"""

from types import SimpleNamespace


def fake_tool_call(name: str, arguments: str, call_id: str = "call_1"):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=arguments),
        type="function",
    )


def fake_response(content=None, tool_calls=None, prompt_tokens=100, completion_tokens=50):
    """litellm ModelResponse와 같은 모양의 최소 객체."""
    message = SimpleNamespace(
        content=content,
        tool_calls=tool_calls,
        role="assistant",
        model_dump=lambda: {
            "role": "assistant",
            "content": content,
            "tool_calls": [
                {
                    "id": c.id,
                    "type": "function",
                    "function": {"name": c.function.name, "arguments": c.function.arguments},
                }
                for c in (tool_calls or [])
            ]
            or None,
        },
    )
    return SimpleNamespace(
        choices=[SimpleNamespace(message=message)],
        usage=SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
        model="fake-model",
    )


class ScriptedLLM:
    """completion 대역: 정해진 응답을 순서대로 내주고, 받은 요청을 기록한다."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []  # 각 호출의 kwargs 기록

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        if not self.responses:
            raise AssertionError("각본에 없는 추가 LLM 호출이 발생했다")
        return self.responses.pop(0)
