"""
Gmail Tool for AI Employee Vault

Provides email operations via Gmail MCP server:
- send_email(to, subject, body) - Send emails
- search_email(query) - Search inbox

Authentication is handled automatically by the Gmail MCP server.
No additional setup required.

Usage:
    from tools.gmail_tool import send_email, search_email
    
    # Send an email
    result = send_email("to@example.com", "Subject", "Body text")
    print(result)  # "Email sent successfully"
    
    # Search emails
    results = search_email("in:inbox")
    print(results)  # "Search results retrieved" + email list
"""

import subprocess
import json
import sys
from pathlib import Path

# MCP Server configuration
MCP_SERVER = "@gongrzhe/server-gmail-autoauth-mcp"


def _call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """
    Call a Gmail MCP server tool.
    
    Args:
        tool_name: Name of the MCP tool to call
        arguments: Tool arguments as dictionary
    
    Returns:
        Response from MCP server
    """
    request = {
        "tool": tool_name,
        "arguments": arguments
    }
    
    try:
        result = subprocess.run(
            ["npx", "-y", MCP_SERVER],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"raw": result.stdout}
        
        if result.stderr:
            return {"error": result.stderr}
        
        return {"error": "No response from server"}
        
    except subprocess.TimeoutExpired:
        return {"error": "Request timed out"}
    except Exception as e:
        return {"error": str(e)}


def send_email(to: str, subject: str, body: str, html: bool = False) -> str:
    """
    Send an email via Gmail MCP server.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body content
        html: Set to True if body contains HTML (default: False)
    
    Returns:
        Human-readable status message:
        - "Email sent successfully"
        - "Email sent successfully to <recipient>"
        - Error message if sending failed
    
    Example:
        >>> send_email("user@example.com", "Meeting", "Let's meet at 3pm")
        'Email sent successfully'
    """
    arguments = {
        "to": to,
        "subject": subject,
        "body": body,
        "html": html
    }
    
    response = _call_mcp_tool("gmail_send_email", arguments)
    
    if response.get("success"):
        return f"Email sent successfully to {to}"
    
    error = response.get("error", "Unknown error")
    return f"Failed to send email: {error}"


def search_email(query: str = "in:inbox", max_results: int = 5) -> str:
    """
    Search emails via Gmail MCP server.
    
    Args:
        query: Gmail search query (default: "in:inbox")
               Examples: "from:example@gmail.com", "subject:meeting", "is:unread"
        max_results: Maximum number of emails to return (default: 5)
    
    Returns:
        Human-readable search results:
        - "Search results retrieved" followed by email summaries
        - "No emails found" if query returned no results
        - Error message if search failed
    
    Example:
        >>> search_email("in:inbox", max_results=3)
        'Search results retrieved:\\n1. From: John - Subject: Meeting...'
    """
    arguments = {
        "query": query,
        "max_results": max_results
    }
    
    response = _call_mcp_tool("gmail_search_emails", arguments)
    
    if "error" in response:
        return f"Search failed: {response['error']}"
    
    if "messages" in response or "emails" in response:
        emails = response.get("messages", response.get("emails", []))
        
        if not emails:
            return "No emails found"
        
        lines = ["Search results retrieved:"]
        for i, email in enumerate(emails, 1):
            subject = email.get("subject", "No subject")
            sender = email.get("from", "Unknown")
            date = email.get("date", "")
            lines.append(f"{i}. From: {sender} | Subject: {subject} | Date: {date}")
        
        return "\n".join(lines)
    
    # Raw response
    return f"Search results retrieved: {json.dumps(response, indent=2)}"


def read_email(message_id: str) -> str:
    """
    Read full email content by message ID.
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        Human-readable email content with headers and body
    """
    arguments = {"message_id": message_id}
    response = _call_mcp_tool("gmail_read_email", arguments)
    
    if "error" in response:
        return f"Failed to read email: {response['error']}"
    
    lines = [
        f"From: {response.get('from', 'Unknown')}",
        f"To: {response.get('to', 'Unknown')}",
        f"Subject: {response.get('subject', 'No subject')}",
        f"Date: {response.get('date', 'Unknown')}",
        "",
        response.get("body", "")
    ]
    
    return "\n".join(lines)


def mark_as_read(message_id: str) -> str:
    """
    Mark an email as read.
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        Status message indicating success or failure
    """
    arguments = {"message_id": message_id}
    response = _call_mcp_tool("gmail_mark_as_read", arguments)
    
    if response.get("success"):
        return "Email marked as read"
    
    return f"Failed to mark as read: {response.get('error', 'Unknown error')}"


def mark_as_unread(message_id: str) -> str:
    """
    Mark an email as unread.
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        Status message indicating success or failure
    """
    arguments = {"message_id": message_id}
    response = _call_mcp_tool("gmail_mark_as_unread", arguments)
    
    if response.get("success"):
        return "Email marked as unread"
    
    return f"Failed to mark as unread: {response.get('error', 'Unknown error')}"


def archive_email(message_id: str) -> str:
    """
    Archive an email.
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        Status message indicating success or failure
    """
    arguments = {"message_id": message_id}
    response = _call_mcp_tool("gmail_archive_email", arguments)
    
    if response.get("success"):
        return "Email archived"
    
    return f"Failed to archive: {response.get('error', 'Unknown error')}"


def delete_email(message_id: str) -> str:
    """
    Delete an email permanently.
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        Status message indicating success or failure
    """
    arguments = {"message_id": message_id}
    response = _call_mcp_tool("gmail_delete_email", arguments)
    
    if response.get("success"):
        return "Email deleted"
    
    return f"Failed to delete: {response.get('error', 'Unknown error')}"
