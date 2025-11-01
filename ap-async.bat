@echo off
setlocal
setlocal enabledelayedexpansion

set "PLAYERS=C:\Games\Archipelago\Players\"
set "GENERATE=C:\Games\Archipelago\ArchipelagoGenerate.exe"

:: --- Select generation mode ---
echo Select generation mode:
echo 1 = Count
echo 2 = Weights
echo 3 = Quit
choice /c 123 /n /m "Enter choice (1-3): "
set "CHOICE=%ERRORLEVEL%"

if "%CHOICE%"=="3" (
    echo Quitting.
    exit /b
)

if "%CHOICE%"=="1" (
    set "GENERATION=count"
) else if "%CHOICE%"=="2" (
    set "GENERATION=weights"
) else (
    echo Invalid choice, quitting.
    exit /b
)

:: --- Number of multiworlds ---
set /p NUM_MULTIWORLDS="Enter number of multiworlds to create (0 to quit): "
if "%NUM_MULTIWORLDS%"=="0" (
    echo User chose 0, exiting.
    exit /b
)

:: --- Clean up old files ---
echo Cleaning up old files in Archipelago Players directory
del "%PLAYERS%\*.yaml"

:: --- Copy new files ---
echo Copying files to Archipelago Players directory
copy "output\*.yaml" "%PLAYERS%"

:: --- Number of players if weights ---
set "MULTI_ARGS="
if /i "%GENERATION%"=="weights" (
    set /p NUM_PLAYERS="Number of players in each multiworld: "
    if not "!NUM_PLAYERS!"=="" (
        set "MULTI_ARGS=--multi !NUM_PLAYERS!"
    )
)

:: --- Generate ---
echo Generating...
for /L %%i in (1,1,%NUM_MULTIWORLDS%) do (
    echo Running: "%GENERATE%" --csv_output --spoiler 0 %MULTI_ARGS%
    "%GENERATE%" --csv_output --spoiler 0 %MULTI_ARGS%
)

echo Done.
