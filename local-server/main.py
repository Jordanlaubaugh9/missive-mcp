#!/usr/bin/env python3
import os
import httpx
from fastmcp import FastMCP

# Initialize FastMCP server for local stdio use
mcp = FastMCP("Missive MCP")

@mcp.tool
async def get_conversations() -> str:
    """Get recent conversations from Missive inbox"""
    
    # Get API token from environment variable (set by Claude Desktop)
    api_token = os.getenv("MISSIVE_API_TOKEN")
    
    if not api_token:
        return "Error: MISSIVE_API_TOKEN not set in environment"
    
    # Use the token to call Missive API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/conversations",
                headers={"Authorization": f"Bearer {api_token}"},
                params={"inbox": "true", "limit": 10}
            )
            response.raise_for_status()
            data = response.json()
            
            # Format conversations for display
            conversations = data.get("conversations", [])
            if not conversations:
                return "No conversations found in your Missive inbox"
            
            result = "📧 Recent Missive Conversations:\n\n"
            for conv in conversations[:5]:  # Show first 5
                subject = conv.get("latest_message_subject", "No subject")
                authors = ", ".join([a.get("name", "Unknown") for a in conv.get("authors", [])])
                result += f"• {subject}\n  From: {authors}\n\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            else:
                return f"Error fetching conversations: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching conversations: {str(e)}"

# Run the server in stdio mode only (for Claude Desktop)
if __name__ == "__main__":
    mcp.run()
