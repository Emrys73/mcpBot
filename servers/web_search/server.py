from mcp.server.fastmcp import FastMCP
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
import os

load_dotenv()

mcp = FastMCP(name="WebSearchServer")

# Initialize Tavily Tool
tavily_tool = TavilySearchResults(max_results=3)

@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for a given query using Tavily.
    Args:
        query: The search query string.
    Returns:
        A formatted string of search results.
    """
    try:
        results = tavily_tool.invoke({"query": query})
        # Format results nicely
        formatted_results = []
        for res in results:
            formatted_results.append(f"- {res['content']} ({res['url']})")
        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"Error performing search: {str(e)}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001, help="Port to run the server on")
    args = parser.parse_args()
    
    mcp.settings.port = args.port
    mcp.run(transport="sse")
