@echo off
echo ========================================
echo   PaperHub quick start script
echo ========================================
echo.

echo [1/4] Check Docker container status...
docker-compose ps

echo.
echo [2/4] Start PostgreSQL database...
docker-compose up -d

echo.
echo [3/4] Wait for database to be ready...
timeout /t 15 /nobreak

echo.
echo [4/4] Initialize database tables...
python -m app.database

echo.
echo ========================================
echo   Launching Streamlit app...
echo   The browser will automatically open http://localhost:8501
echo ========================================
echo.

python -m streamlit run app/main.py

pause
