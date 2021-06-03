@echo off

setlocal

set PYTHON_EXE=%~dp0\python\python.exe
set SCRIPT=%~dp0\cal_ui.py
set /p YEAR=Which year you would like to calculate?:
set /p MONTH=Which month you would like to calculate?:
%PYTHON_EXE% %SCRIPT% %YEAR% %MONTH%

endlocal