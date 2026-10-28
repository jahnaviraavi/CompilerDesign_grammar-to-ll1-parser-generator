@echo off
echo Installing required package...
py -m pip install -r requirements.txt
echo.
echo Starting Grammar to LL(1) Parser Generator...
py -m streamlit run app.py
pause
