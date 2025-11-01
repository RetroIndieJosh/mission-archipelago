@echo off

set "PLAYERS=C:\Games\Archipelago\Players\"
set "GENERATE=C:\Games\Archipelago\ArchipelagoGenerate.exe"

if "%~1"=="" (
    set "NUM_MULTIWORLDS=1"
) else (
    set /a test=%~1 >nul 2>&1
    if errorlevel 1 (
        echo Expected number of worlds as second argument but got '%~1'
        exit
    ) 
    set "NUM_MULTIWORLDS=%~1"
)

echo Cleaning up old files in Archipelago Players directory
del "%PLAYERS%\*.yaml"

echo Copying files to Archipelago Players directory
copy "output\*.yaml" "%PLAYERS%"

echo Creating %NUM_MULTIWORLDS% multiworlds.
set /p num_players="Number of players in each multiworld: "

echo Generating...
for /L %%i in (1, 1, %NUM_MULTIWORLDS%) do (
    call "C:\Games\Archipelago\ArchipelagoGenerate.exe" --csv_output --spoiler 0 --multi %num_players%
)
echo Done.