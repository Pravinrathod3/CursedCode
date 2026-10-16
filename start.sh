#!/bin/bash
# One-command startup script for Debug Dojo (DI-01)
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=== Starting Debug Dojo (DI-01) ==="

# 1. Start go-judge sandbox daemon if binary is present
if [ -f "./server/bin/go-judge" ]; then
    echo "Starting go-judge sandbox on port 5050..."
    ./server/bin/go-judge -http-addr 127.0.0.1:5050 > /tmp/go-judge.log 2>&1 &
    GO_JUDGE_PID=$!
    echo "go-judge started (PID: $GO_JUDGE_PID)"
fi

# 2. Start FastAPI Backend
echo "Starting FastAPI server on port 8000..."
cd "$DIR/server"
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# 3. Start Frontend
echo "Starting Vite client on port 5173..."
cd "$DIR/client"
npm run dev -- --host 0.0.0.0 --port 5173 &
CLIENT_PID=$!
echo "Client started (PID: $CLIENT_PID)"

echo "=== All services running ==="
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:8000"
echo "go-judge: http://localhost:5050"

# Graceful shutdown handler
trap "kill $BACKEND_PID $CLIENT_PID $GO_JUDGE_PID 2>/dev/null || true; exit" SIGINT SIGTERM EXIT
wait
