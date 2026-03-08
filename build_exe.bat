@echo off
setlocal

if not exist venv (
  py -m venv venv
)

call venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt pyinstaller

pyinstaller --noconfirm --clean --name webp_converter --windowed --onefile app.py

echo.
echo Build completed. EXE is in dist\webp_converter.exe
pause
