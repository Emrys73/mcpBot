import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient  

from langchain.agents import create_agent

from langchain_groq import ChatGroq

from dotenv import load_dotenv



load_dotenv()

async def main():
    client=MultiServerMCPClient({
        #
        "math": {
            "command": "python",
            "args": ["mathserver.py"], ## ensure correct absolute path to the mathserver.py file
            "transport": "stdio", ## Use standard input and output(stdin/stdout) to recieve and respond to tool fuction calls
        },
        "weather": {
            "url": "http://127.0.0.1:8000/sse",
            "transport": "streamable-http", ## Use streamable HTTP to recieve and respond to tool fuction calls
        },
    })


    import os 
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

    try:
        tools = await client.get_tools()
        print(f"Loaded {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"Warning: Failed to load tools from all servers: {e}")
        print("Retrying with math server only...")
        # Fallback to math server only
        client = MultiServerMCPClient({
            "math": {
                "command": "python",
                "args": ["mathserver.py"],
                "transport": "stdio",
            },
        })
        tools = await client.get_tools()
        print(f"Loaded {len(tools)} tools (math only):")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
    
    model = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))
    agent = create_agent(model, tools, system_prompt="You are a helpful assistant that can use available tools to answer questions.")

    result = await agent.ainvoke({"messages": [{"role": "user", "content": "What is weather in Tokyo?"}]})
    print(result.get("output", result))

asyncio.run(main())