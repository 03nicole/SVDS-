# Starts the whole VRRS system: backend, frontend, and the phone camera
# node, each in its own window. Run this once instead of opening three
# separate terminals.
#
# Usage:  powershell -ExecutionPolicy Bypass -File .\run-all.ps1

$root = $PSScriptRoot

Write-Host "Starting backend (FastAPI) on http://127.0.0.1:8000 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$root\vrrs-backend'; .\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
) -WindowStyle Normal

Write-Host "Starting frontend (Vite) on http://localhost:5173 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$root\vrrs-frontend'; npm run dev"
) -WindowStyle Normal

Write-Host "Starting camera node (phone stream -> YOLO -> OCR -> backend, GPU) ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$root\vrrs-node'; C:\Users\user\anaconda3\envs\yolov8-env\python.exe plate_node.py"
) -WindowStyle Normal

Write-Host ""
Write-Host "All three started in separate windows. Close those windows (or Ctrl+C in each) to stop."
Write-Host "Before the camera node connects, make sure vrrs-node\.env has the correct PHONE_STREAM_URL for your phone's IP Webcam address."
