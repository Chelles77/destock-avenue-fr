@echo off
cd /d C:\Users\nqair\OneDrive\Bureau\ReventePro_V4\destock-avenue-fr\backend
start cmd /k "npm start"
timeout /t 3
cd /d C:\Users\nqair\OneDrive\Bureau\ReventePro_V4\destock-avenue-fr
start cmd /k "python -m http.server 5500"
