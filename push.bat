@echo off
REM Healthcare Hackathon - Git Push Script
REM This script pushes code to GitHub

echo Pushing code to GitHub...
echo.

REM Add all changes
git add .

REM Commit with timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
git commit -m "Update: %mydate% %mytime%"

REM Push to main branch
git push -u origin main

echo.
echo Code pushed to GitHub successfully!
pause
