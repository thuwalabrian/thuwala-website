@echo off
cd /d "C:\Users\DMZ\Desktop\thuwala-website"
call thuwala\Scripts\activate.bat
echo Thuwala virtual environment activated!
echo Python: %python%
python --version
cmd /k