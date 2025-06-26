# Missive MCP Server

Model Context Protocol (MCP) server for accessing Missive conversations in Claude Desktop.

## 🎯 What This Provides

- **Get Conversations**: Retrieve recent conversations from your Missive inbox
- **Secure Authentication**: Uses your personal Missive API token
- **Claude Integration**: Works seamlessly with Claude Desktop
- **Local Execution**: Runs entirely on your machine for privacy and security

## 📁 Project Structure

```
missive-mcp/
├── local-server/
│   ├── main.py            # MCP server implementation
│   ├── requirements.txt   # Python dependencies
│   └── install.sh         # Automated setup script
├── README.md              # This file
└── LICENSE                # MIT License
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
cd local-server
./install.sh
```

The script will:
- Create a virtual environment
- Install dependencies
- Show you the exact configuration for Claude Desktop

### Option 2: Manual Setup

1. **Create virtual environment:**
   ```bash
   cd local-server
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get your Missive API token:**
   - Go to Missive → Settings → API
   - Create a new API token
   - Copy the token (starts with `missive_pat-...`)

## ⚙️ Claude Desktop Configuration

Add this to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "missive": {
      "command": "/path/to/missive-mcp/local-server/.venv/bin/python",
      "args": ["/path/to/missive-mcp/local-server/main.py"],
      "env": {
        "MISSIVE_API_TOKEN": "YOUR_MISSIVE_API_TOKEN_HERE"
      }
    }
  }
}
```

**Important**: 
- Replace `/path/to/missive-mcp/` with the actual path to this project
- Replace `YOUR_MISSIVE_API_TOKEN_HERE` with your actual Missive API token
- On Windows, use `.venv\Scripts\python.exe` instead of `.venv/bin/python`

## 🧪 Testing

1. **Restart Claude Desktop** completely (quit and reopen)
2. **Test the connection** by asking Claude:
   - "Show me my recent email conversations"
   - "What's in my Missive inbox?"
   - "Get my latest conversations"

## 🔧 How It Works

- **Local execution**: Runs as a local process launched by Claude Desktop
- **Stdio transport**: Uses standard input/output for MCP communication
- **Environment variables**: API token passed securely via environment
- **Direct API calls**: Connects directly to Missive API from your machine

## 🔐 Security Features

- ✅ **No hardcoded tokens**: You provide your own API token
- ✅ **Local processing**: All data stays on your machine
- ✅ **Environment variables**: Secure token storage
- ✅ **Direct API calls**: No intermediary services
- ✅ **Minimal permissions**: Only reads conversations

## 🛠 Troubleshooting

### Connection Errors
1. **Check paths**: Ensure the paths in your Claude config are correct
2. **Verify token**: Make sure your Missive API token is valid
3. **Check permissions**: Ensure `main.py` is executable (`chmod +x main.py`)
4. **Python path**: Verify the virtual environment Python path is correct

### Common Issues
- **"spawn ENOENT"**: Wrong Python path in Claude config
- **"nodename nor servname provided"**: Network connectivity issue
- **"Invalid API token"**: Check your Missive API token

### Getting Help
1. Check the Claude Desktop logs for detailed error messages
2. Test your API token with curl:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        "https://public.missiveapp.com/v1/conversations?inbox=true&limit=5"
   ```

## 🧑‍💻 Development

### Local Testing
```bash
cd local-server
source .venv/bin/activate
MISSIVE_API_TOKEN="your_token" python main.py
```

### Adding Features
The server uses the [FastMCP](https://github.com/jlowin/fastmcp) framework. To add new tools:

1. Add a new function decorated with `@mcp.tool`
2. Use the Missive API documentation: https://learn.missiveapp.com/api-documentation
3. Follow the existing pattern in `main.py`

## 📚 API Reference

This server currently implements:

- **`get_conversations`**: Retrieves recent conversations from your Missive inbox

Future tools could include:
- Send messages
- Create tasks
- Search conversations
- Manage labels

## 🤝 Contributing

Contributions welcome! This project demonstrates:
- FastMCP framework usage
- Secure API token handling
- Claude Desktop integration patterns
- Local MCP server best practices

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [FastMCP](https://github.com/jlowin/fastmcp) - The MCP framework used
- [Missive API](https://learn.missiveapp.com/api-documentation) - Official API documentation
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
