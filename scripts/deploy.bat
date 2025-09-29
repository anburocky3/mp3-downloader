@echo off
REM deploy.bat - full build, package, and release script

REM Change to repository root (parent of this scripts folder)
cd /d "%~dp0.."

echo === Deploy script started ===

REM Ensure Python is available for version extraction
where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python not found in PATH. Activate your venv or install Python.
  pause
  exit /b 1
)

echo Extracting FileVersion and ProductVersion using Python helper...
if not exist scripts\extract_version.py (
  echo ERROR: scripts\extract_version.py not found. Cannot extract versions.
  pause
  exit /b 1
)

python scripts\extract_version.py > scripts\version_extracted.tmp 2> scripts\version_extracted.err
if errorlevel 1 (
  echo ERROR: Failed to run Python helper to extract versions. See scripts\version_extracted.err for details.
  type scripts\version_extracted.err
  pause
  exit /b 1
)

set "FILE_VERSION="
set "PRODUCT_VERSION="
if exist scripts\version_extracted.tmp (
  set /p FILE_VERSION=<scripts\version_extracted.tmp
  for /f "skip=1 delims=" %%V in (scripts\version_extracted.tmp) do (
    set "PRODUCT_VERSION=%%V"
    goto :after_read_versions
  )
)
:after_read_versions
if exist scripts\version_extracted.tmp del scripts\version_extracted.tmp
if exist scripts\version_extracted.err del scripts\version_extracted.err

echo FileVersion: %FILE_VERSION%
echo ProductVersion: %PRODUCT_VERSION%

REM Prefer ProductVersion for the release tag; fallback to FileVersion if missing
if not "%PRODUCT_VERSION%"=="" (
  set "VERSION=%PRODUCT_VERSION%"
) else (
  set "VERSION=%FILE_VERSION%"
)
if "%VERSION%"=="" (
  echo ERROR: No version value found to use for the release tag.
  pause
  exit /b 1
)
set "VERSION_TAG=v%VERSION%"
echo Using release tag: %VERSION_TAG%

REM === Build step: prefer scripts\deploy.bat (existing), fallback to scripts\build.bat ===
if exist scripts\build.bat (
  echo Running scripts\build.bat to build EXE...
  call scripts\build.bat
) else (
  echo Warning: no build script found. Ensure you build the EXE before running deploy.
)

REM === Package: compress dist folder => dist\MP3Downloader_v{version}.zip ===
set "ZIP_NAME=MP3Downloader_%VERSION_TAG%.zip"
set "ZIP_PATH=dist\%ZIP_NAME%"
if exist dist (
  echo Creating zip of dist folder: %ZIP_PATH% ...
  powershell -NoProfile -NonInteractive -Command "if(Test-Path -Path 'dist') { Remove-Item -LiteralPath '%ZIP_PATH%' -ErrorAction SilentlyContinue }; Compress-Archive -Path 'dist\*' -DestinationPath '%ZIP_PATH%' -Force"
  if errorlevel 1 (
    echo ERROR: Failed to create zip of dist folder.
    pause
    exit /b 1
  )
) else (
  echo ERROR: dist folder not found. Build may have failed.
  pause
  exit /b 1
)

REM === Create GitHub release (if gh available) ===
where gh >nul 2>nul
if errorlevel 1 (
  echo Note: GitHub CLI (gh) not found. Skipping automatic release creation.
  echo To upload manually, run:
  echo   gh release create %VERSION_TAG% "%ZIP_PATH%" --title "%VERSION_TAG%" --notes "Release %VERSION_TAG%"
) else (
  echo Creating GitHub release %VERSION_TAG% and uploading %ZIP_PATH% ...
  gh release create %VERSION_TAG% "%ZIP_PATH%" --title "%VERSION_TAG%" --notes "Release %VERSION_TAG%"
  if errorlevel 1 (
    echo ERROR: gh release command failed. Check authentication and network.
  ) else (
    echo GitHub release created successfully.
  )
)

echo ================================
echo Successfully prepared release %VERSION_TAG%.
echo Package: %ZIP_PATH%
echo ===============================

color 0a
echo Done.
pause