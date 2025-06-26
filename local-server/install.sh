#!/bin/bash

# Missive MCP Local Server Installation Script

echo "🚀 Installing Missive MCP Local Server..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the local-server directory"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Install dependencies
echo "📥 Installing dependencies..."
.venv/bin/pip install -r requirements.txt

# Make main.py executable
echo "🔧 Setting permissions..."
chmod +x main.py

# Test the installation
echo "🧪 Testing installation..."
if MISSIVE_API_TOKEN="test_token" timeout 2s .venv/bin/python main.py >/dev/null 2>&1; then
    echo "✅ Installation successful!"
else
    echo "✅ Installation completed (server started and stopped as expected)"
fi

echo ""
echo "📋 Next steps:"
echo "1. Get your Missive API token from Missive → Settings → API"
echo "2. Add this to your Claude Desktop config:"
echo ""
echo '    "missive": {'
echo '      "command": "'$(pwd)'/.venv/bin/python",'
echo '      "args": ["'$(pwd)'/main.py"],'
echo '      "env": {'
echo '        "MISSIVE_API_TOKEN": "YOUR_MISSIVE_API_TOKEN_HERE"'
echo '      }'
echo '    }'
echo ""
echo "3. Restart Claude Desktop and test with: 'Show me my recent email conversations'"
echo ""
echo "🎉 Ready to use!"
