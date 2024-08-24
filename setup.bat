@echo off
chcp 65001 > nul

color 3

echo ┳┓┏┓  ┳┳┏┓┓ ┏┓┏┓┳┓┏┓┳┓  ┏┓┏┓┏┳┓┳┳┏┓
echo ┣┫┃┃━━┃┃┃┃┃ ┃┃┣┫┃┃┣ ┣┫  ┗┓┣  ┃ ┃┃┃┃
echo ┛┗┗┛  ┗┛┣┛┗┛┗┛┛┗┻┛┗┛┛┗  ┗┛┗┛ ┻ ┗┛┣┛
echo    

echo Made by 5nz!

echo Installing requirements!

pip install -r requirements.txt
if %errorlevel%==0 (
  del setup.bat
  del requirements.txt
)