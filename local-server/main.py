#!/usr/bin/env python3
import os
import json
from datetime import datetime
from typing import Optional, List
import httpx
from fastmcp import FastMCP

# Initialize FastMCP server for local stdio use
mcp = FastMCP("Missive MCP")

# Helper function to get API token
def get_api_token():
    """Get API token from environment variable"""
    api_token = os.getenv("MISSIVE_API_TOKEN")
    if not api_token:
        raise ValueError("MISSIVE_API_TOKEN not set in environment")
    return api_token

# Helper function to format timestamp
def format_timestamp(timestamp):
    """Convert Unix timestamp to readable date"""
    if timestamp:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
    return "Not set"

# ============================================================================
# CONVERSATION ENDPOINTS
# ============================================================================

@mcp.tool
async def get_conversations() -> str:
    """Get recent conversations from Missive inbox"""
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/conversations",
                headers={"Authorization": f"Bearer {api_token}"},
                params={"inbox": "true", "limit": 10}
            )
            response.raise_for_status()
            data = response.json()
            
            conversations = data.get("conversations", [])
            if not conversations:
                return "No conversations found in your Missive inbox"
            
            result = "📧 Recent Missive Conversations:\n\n"
            for conv in conversations[:5]:
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

@mcp.tool
async def get_conversations_filtered(
    mailbox: str = "inbox",
    limit: int = 10,
    team_id: Optional[str] = None
) -> str:
    """Get conversations with filtering options.
    
    Args:
        mailbox: Filter by mailbox (inbox, all, assigned, closed, flagged, trashed, junked, snoozed)
        limit: Number of conversations to return (max 50)
        team_id: Optional team ID to filter by team conversations
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    # Build parameters based on mailbox type
    params = {"limit": min(limit, 50)}
    
    if mailbox == "inbox":
        params["inbox"] = "true"
    elif mailbox == "all":
        params["all"] = "true"
    elif mailbox == "assigned":
        params["assigned"] = "true"
    elif mailbox == "closed":
        params["closed"] = "true"
    elif mailbox == "flagged":
        params["flagged"] = "true"
    elif mailbox == "trashed":
        params["trashed"] = "true"
    elif mailbox == "junked":
        params["junked"] = "true"
    elif mailbox == "snoozed":
        params["snoozed"] = "true"
    else:
        return f"Error: Invalid mailbox '{mailbox}'. Valid options: inbox, all, assigned, closed, flagged, trashed, junked, snoozed"
    
    if team_id:
        if mailbox == "inbox":
            params = {"team_inbox": team_id, "limit": min(limit, 50)}
        elif mailbox == "closed":
            params = {"team_closed": team_id, "limit": min(limit, 50)}
        elif mailbox == "all":
            params = {"team_all": team_id, "limit": min(limit, 50)}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/conversations",
                headers={"Authorization": f"Bearer {api_token}"},
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            conversations = data.get("conversations", [])
            if not conversations:
                return f"No conversations found in {mailbox} mailbox"
            
            result = f"📧 Conversations from {mailbox.title()} ({len(conversations)} found):\n\n"
            for conv in conversations:
                subject = conv.get("latest_message_subject", "No subject")
                authors = ", ".join([a.get("name", "Unknown") for a in conv.get("authors", [])])
                assignees = conv.get("assignee_names", "Unassigned")
                tasks_count = conv.get("tasks_count", 0)
                
                result += f"• {subject}\n"
                result += f"  From: {authors}\n"
                if assignees:
                    result += f"  Assigned: {assignees}\n"
                if tasks_count > 0:
                    result += f"  Tasks: {tasks_count}\n"
                result += f"  ID: {conv.get('id')}\n\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            else:
                return f"Error fetching conversations: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching conversations: {str(e)}"

@mcp.tool
async def get_conversation_details(conversation_id: str) -> str:
    """Get detailed information about a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation to retrieve
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://public.missiveapp.com/v1/conversations/{conversation_id}",
                headers={"Authorization": f"Bearer {api_token}"}
            )
            response.raise_for_status()
            data = response.json()
            
            conversations = data.get("conversations", [])
            if not conversations:
                return f"Conversation {conversation_id} not found"
            
            conv = conversations[0]
            
            result = f"📧 Conversation Details:\n\n"
            result += f"Subject: {conv.get('latest_message_subject', 'No subject')}\n"
            result += f"ID: {conv.get('id')}\n"
            
            # Authors
            authors = conv.get("authors", [])
            if authors:
                result += f"Authors: {', '.join([a.get('name', 'Unknown') for a in authors])}\n"
            
            # Assignees
            assignees = conv.get("assignee_names", "")
            if assignees:
                result += f"Assigned to: {assignees}\n"
            
            # Team
            team = conv.get("team")
            if team:
                result += f"Team: {team.get('name')}\n"
            
            # Organization
            org = conv.get("organization")
            if org:
                result += f"Organization: {org.get('name')}\n"
            
            # Counts
            result += f"Messages: {conv.get('messages_count', 0)}\n"
            result += f"Tasks: {conv.get('tasks_count', 0)} ({conv.get('completed_tasks_count', 0)} completed)\n"
            result += f"Attachments: {conv.get('attachments_count', 0)}\n"
            result += f"Drafts: {conv.get('drafts_count', 0)}\n"
            
            # Status
            users = conv.get("users", [])
            if users:
                user = users[0]
                status = []
                if user.get("assigned"): status.append("assigned")
                if user.get("closed"): status.append("closed")
                if user.get("archived"): status.append("archived")
                if user.get("flagged"): status.append("flagged")
                if user.get("snoozed"): status.append("snoozed")
                if user.get("trashed"): status.append("trashed")
                if user.get("junked"): status.append("junked")
                
                if status:
                    result += f"Status: {', '.join(status)}\n"
            
            # Shared labels
            shared_labels = conv.get("shared_label_names", "")
            if shared_labels:
                result += f"Labels: {shared_labels}\n"
            
            # Last activity
            last_activity = conv.get("last_activity_at")
            if last_activity:
                result += f"Last activity: {format_timestamp(last_activity)}\n"
            
            # URLs
            result += f"\nWeb URL: {conv.get('web_url', 'N/A')}\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: Conversation {conversation_id} not found"
            else:
                return f"Error fetching conversation: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching conversation: {str(e)}"

