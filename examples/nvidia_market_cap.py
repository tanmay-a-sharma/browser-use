from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

async def main():
    # Initialize the agent with a task and language model
    agent = Agent(
        task="Find quarterly market cap of NVIDIA",
        llm=ChatOpenAI(model="gpt-4o"),  # You can also use gpt-3.5-turbo
        use_vision=True  # Enable vision features
    )
    
    # Run the agent with a maximum of 10 steps
    result = await agent.run(max_steps=10)
    print(result)

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())
