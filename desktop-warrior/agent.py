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

TOOLS: Final[list[ChatCompletionFunctionToolParam]] = [
    {
        "type": "function",
        "function": {
            "name": "ls",
            "description": "list directory contents",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the directory, e.g., ~/Desktop",
                    },
                },
                "required": ["path"],
            },
        },
    },
]


def execute_tool(
    call: ChatCompletionMessageFunctionToolCall,
) -> ChatCompletionToolMessageParam:
    func = call.function.name
    args = json.loads(call.function.arguments)

    if func == "ls":
        output = os.listdir(args["path"])
    else:
        output = "Unknown tool"
    return {"role": "tool", "tool_call_id": call.id, "content": json.dumps(output)}


def agent(client: OpenAI, model: str, system: str) -> None:
    messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": system}]

    while True:
        prompt = input("User: ")
        messages.append({"role": "user", "content": prompt})

        agent_turn = True
        while agent_turn:
            completion = client.chat.completions.create(
                model=model, messages=messages, tools=TOOLS
            )
            response = completion.choices[0].message
            messages.append(response)

            if response.tool_calls:
                # When thinking out loud, print thoughts
                if response.content:
                    print(response.content)
                for tool_call in response.tool_calls:
                    messages.append(execute_tool(tool_call))
                agent_turn = True
            else:
                # Regular response - print and exit inner loop
                print(f"Assistant: {response.content or ''}")
                agent_turn = False
