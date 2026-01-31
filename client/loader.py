
import os
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

# Global client reference
mcp_client = None

@tool
async def read_resource(uri: str) -> str:
    """Read a resource from the MCP server.
    Use this tool to read the content of a resource.
    """
    if not mcp_client:
        return "Error: Client not initialized."
    try:
        content = await mcp_client.read_resource(uri)
        return str(content)
    except Exception as e:
        return f"Error reading resource: {e}"

async def get_agent_app():
    global mcp_client
    
    # Calculate absolute path to math server
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    math_server_path = os.path.join(base_dir, "servers", "math", "server.py")

    client=MultiServerMCPClient({
        "math": {
            "command": "python",
            "args": [math_server_path],
            "transport": "stdio",
        },
        "weather": {
            "url": "http://127.0.0.1:8000/sse",
            "transport": "sse",
        },
        "web": {
            "url": "http://127.0.0.1:8001/sse",
            "transport": "sse",
        },
        "image_gen": {
            "url": "http://127.0.0.1:8003/sse",
            "transport": "sse",
        },
    })

    try:
        # Retry logic for connecting to servers
        max_retries = 5
        for attempt in range(max_retries):
            try:
                tools = await client.get_tools()
                resources = await client.get_resources()
                print("Successfully connected to all MCP servers.")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt+1}/{max_retries} failed to connect to servers: {e}")
                    print("Retrying in 2 seconds...")
                    await asyncio.sleep(2)
                else:
                    raise e
    except Exception as e:
        print(f"Warning: Failed to load tools from all servers: {e}")
        print("Retrying with math server only...")
        # Fallback logic omitted for brevity in API, but good to have
        client = MultiServerMCPClient({
            "math": {
                "command": "python",
                "args": [math_server_path],
                "transport": "stdio",
            },
        })
        tools = await client.get_tools()
        resources = []

    mcp_client = client
    
    all_tools = tools + [read_resource]
    
    resource_info = "\n".join([f"- {r.metadata['uri']}" if hasattr(r, 'metadata') else f"- {r.uri}" for r in resources])
    system_prompt = (
        "You are a helpful assistant that can use available tools to answer questions.\n"
        "You have access to the following resources (use read_resource to read them):\n"
        f"{resource_info}"
    )

    model = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))
    memory = MemorySaver()

    agent = create_react_agent(
        model,
        all_tools,
        checkpointer=memory,
        prompt=system_prompt,
    )
    
    return agent, client
