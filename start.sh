#!/bin/bash


# Kill all background processes on exit
trap 'kill $(jobs -p)' EXIT

cleanup_ports() {
    local ports=(8000 8001 8002 8003 3000)
    for port in "${ports[@]}"; do
        # Find PID using lsof
        # -t: terse output (PID only)
        # -i: specific internet address
        if pid=$(lsof -t -i:$port); then
            echo "Killing process $pid on port $port..."
            kill -9 $pid 2>/dev/null || true
        fi
    done
}

cleanup_ports

echo " Starting MCP System..."

echo "1. Starting Weather Server (Port 8000)..."
uv run servers/weather/server.py --port 8000 &
PID_WEATHER=$!

echo "2. Starting Web Search Server (Port 8001)..."
uv run servers/web_search/server.py --port 8001 &
PID_WEB=$!

echo "2.5. Starting Image Gen Server (Port 8003)..."
uv run servers/image_generation/server.py --port 8003 &
PID_IMG=$!

# Wait a bit for tools to start
# Wait a bit for tools to start
sleep 10

echo "3. Starting Backend API (Port 8002)..."
uv run client/api.py &
PID_API=$!

echo "4. Starting Frontend (Port 3000)..."
cd frontend
npm run dev &
PID_FRONT=$!

# Wait for all processes
wait $PID_WEATHER $PID_WEB $PID_IMG $PID_API $PID_FRONT
