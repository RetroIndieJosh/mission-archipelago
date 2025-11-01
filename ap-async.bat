@echo off
setlocal

set "PLAYERS=C:\Games\Archipelago\Players\"
set "GENERATE=C:\Games\Archipelago\ArchipelagoGenerate.exe"
set "CONFIG=async.yaml"

:: Determine generation type from async.yaml
for /f "delims=" %%G in ('powershell -NoProfile -Command ^
    "(Get-Content '%CONFIG%' | ConvertFrom-Yaml).generation"') do (
    set "GENERATION=%%G"
)

if "%~1"=="" (
    set "NUM_MULTIWORLDS=1"
) else (
    set /a test=%~1 >nul 2>&1
    if errorlevel 1 (
        echo Expected number of worlds as argument but got '%~1'
        exit /b
    ) 
    set "NUM_MULTIWORLDS=%~1"
)

echo Cleaning up old files in Archipelago Players directory
del "%PLAYERS%\*.yaml"

echo Copying files to Archipelago Players directory
copy "output\*.yaml" "%PLAYERS%"

echo Creating %NUM_MULTIWORLDS% multiworlds.

:: Only ask for num_players if generation is 'weights'
set "MULTI_ARGS="
if /i "%GENERATION%"=="weights" (
    :ask_players
    set /p num_players="Number of players in each multiworld (WEIGHTS ONLY - 0 to quit): "

    :: check if num_players is numeric
    set /a testnum=%num_players% >nul 2>&1
    if errorlevel 1 (
        echo Invalid input. Please enter a positive integer or 0 to quit.
        goto ask_players
    )

    if %num_players%==0 (
        echo User chose 0, exiting.
        exit /b
    )

    if %num_players% LSS 0 (
        echo Negative numbers are not allowed.
        goto ask_players
    )

    set "MULTI_ARGS=--multi %num_players%"
)

echo Generating...
for /L %%i in (1,1,%NUM_MULTIWORLDS%) do (
    "%GENERATE%" --csv_output --spoiler 0 %MULTI_ARGS%
)
echo Done.
