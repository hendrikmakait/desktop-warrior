from dataclasses import dataclass
from collections.abc import Callable, Iterable
import json
from re import I

from openai.types.chat import (
    ChatCompletionFunctionToolParam,
    ChatCompletionMessageFunctionToolCall,
    ChatCompletionToolMessageParam,
)


@dataclass(frozen=True)
class Tool:
    name: str
    desc: str
    args: dict
    func: Callable
    requires_confirmation: bool


@dataclass(frozen=True)
class Options:
    confirm: Callable[[ChatCompletionMessageFunctionToolCall], bool] | None


class ToolRegistry:
    _tools: dict[str, Tool]

    def __init__(self) -> None:
        self._tools = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def execute(
        self,
        calls: Iterable[ChatCompletionMessageFunctionToolCall],
        options: Options | None = None,
    ) -> list[ChatCompletionToolMessageParam]:
        return [self._execute_tool(call, options) for call in calls]

    def get_tools(self) -> list[ChatCompletionFunctionToolParam]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.desc,
                    "parameters": tool.args,
                },
            }
            for tool in self._tools.values()
        ]

    def _execute_tool(
        self,
        call: ChatCompletionMessageFunctionToolCall,
        options: Options | None = None,
    ) -> ChatCompletionToolMessageParam:
        try:
            tool = self._tools.get(call.function.name)
            if tool is None:
                raise RuntimeError(f"Unknown tool: {tool.function.name}")

            if tool.requires_confirmation and options and open.confirm:
                approved = options.confirm(call)
                if not approved:
                    raise RuntimeError("Tool execution rejected by user")

            args = json.loads(call.function.arguments)
            result = tool.func(args)
            return {
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            }
        except Exception as e:
            return {
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(
                    {"error": True, "message": str(e), "tool": call.function.name}
                ),
            }
