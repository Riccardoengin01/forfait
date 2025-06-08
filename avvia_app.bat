@echo off
REM Attiva l'ambiente virtuale e avvia l'app Streamlit
call venv\Scripts\activate.bat
streamlit run forfait.py
pause
