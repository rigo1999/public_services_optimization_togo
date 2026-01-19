@echo off
REM ============================================================================
REM Streamlit Dashboard Launcher - Services Publics Togo
REM ============================================================================
REM
REM Script de démarrage rapide du tableau de bord Streamlit
REM Vérifie les prérequis et lance l'application
REM

echo.
echo ============================================================================
echo  TABLEAU DE BORD STREAMLIT - SERVICES PUBLICS TOGO
echo ============================================================================
echo.

REM Vérifier que nous sommes dans le bon répertoire
if not exist "app_streamlit.py" (
    echo ERROR: app_streamlit.py not found
    echo Please run this script from the 04_Dashboard directory
    pause
    exit /b 1
)

REM Vérifier que le virtual environment existe
if not exist "..\\.venv\\Scripts\\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please ensure .venv is set up in the parent directory
    pause
    exit /b 1
)

echo [1/4] Activating Python virtual environment...
call ..\\.venv\\Scripts\\activate.bat

echo [2/4] Checking Python packages...
pip list | find "streamlit" >nul
if errorlevel 1 (
    echo [2/4] Installing Streamlit...
    pip install streamlit plotly psycopg2-binary -q
)

echo [3/4] Checking PostgreSQL connection (Docker container: service_public_db_togo)...
python -c "import psycopg2; conn=psycopg2.connect('host=localhost port=5434 user=postgres password=postgres database=service_public_db'); print('✓ PostgreSQL connection OK'); conn.close()" 2>nul
if errorlevel 1 (
    echo WARNING: Could not connect to PostgreSQL
    echo Make sure Docker container 'service_public_db_togo' is running
    echo Run: docker start service_public_db_togo
    echo.
)

echo [4/4] Launching Streamlit application...
echo.
echo Application will open at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.
timeout /t 2

streamlit run app_streamlit.py

pause
