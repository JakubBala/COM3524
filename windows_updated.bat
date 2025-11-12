@echo off
REM ============================
REM Compose and Run Team 13's Docker Container
REM ============================

REM ---- BUILD IMAGE ----
echo Building Docker image...
docker compose run --build com3524_project

pause
