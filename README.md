# MCP Server & Client

This project implements a Model Context Protocol (MCP) client that connects to multiple tool servers (Math and Weather) to perform tasks using an AI agent.

## Prerequisites

1.  **Install `uv`**: Ensure you have [uv](https://github.com/astral-sh/uv) installed.
2.  **Groq API Key**: You need a Groq API Key for the LLM.
    *   Create a `.env` file in the root directory.
    *   Add your key: `GROQ_API_KEY=gsk_...`

## How to Run

You need to run the Weather Server and the Client in separate terminal windows.

### 1. Start the Weather Server
The client expects the weather server to run on port 8000.

```bash
uv run weather.py --port 8000
```
### 2. Start the webSearch Server
The client expects the weather server to run on port 8001.

```bash
uv run weather.py --port 8001
```

### After changing the port of the servers, remember to change the port number in the client.py to listen.


### 3. Start the Client
In a separate terminal window, run the client. It will automatically start the Math server internally.

```bash
uv run client.py
```

## Project Structure

*   `client.py`: Main entry point. Connects to servers and runs the AI agent.
*   `mathserver.py`: A local MCP server for math operations (runs via stdio).
*   `weather.py`: A local MCP server for weather data (runs via HTTP SSE).
