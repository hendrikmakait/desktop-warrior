from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

def agent(client: OpenAI, model: str, system: str) -> None:
    messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": system}]

    while True:
        prompt = input("User: ")
        messages.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(model=model, messages=messages)

        answer = None
        if completion.choices:
            answer = completion.choices[0].message.content
        messages.append({"role": "assistant", "content": answer})
        print(f"Assistant: {answer or ''}")
