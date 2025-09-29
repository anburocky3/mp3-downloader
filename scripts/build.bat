@echo off

echo [INFO] Building the executable...

pip install -r requirements.txt

echo [INFO] Ensuring Playwright browsers are installed in the local project directory
set PLAYWRIGHT_BROWSERS_PATH=0

echo [INFO] Installing Playwright Chromium browser
playwright install chromium

echo [INFO] Building with PyInstaller
pyinstaller -F --onedir --name "MP3Downloader" --version-file=scripts/version.txt --icon=scripts/app.ico --copy-metadata readchar --distpath --noconfirm dist main.py

echo [SUCCESS] Build has completed. The executable is located in the dist folder.

if not exist dist\MP3Downloader\MP3Downloader.exe (
    echo [ERROR] Build failed! Check the output above for details.
)

pause
