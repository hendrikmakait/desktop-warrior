from openai import OpenAI
from .agent import agent
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    agent(client=OpenAI(), model="gpt-5", system="You are a helpful assistant")
