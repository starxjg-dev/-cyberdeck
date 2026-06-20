@echo off
REM ============================================================
REM  Cyberdeck Setup — One-click installer for Windows
REM  Installs the Cyberdeck skill into Hermes Agent
REM ============================================================
echo.
echo   ╔══════════════════════════════════════════╗
echo   ║     CYBERDECK v5.0 — Setup Wizard        ║
echo   ╚══════════════════════════════════════════╝
echo.

REM Check if Hermes is installed
where hermes >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Hermes Agent not found.
    echo        Install from: https://github.com/NousResearch/hermes-agent
    echo        Then run this script again.
    pause
    exit /b 1
)

echo [OK]   Hermes Agent found

REM Determine skill directory
if exist "%USERPROFILE%\.hermes\skills" (
    set SKILL_DIR=%USERPROFILE%\.hermes\skills\software-development\cyberdeck
) else if exist "E:\.hermes\skills" (
    set SKILL_DIR=E:\.hermes\skills\software-development\cyberdeck
) else (
    echo [FAIL] Can't find Hermes skills directory.
    echo        Expected: %%USERPROFILE%%\.hermes\skills or E:\.hermes\skills
    pause
    exit /b 1
)

REM Create directory and copy skill
mkdir "%SKILL_DIR%" 2>nul
copy /Y "%~dp0SKILL.md" "%SKILL_DIR%\SKILL.md" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Could not copy SKILL.md to %SKILL_DIR%
    pause
    exit /b 1
)

echo [OK]   SKILL.md installed to %SKILL_DIR%

REM Check if .env has API keys
if exist "%USERPROFILE%\.hermes\.env" (
    findstr /C:"API_KEY" "%USERPROFILE%\.hermes\.env" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK]   API keys found in .env
    ) else (
        echo [WARN] No API keys in .env — add them to use cloud models
    )
) else if exist "E:\.hermes\.env" (
    findstr /C:"API_KEY" "E:\.hermes\.env" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK]   API keys found in .env
    ) else (
        echo [WARN] No API keys in .env — add them to use cloud models
    )
) else (
    echo [WARN] No .env file found. Copy .env.example, add your keys.
)

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║   INSTALL COMPLETE                       ║
echo   ╚══════════════════════════════════════════╝
echo.
echo   Next steps:
echo     1. hermes -s cyberdeck        (load with skill)
echo     2. Just start chatting!       (Wizard auto-runs)
echo.
echo   Try the demo:  python mini-agent.py "Hello!"
echo.
pause
