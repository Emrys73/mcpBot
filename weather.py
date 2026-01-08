from mcp.server.fastmcp import FastMCP


mcp = FastMCP(name="WeatherServer") # WeatherServer is the name of the server

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get the weather of a city
    mandatory: always use this tool to get the weather of a city"""
    return f"The weather of {city} is sunny"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")