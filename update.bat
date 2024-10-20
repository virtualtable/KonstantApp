@echo off
set url=https://raw.githubusercontent.com/Whatmanhere/KonstantApp/main/konstant.py
set filename=konstant.py

if exist %filename% del %filename%

curl -o %filename% %url%

python %filename%
