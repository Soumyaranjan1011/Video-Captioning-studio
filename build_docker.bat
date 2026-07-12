@echo off
REM Installs Docker Desktop if missing, then builds the app image(s).
REM After this finishes, run: docker compose up -d
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if not exist "backend\.env" (
  echo Missing backend\.env - copy backend\.env.example to backend\.env and set your GEMINI_API_KEY first.
  exit /b 1
)

where docker >nul 2>nul
if errorlevel 1 (
  echo Docker not found - installing Docker Desktop...
  where winget >nul 2>nul
  if errorlevel 1 (
    echo winget is not available on this system.
    echo Install Docker Desktop manually: https://www.docker.com/products/docker-desktop/
    exit /b 1
  )
  winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
  echo.
  echo Docker Desktop installed. Open it once from the Start menu so it finishes
  echo first-time setup ^(whale icon appears in the system tray^), then re-run this script.
  exit /b 1
)

docker compose version >nul 2>nul
if errorlevel 1 (
  echo docker compose not found - make sure Docker Desktop is fully started, then try again.
  exit /b 1
)

echo Building images...
docker compose build
if errorlevel 1 (
  echo.
  echo Build failed. Common causes: Docker Desktop isn't fully started yet
  echo ^(wait for the whale icon in the system tray^), or your Windows user
  echo isn't in the "docker-users" group yet ^(log out/in after installing
  echo Docker Desktop for the first time^).
  exit /b 1
)

echo.
echo Build complete. Start the app with:
echo   docker compose up -d
echo Then open http://localhost:8000
