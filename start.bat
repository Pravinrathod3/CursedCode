@echo off
REM One-command startup script for CursedCode on Windows
echo === Starting CursedCode ===

REM 1. Start go-judge daemon on Windows if present
if exist "server\bin\go-judge.exe" (
    echo Starting go-judge sandbox on port 5050...
    start "go-judge" server\bin\go-judge.exe -http-addr 127.0.0.1:5050
)

REM 2. Start FastAPI server
echo Starting FastAPI server on port 8000...
cd server
start "CursedCode Backend" cmd /k ".venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000"
cd ..

REM 3. Start Vite frontend
echo Starting Vite client on port 5173...
cd client
start "CursedCode Client" cmd /k "npm run dev -- --host 0.0.0.0 --port 5173"
cd ..

echo === All services launched ===
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo go-judge: http://localhost:5050
pause