@mcp.tool
async def get_conversation_messages(conversation_id: str, limit: int = 5) -> str:
    """Get messages from a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation
        limit: Number of messages to return (max 10)
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://public.missiveapp.com/v1/conversations/{conversation_id}/messages",
                headers={"Authorization": f"Bearer {api_token}"},
                params={"limit": min(limit, 10)}
            )
            response.raise_for_status()
            data = response.json()
            
            messages = data.get("messages", [])
            if not messages:
                return f"No messages found in conversation {conversation_id}"
            
            result = f"💬 Messages in Conversation ({len(messages)} found):\n\n"
            
            for i, msg in enumerate(messages, 1):
                result += f"{i}. {msg.get('subject', 'No subject')}\n"
                
                # From field
                from_field = msg.get("from_field", {})
                if from_field:
                    result += f"   From: {from_field.get('name', 'Unknown')} <{from_field.get('address', 'unknown')}>\n"
                
                # To fields
                to_fields = msg.get("to_fields", [])
                if to_fields:
                    to_names = [f"{t.get('name', 'Unknown')} <{t.get('address', 'unknown')}>" for t in to_fields]
                    result += f"   To: {', '.join(to_names)}\n"
                
                # Preview
                preview = msg.get("preview", "")
                if preview:
                    result += f"   Preview: {preview[:100]}{'...' if len(preview) > 100 else ''}\n"
                
                # Delivered time
                delivered_at = msg.get("delivered_at")
                if delivered_at:
                    result += f"   Delivered: {format_timestamp(delivered_at)}\n"
                
                # Attachments
                attachments = msg.get("attachments", [])
                if attachments:
                    result += f"   Attachments: {len(attachments)} file(s)\n"
                
                result += f"   Message ID: {msg.get('id')}\n\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: Conversation {conversation_id} not found"
            else:
                return f"Error fetching messages: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching messages: {str(e)}"

@mcp.tool
async def get_conversation_comments(conversation_id: str, limit: int = 5) -> str:
    """Get comments from a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation
        limit: Number of comments to return (max 10)
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://public.missiveapp.com/v1/conversations/{conversation_id}/comments",
                headers={"Authorization": f"Bearer {api_token}"},
                params={"limit": min(limit, 10)}
            )
            response.raise_for_status()
            data = response.json()
            
            comments = data.get("comments", [])
            if not comments:
                return f"No comments found in conversation {conversation_id}"
            
            result = f"💭 Comments in Conversation ({len(comments)} found):\n\n"
            
            for i, comment in enumerate(comments, 1):
                result += f"{i}. {comment.get('body', 'No content')}\n"
                
                # Author
                author = comment.get("author", {})
                if author:
                    result += f"   By: {author.get('name', 'Unknown')} <{author.get('email', 'unknown')}>\n"
                
                # Created time
                created_at = comment.get("created_at")
                if created_at:
                    result += f"   Created: {format_timestamp(created_at)}\n"
                
                # Task info
                task = comment.get("task")
                if task:
                    result += f"   Task: {task.get('description', 'No description')}\n"
                    result += f"   Task State: {task.get('state', 'unknown')}\n"
                    
                    due_at = task.get("due_at")
                    if due_at:
                        result += f"   Due: {format_timestamp(due_at)}\n"
                    
                    assignees = task.get("assignees", [])
                    if assignees:
                        assignee_names = [a.get('name', 'Unknown') for a in assignees]
                        result += f"   Assigned to: {', '.join(assignee_names)}\n"
                
                # Attachment
                attachment = comment.get("attachment")
                if attachment:
                    result += f"   Attachment: {attachment.get('filename', 'Unknown file')}\n"
                
                result += f"   Comment ID: {comment.get('id')}\n\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: Conversation {conversation_id} not found"
            else:
                return f"Error fetching comments: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching comments: {str(e)}"

