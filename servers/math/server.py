from mcp.server.fastmcp import FastMCP


mcp = FastMCP(name="MathServer") # MathServer is the name of the server

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

# the transport = "stdio" argument tells server to: 

# Use standard input and output(stdin/stdout) to recieve and respond to tool fuction calls
# this is done, so that we can interact with the server using the command prompt

if __name__ == "__main__":
    mcp.run(transport="stdio")
