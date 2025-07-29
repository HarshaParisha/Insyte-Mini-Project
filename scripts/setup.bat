@echo off
echo 🧠 Insyte AI - Windows Setup Script
echo =====================================

echo.
echo 📁 Setting up project directory...

:: Create virtual environment
echo 🐍 Creating Python virtual environment...
python -m venv venv

:: Activate virtual environment  
echo ⚡ Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo 📥 Installing Python dependencies...
echo This may take 10-15 minutes depending on your internet connection...
pip install -r requirements.txt

:: Create necessary directories
echo 📂 Creating data directories...
if not exist "data\database" mkdir data\database
if not exist "data\models" mkdir data\models
if not exist "logs" mkdir logs

:: Run setup and testing script
echo 🧪 Running setup and testing...
python scripts\setup_and_test.py

echo.
echo ✅ Setup complete!
echo.
echo 🚀 To start Insyte AI:
echo 1. Activate the environment: venv\Scripts\activate.bat
echo 2. Run the dashboard: streamlit run src\dashboard\main.py
echo.
pause
