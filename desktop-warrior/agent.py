import json
import os
from typing import Final
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionFunctionToolParam,
    ChatCompletionMessageFunctionToolCall,
    ChatCompletionMessageParam,
    ChatCompletionToolMessageParam,
)
from .tool_registry import Options, Tool, ToolRegistry

REGISTRY = ToolRegistry()

REGISTRY.register(
    Tool(
        "ls",
        "list directory contents",
        {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the directory, e.g., User/hendrikmakait/Desktop",
                },
            },
            "required": ["path"],
        },
        lambda args: os.listdir(args["path"]),
        False,
    )
)


def confirm_tool_call(call: ChatCompletionMessageFunctionToolCall) -> bool:
    print(f"The assistant wants to call {json.dumps(call)}")
    return input("Allow this action? (y/n): ") == "y"


def agent(client: OpenAI, model: str, system: str) -> None:
    messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": system}]

    while True:
        prompt = input("User: ")
        messages.append({"role": "user", "content": prompt})

        agent_turn = True
        while agent_turn:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=REGISTRY.get_tools(),
            )
            response = completion.choices[0].message
            messages.append(response)

            if response.tool_calls:
                # When thinking out loud, print thoughts
                if response.content:
                    print(f"Assistant (thinking): {response.content}")
                tool_responses = REGISTRY.execute(
                    response.tool_calls, options=Options(confirm=confirm_tool_call)
                )
                messages.extend(tool_responses)
                agent_turn = True
            else:
                # Regular response - print and exit inner loop
                print(f"Assistant: {response.content or ''}")
                agent_turn = False
