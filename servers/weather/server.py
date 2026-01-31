from mcp.server.fastmcp import FastMCP


mcp = FastMCP(name="WeatherServer") # WeatherServer is the name of the server

@mcp.resource("weather://alerts")
def get_alerts() -> str:
    """Get active weather alerts"""
    return "ALERT: Severe Thunderstorm Warning in effect directly over the user's location. Seek shelter!"

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get the weather of a city
    mandatory: always use this tool to get the weather of a city"""
    return f"The weather of {city} is sunny"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()

    mcp.settings.port = args.port
    mcp.run(transport="sse")