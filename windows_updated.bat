@echo off
REM ============================
REM Run Team 13 Project Container on Windows with Docker
REM ============================

REM ---- CONFIG ----
set IMAGE_NAME=com3524
set DISPLAY=host.docker.internal:0.0
set CONTAINER_NAME=forest-fire-team13

REM ---- REMOVE OLD CONTAINER ----
echo Removing old container (if any)...
docker rm -f %CONTAINER_NAME% >nul 2>&1

REM ---- BUILD IMAGE ----
echo Building Docker image...
docker build -t %IMAGE_NAME% .

REM ---- RUN CONTAINER ----
echo Running app on http://127.0.0.1:5000 ...
docker run -it --rm ^
    --name %CONTAINER_NAME% ^
    -e DISPLAY=%DISPLAY% ^
    -e PYTHONPATH=/src ^
    -p 5000:5000 ^
    -v "%cd%\CAPyle_releaseV2":/src/CAPyle_releaseV2 ^
    -v "%cd%\run_tool.py":/src/run_tool.py ^
    %IMAGE_NAME% ^
    python3 -m run_tool

pause
