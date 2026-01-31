import asyncio
import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()


def _get_user_input() -> str:
    """Blocking input for use in executor."""
    return input("You: ").strip()


from langchain_core.tools import tool

# Global client reference to be set in main
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

async def main():
    global mcp_client

    # Calculate absolute path to math server
    # __file__ is client/main.py, so dirname(dirname(...)) gives root MCP_server/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    math_server_path = os.path.join(base_dir, "servers", "math", "server.py")

    client=MultiServerMCPClient({
        #
        "math": {
            "command": "python",
            "args": [math_server_path], ## ensure correct absolute path to the mathserver.py file
            "transport": "stdio", ## Use standard input and output(stdin/stdout) to recieve and respond to tool fuction calls
        },
        "weather": {
            "url": "http://127.0.0.1:8000/sse",
            "transport": "sse", ## Use SSE to recieve and respond to tool fuction calls
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


    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

    try:
        tools = await client.get_tools()
        print(f"Loaded {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        resources = await client.get_resources()
        print(f"Loaded {len(resources)} resources:")
        for resource in resources:
            # Handle potentially different resource object structures
            # Based on debug: object has metadata={'uri': ...}
            r_uri = 'Unknown'
            if hasattr(resource, 'metadata') and 'uri' in resource.metadata:
                r_uri = resource.metadata['uri']
            elif hasattr(resource, 'uri'):
                r_uri = resource.uri
            
            print(f"  - Resource URI: {r_uri}")
    except Exception as e:
        print(f"Warning: Failed to load tools from all servers: {e}")
        print("Retrying with math server only...")
        client = MultiServerMCPClient({
            "math": {
                "command": "python",
                "args": [math_server_path],
                "transport": "stdio",
            },
        })
        tools = await client.get_tools()
        print(f"Loaded {len(tools)} tools (math only):")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

    # Set the global client for the tool to use
    mcp_client = client

    model = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))
    memory = MemorySaver()
    
    all_tools = tools + [read_resource]

    # Create a system prompt that includes the list of available resources
    resource_info = "\n".join([f"- {r.metadata['uri']}" if hasattr(r, 'metadata') else f"- {r.uri}" for r in resources])
    system_prompt = (
        "You are a helpful assistant that can use available tools to answer questions.\n"
        "You have access to the following resources (use read_resource to read them):\n"
        f"{resource_info}"
    )

    agent = create_react_agent(
        model,
        all_tools,
        checkpointer=memory,
        prompt=system_prompt,
    )

    thread_id = "chat-1"
    config = {"configurable": {"thread_id": thread_id}}
    print("\nChat with the agent (tools + memory). Type 'quit', 'exit', or 'q' to stop.\n")

    loop = asyncio.get_event_loop()
    while True:
        user_input = await loop.run_in_executor(None, _get_user_input)
        if not user_input or user_input.lower() in ("quit", "exit", "q"):
            print("Bye.")
            break
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
        )
        messages = result.get("messages", [])
        last_ai = next((m for m in reversed(messages) if isinstance(m, AIMessage)), None)
        if last_ai and last_ai.content:
            print("Assistant:", last_ai.content)
        elif last_ai:
            print("Assistant:", "(no text reply)")
        else:
            print("Assistant:", result)


asyncio.run(main())