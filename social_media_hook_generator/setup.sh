#!/bin/bash
# Quick Setup Script for Social Media Hook Generator
# Run this script to set up the project quickly

echo "🚀 Setting up Social Media Hook Generator..."
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $(python --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate  # On Windows, this would be: venv\Scripts\activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys!"
    echo "   - Get Google Gemini API key: https://makersuite.google.com/app/apikey"
    echo "   - Optional: Get Twitter Bearer Token for trending hashtags"
else
    echo "✅ .env file already exists"
fi

# Generate secret key if not set
if ! grep -q "SECRET_KEY=your-secret-key-here" .env; then
    echo "🔑 Secret key already configured"
else
    echo "🔑 Generating new secret key..."
    python -c "
import secrets
import os
key = secrets.token_hex(32)
with open('.env', 'r') as f:
    content = f.read()
content = content.replace('SECRET_KEY=your-secret-key-here', f'SECRET_KEY={key}')
with open('.env', 'w') as f:
    f.write(content)
    print('✅ Secret key generated and saved')
"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: python app.py"
echo "3. Open http://localhost:5000 in your browser"
echo ""
echo "📖 For detailed setup instructions, see SETUP_GUIDE.md"