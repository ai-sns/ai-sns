@echo off
REM ============================================================
REM RPM + Mixamo Animation Binding Tool
REM Uses Blender headless to retarget Mixamo animation onto RPM model
REM ============================================================

setlocal

REM Path to Blender executable (update if installed elsewhere)
set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.3\blender.exe

REM Default paths (edit these or pass as arguments)
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..\..

REM Check for command line arguments
if "%~1"=="" (
    echo Usage: rpm_mixamo_bind.bat [rpm_glb] [mixamo_fbx] [output_glb]
    echo.
    echo Example:
    echo   rpm_mixamo_bind.bat cankao2\man.glb cankao2\Idle.fbx cankao2\man_idle.glb
    echo.
    echo Running with default paths...
    set RPM_FILE=%PROJECT_DIR%\cankao2\man.glb
    set ANIM_FILE=%PROJECT_DIR%\cankao2\Idle.fbx
    set OUTPUT_FILE=%PROJECT_DIR%\cankao2\man_idle.glb
) else (
    set RPM_FILE=%~1
    set ANIM_FILE=%~2
    set OUTPUT_FILE=%~3
)

echo.
echo RPM model:  %RPM_FILE%
echo Animation:  %ANIM_FILE%
echo Output:     %OUTPUT_FILE%
echo.

"%BLENDER_EXE%" --background --python "%SCRIPT_DIR%rpm_mixamo_bind.py" -- --rpm "%RPM_FILE%" --anim "%ANIM_FILE%" --output "%OUTPUT_FILE%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully!
) else (
    echo.
    echo Build failed with error code %ERRORLEVEL%
)

pause
