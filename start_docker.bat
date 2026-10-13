@echo off
title TRANSEARCH Docker Launcher (FastAPI + MongoDB + Mongo Express)
echo =========================================================================
echo  TRANSEARCH International - Docker Container Stack Launcher
echo =========================================================================
echo.
echo Starting MongoDB, Python FastAPI Backend, and Mongo Express UI...
echo.

docker compose up --build -d

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =========================================================================
    echo  SUCCESS! All Docker services are running:
    echo =========================================================================
    echo  - Python FastAPI Backend : http://localhost:8000
    echo  - Swagger API Docs       : http://localhost:8000/docs
    echo  - MongoDB Database       : localhost:27017
    echo  - Mongo Express Web UI   : http://localhost:8081
    echo =========================================================================
    echo.
    echo To view live logs, run: docker compose logs -f
    echo To stop all containers, run: docker compose down
) else (
    echo.
    echo [ERROR] Docker command failed. Please ensure Docker Desktop is running.
)

pause
