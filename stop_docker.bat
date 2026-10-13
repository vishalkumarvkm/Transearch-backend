@echo off
title Stop TRANSEARCH Docker Containers
echo Stopping all TRANSEARCH Docker containers...
docker compose down
echo.
echo All containers stopped successfully.
pause
