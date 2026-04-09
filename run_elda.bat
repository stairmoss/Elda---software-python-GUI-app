@echo off
echo ===================================================
echo      ELDA - AI Alzheimer's Assistant v1.0
echo ===================================================
echo [1/3] Checking Ollama...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Ollama is running.
) else (
    echo Starting Ollama...
    start /min ollama serve
    timeout /t 3
)

echo [2/3] Checking Model Qwen2.5-3b...
ollama list | find "qwen2.5:3b" >NUL 2>&1
if errorlevel 1 (
    echo Pulling Qwen Model (This happens once)...
    ollama pull qwen2.5:3b
)

echo [3/3] Launching ELDA System...
echo ===================================================
echo NOTE: Initial launch may take 30s to load Voice/Laptop models.
echo Please look at the console for "Warmup: AI Models Ready".
echo ===================================================
python start.py
pause
