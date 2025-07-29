#!/bin/bash

echo "🧠 Insyte AI - Unix/Linux Setup Script"
echo "======================================"

echo ""
echo "📁 Setting up project directory..."

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "📥 Installing Python dependencies..."
echo "This may take 10-15 minutes depending on your internet connection..."
pip install -r requirements.txt

# Create necessary directories
echo "📂 Creating data directories..."
mkdir -p data/database
mkdir -p data/models
mkdir -p logs

# Make scripts executable
chmod +x scripts/*.sh

# Run setup and testing script
echo "🧪 Running setup and testing..."
python scripts/setup_and_test.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start Insyte AI:"
echo "1. Activate the environment: source venv/bin/activate"
echo "2. Run the dashboard: streamlit run src/dashboard/main.py"
echo ""