# ============================================================================
# TASK ENDPOINTS
# ============================================================================

@mcp.tool
async def create_task(
    title: str,
    description: str = "",
    organization_id: Optional[str] = None,
    team_id: Optional[str] = None,
    assignee_ids: Optional[List[str]] = None,
    due_date_timestamp: Optional[int] = None,
    conversation_id: Optional[str] = None,
    is_subtask: bool = False
) -> str:
    """Create a new task in Missive.
    
    Args:
        title: Task title (required, max 1000 characters)
        description: Task description (optional, max 10000 characters)
        organization_id: Organization ID (required when using team_id or assignee_ids)
        team_id: Team ID (either team_id or assignee_ids required for standalone tasks)
        assignee_ids: List of user IDs to assign (either team_id or assignee_ids required for standalone tasks)
        due_date_timestamp: Unix timestamp for due date (optional)
        conversation_id: Conversation ID for subtasks (required when is_subtask=True)
        is_subtask: Whether this is a subtask of a conversation
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    # Build task payload
    task_data = {
        "title": title[:1000],  # Limit to 1000 characters
        "description": description[:10000] if description else "",  # Limit to 10000 characters
    }
    
    # Add optional fields
    if organization_id:
        task_data["organization"] = organization_id
    
    if team_id:
        task_data["team"] = team_id
    
    if assignee_ids:
        task_data["assignees"] = assignee_ids
    
    if due_date_timestamp:
        task_data["due_at"] = due_date_timestamp
    
    if is_subtask:
        if not conversation_id:
            return "Error: conversation_id is required when creating a subtask"
        task_data["conversation"] = conversation_id
        task_data["subtask"] = True
    else:
        # For standalone tasks, either team or assignees is required
        if not team_id and not assignee_ids:
            return "Error: Either team_id or assignee_ids is required for standalone tasks"
    
    payload = {"tasks": task_data}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://public.missiveapp.com/v1/tasks",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            task = data.get("tasks", {})
            
            result = f"✅ Task Created Successfully!\n\n"
            result += f"Title: {task.get('title', 'Unknown')}\n"
            result += f"Description: {task.get('description', 'No description')}\n"
            result += f"State: {task.get('state', 'unknown')}\n"
            result += f"Task ID: {task.get('id')}\n"
            
            # Due date
            due_at = task.get("due_at")
            if due_at:
                result += f"Due: {format_timestamp(due_at)}\n"
            
            # Assignees
            assignees = task.get("assignees", [])
            if assignees:
                result += f"Assignees: {', '.join(assignees)}\n"
            
            # Team
            team = task.get("team")
            if team:
                result += f"Team: {team}\n"
            
            # Conversation (for subtasks)
            conversation = task.get("conversation")
            if conversation:
                result += f"Conversation: {conversation}\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 400:
                return f"Error: Invalid task data. Please check your parameters."
            else:
                return f"Error creating task: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error creating task: {str(e)}"

@mcp.tool
async def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    state: Optional[str] = None,
    assignee_ids: Optional[List[str]] = None,
    team_id: Optional[str] = None,
    due_date_timestamp: Optional[int] = None
) -> str:
    """Update an existing task.
    
    Args:
        task_id: ID of the task to update (required)
        title: New task title (optional, max 1000 characters)
        description: New task description (optional, max 10000 characters)
        state: New task state (optional: todo, in_progress, closed)
        assignee_ids: New list of user IDs to assign (optional)
        team_id: New team ID (optional)
        due_date_timestamp: New Unix timestamp for due date (optional)
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    # Build update payload with only provided fields
    task_data = {}
    
    if title is not None:
        task_data["title"] = title[:1000]
    
    if description is not None:
        task_data["description"] = description[:10000]
    
    if state is not None:
        if state not in ["todo", "in_progress", "closed"]:
            return "Error: state must be one of: todo, in_progress, closed"
        task_data["state"] = state
    
    if assignee_ids is not None:
        task_data["assignees"] = assignee_ids
    
    if team_id is not None:
        task_data["team"] = team_id
    
    if due_date_timestamp is not None:
        task_data["due_at"] = due_date_timestamp
    
    if not task_data:
        return "Error: At least one field must be provided to update"
    
    payload = {"tasks": task_data}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"https://public.missiveapp.com/v1/tasks/{task_id}",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            task = data.get("tasks", {})
            
            result = f"✅ Task Updated Successfully!\n\n"
            result += f"Title: {task.get('title', 'Unknown')}\n"
            result += f"Description: {task.get('description', 'No description')}\n"
            result += f"State: {task.get('state', 'unknown')}\n"
            result += f"Task ID: {task.get('id')}\n"
            
            # Due date
            due_at = task.get("due_at")
            if due_at:
                result += f"Due: {format_timestamp(due_at)}\n"
            
            # Assignees
            assignees = task.get("assignees", [])
            if assignees:
                result += f"Assignees: {', '.join(assignees)}\n"
            
            # Team
            team = task.get("team")
            if team:
                result += f"Team: {team}\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: Task {task_id} not found"
            elif e.response.status_code == 400:
                return f"Error: Invalid task data. Please check your parameters."
            else:
                return f"Error updating task: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error updating task: {str(e)}"

