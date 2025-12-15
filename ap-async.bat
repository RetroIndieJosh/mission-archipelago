@echo off
setlocal EnableDelayedExpansion

set "AP_ROOT=C:\Games\Archipelago"
set "PLAYERS=%AP_ROOT%\Players"
set "GENERATE=%AP_ROOT%\ArchipelagoGenerate.exe"
set "ASYNC_ROOT=%AP_ROOT%\output"

set "META=output\ffr.meta"

:: --- Validate meta file ---
if not exist "%META%" (
    echo Missing ffr.meta. If you expect FFR in the generator, you will be sorely disappointed.
    pause
)

set "FF_COUNT=0"

if exist "%META%" (
    :: --- Read meta ---
    for /f "usebackq tokens=1,2 delims==" %%A in ("%META%") do (
        if "%%A"=="count" set "FF_COUNT=%%B"
    )

    :: --- Create async directory ---
    for /f %%T in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TIMESTAMP=%%T
    set "ASYNC_DIR=%ASYNC_ROOT%\async_%TIMESTAMP%"

    echo Creating directory: "%ASYNC_DIR%"
    mkdir "%ASYNC_DIR%"

    :: --- Copy NES files ---
    if %FF_COUNT% GTR 0 (
        echo Copying Final Fantasy ROMs to %ASYNC_DIR%
        for /L %%I in (1,1,%FF_COUNT%) do (
            copy "%FF_SOURCE%\Final Fantasy_%%I.nes" "%ASYNC_DIR%" >nul
        )
    )
)

:: --- Clean up old YAMLs ---
del "%PLAYERS%\*.yaml" >nul 2>&1

:: --- Copy YAMLs ---
copy "output\*.yaml" "%PLAYERS%" >nul

:: --- Generate ---
echo Generating...
"%GENERATE%" --csv_output --spoiler 1

echo Done.
