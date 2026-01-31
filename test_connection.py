
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def test_connection():
    try:
        print("Attempting to connect to Weather Server at http://127.0.0.1:8000/sse ...")
        client = MultiServerMCPClient({
            "weather": {
                "url": "http://127.0.0.1:8000/sse",
                "transport": "sse",
            },
        })
        print("Client initialized. Fetching tools...")
        tools = await client.get_tools()
        print("\nSUCCESS! Tools loaded:")
        for tool in tools:
            print(f" - {tool.name}: {tool.description}")
            
    except Exception as e:
        print(f"\nFAILURE: Could not connect to server.")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