# ============================================================================
# MESSAGE ENDPOINTS
# ============================================================================

@mcp.tool
async def get_message_details(message_id: str) -> str:
    """Get full details of a specific message including body and attachments.
    
    Args:
        message_id: The ID of the message to retrieve
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://public.missiveapp.com/v1/messages/{message_id}",
                headers={"Authorization": f"Bearer {api_token}"}
            )
            response.raise_for_status()
            data = response.json()
            
            message = data.get("messages", {})
            if not message:
                return f"Message {message_id} not found"
            
            result = f"📨 Message Details:\n\n"
            result += f"Subject: {message.get('subject', 'No subject')}\n"
            result += f"Type: {message.get('type', 'unknown')}\n"
            result += f"Message ID: {message.get('id')}\n"
            
            # From field
            from_field = message.get("from_field", {})
            if from_field:
                result += f"From: {from_field.get('name', 'Unknown')} <{from_field.get('address', 'unknown')}>\n"
            
            # To fields
            to_fields = message.get("to_fields", [])
            if to_fields:
                to_names = [f"{t.get('name', 'Unknown')} <{t.get('address', 'unknown')}>" for t in to_fields]
                result += f"To: {', '.join(to_names)}\n"
            
            # CC fields
            cc_fields = message.get("cc_fields", [])
            if cc_fields:
                cc_names = [f"{c.get('name', 'Unknown')} <{c.get('address', 'unknown')}>" for c in cc_fields]
                result += f"CC: {', '.join(cc_names)}\n"
            
            # Timestamps
            delivered_at = message.get("delivered_at")
            if delivered_at:
                result += f"Delivered: {format_timestamp(delivered_at)}\n"
            
            created_at = message.get("created_at")
            if created_at:
                result += f"Created: {format_timestamp(created_at)}\n"
            
            # Preview
            preview = message.get("preview", "")
            if preview:
                result += f"Preview: {preview}\n"
            
            # Body (truncated for display)
            body = message.get("body", "")
            if body:
                # Remove HTML tags for cleaner display
                import re
                clean_body = re.sub('<[^<]+?>', '', body)
                result += f"Body: {clean_body[:500]}{'...' if len(clean_body) > 500 else ''}\n"
            
            # Attachments
            attachments = message.get("attachments", [])
            if attachments:
                result += f"\nAttachments ({len(attachments)}):\n"
                for att in attachments:
                    result += f"  • {att.get('filename', 'Unknown')} ({att.get('size', 0)} bytes)\n"
                    result += f"    Type: {att.get('media_type', 'unknown')}/{att.get('sub_type', 'unknown')}\n"
                    if att.get('width') and att.get('height'):
                        result += f"    Dimensions: {att.get('width')}x{att.get('height')}\n"
            
            # Conversation info
            conversation = message.get("conversation", {})
            if conversation:
                result += f"\nConversation: {conversation.get('latest_message_subject', 'No subject')}\n"
                result += f"Conversation ID: {conversation.get('id')}\n"
                
                # Team
                team = conversation.get("team", {})
                if team:
                    result += f"Team: {team.get('name')}\n"
                
                # Organization
                org = conversation.get("organization", {})
                if org:
                    result += f"Organization: {org.get('name')}\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: Message {message_id} not found"
            else:
                return f"Error fetching message: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching message: {str(e)}"

@mcp.tool
async def search_messages_by_email_id(email_message_id: str) -> str:
    """Find messages by email Message-ID header.
    
    Args:
        email_message_id: The Message-ID found in an email's header
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/messages",
                headers={"Authorization": f"Bearer {api_token}"},
                params={"email_message_id": email_message_id}
            )
            response.raise_for_status()
            data = response.json()
            
            messages = data.get("messages", [])
            if not messages:
                return f"No messages found with email Message-ID: {email_message_id}"
            
            result = f"📧 Messages found for Message-ID '{email_message_id}' ({len(messages)} found):\n\n"
            
            for i, message in enumerate(messages, 1):
                result += f"{i}. {message.get('subject', 'No subject')}\n"
                
                # From field
                from_field = message.get("from_field", {})
                if from_field:
                    result += f"   From: {from_field.get('name', 'Unknown')} <{from_field.get('address', 'unknown')}>\n"
                
                # To fields
                to_fields = message.get("to_fields", [])
                if to_fields:
                    to_names = [f"{t.get('name', 'Unknown')} <{t.get('address', 'unknown')}>" for t in to_fields]
                    result += f"   To: {', '.join(to_names)}\n"
                
                # Preview
                preview = message.get("preview", "")
                if preview:
                    result += f"   Preview: {preview[:100]}{'...' if len(preview) > 100 else ''}\n"
                
                # Delivered time
                delivered_at = message.get("delivered_at")
                if delivered_at:
                    result += f"   Delivered: {format_timestamp(delivered_at)}\n"
                
                # Message type
                msg_type = message.get("type", "unknown")
                result += f"   Type: {msg_type}\n"
                
                result += f"   Message ID: {message.get('id')}\n\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: No messages found with Message-ID: {email_message_id}"
            else:
                return f"Error searching messages: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error searching messages: {str(e)}"

