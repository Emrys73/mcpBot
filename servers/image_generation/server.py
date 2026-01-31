from mcp.server.fastmcp import FastMCP
import urllib.parse
import random

mcp = FastMCP(name="ImageGenerationServer")

@mcp.tool()
async def generate_image(prompt: str) -> str:
    """Generate an image based on a text prompt using Pollinations.ai.
    Returns a markdown image link to the generated image.
    mandatory: always use this tool when the user asks to generate, create, or show an image or picture.
    """
    # 1. Clean and encode the prompt
    clean_prompt = prompt.strip()
    encoded_prompt = urllib.parse.quote(clean_prompt)
    
    # 2. Generate a random seed (prevents caching the same image)
    seed = random.randint(1, 100000)

    # 3. CONSTRUCT THE URL
    # - Domain: Must be 'image.pollinations.ai'
    # - Path: Must be '/prompt/'
    # - Param: 'model=flux' is MANDATORY
    # - Param: 'nologo=true' hides the watermark
    image_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?model=flux"
        f"&width=1024"
        f"&height=1024"
        f"&seed={seed}"
        f"&nologo=true"
    )
    
    # Return markdown so the frontend renders it immediately
    return f"![Generated Image]({image_url})"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8003, help="Port to run the server on")
    args = parser.parse_args()

    mcp.settings.port = args.port
    mcp.run(transport="sse")