@mcp.tool
async def create_custom_message(
    account_id: str,
    body: str,
    from_field_data: str,
    to_fields_data: str,
    subject: Optional[str] = None,
    conversation_id: Optional[str] = None
) -> str:
    """Create a message in a custom channel.
    
    Args:
        account_id: Account ID from custom channel settings
        body: HTML or text message body
        from_field_data: JSON string with sender info (e.g., '{"name": "John", "address": "john@example.com"}')
        to_fields_data: JSON string with recipients info (e.g., '[{"name": "Jane", "address": "jane@example.com"}]')
        subject: Email subject (for email channels only)
        conversation_id: Optional conversation ID to append to existing conversation
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    # Parse JSON strings
    try:
        from_field = json.loads(from_field_data)
        to_fields = json.loads(to_fields_data)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format in from_field_data or to_fields_data: {str(e)}"
    
    # Build message payload
    message_data = {
        "account": account_id,
        "body": body,
        "from_field": from_field,
        "to_fields": to_fields
    }
    
    if subject:
        message_data["subject"] = subject
    
    if conversation_id:
        message_data["conversation"] = conversation_id
    
    payload = {"messages": message_data}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://public.missiveapp.com/v1/messages",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            message = data.get("messages", {})
            
            result = f"📨 Message Created Successfully!\n\n"
            result += f"Subject: {message.get('subject', 'No subject')}\n"
            result += f"Type: {message.get('type', 'unknown')}\n"
            result += f"Message ID: {message.get('id')}\n"
            
            # From field
            from_field = message.get("from_field", {})
            if from_field:
                result += f"From: {from_field.get('name', 'Unknown')} <{from_field.get('address', 'unknown')}>\n"
            
            # To fields
            to_fields = message.get("to_fields", [])
            if to_fields:
                to_names = [f"{t.get('name', 'Unknown')} <{t.get('address', 'unknown')}>" for t in to_fields]
                result += f"To: {', '.join(to_names)}\n"
            
            # Delivered time
            delivered_at = message.get("delivered_at")
            if delivered_at:
                result += f"Delivered: {format_timestamp(delivered_at)}\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 400:
                return f"Error: Invalid message data. Please check your parameters."
            else:
                return f"Error creating message: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error creating message: {str(e)}"

# Run the server in stdio mode only (for Claude Desktop)
if __name__ == "__main__":
    mcp.run()
