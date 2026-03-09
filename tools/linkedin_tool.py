"""
LinkedIn Automation Tool for AI Employee Vault

Provides LinkedIn post management with approval workflow:
- draft_post(content) - Create draft in Plans folder
- approve_post(post_id) - Move post from Pending_Approval to Approved
- publish_post(post_id) - Publish and move to Done folder

Post Workflow:
    Plans → Pending_Approval → Approved → Done

Each post is stored as a JSON file with metadata.

Usage:
    from tools.linkedin_tool import draft_post, approve_post, publish_post
    
    # Create a draft post
    result = draft_post("Excited to share our new product!")
    
    # Approve a post for publishing
    result = approve_post("post_001")
    
    # Publish to LinkedIn
    result = publish_post("post_001")
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Base directory for post folders (project root)
BASE_DIR = Path(__file__).parent.parent
POSTS_BASE = BASE_DIR / "linkedin_posts"

# Workflow folders
FOLDER_PLANS = POSTS_BASE / "Plans"
FOLDER_PENDING = POSTS_BASE / "Pending_Approval"
FOLDER_APPROVED = POSTS_BASE / "Approved"
FOLDER_DONE = POSTS_BASE / "Done"


def _ensure_folders():
    """Create all workflow folders if they don't exist."""
    for folder in [FOLDER_PLANS, FOLDER_PENDING, FOLDER_APPROVED, FOLDER_DONE]:
        folder.mkdir(parents=True, exist_ok=True)


def _generate_post_id() -> str:
    """Generate unique post ID based on timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"post_{timestamp}"


def _find_post(post_id: str) -> tuple:
    """
    Find a post file and return its path and data.
    
    Args:
        post_id: Post identifier
    
    Returns:
        Tuple of (file_path, post_data) or (None, None) if not found
    """
    for folder in [FOLDER_PLANS, FOLDER_PENDING, FOLDER_APPROVED, FOLDER_DONE]:
        file_path = folder / f"{post_id}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return file_path, data
    return None, None


def _move_post(file_path: Path, to_folder: Path, post_data: dict) -> bool:
    """
    Move post file to a different folder.
    
    Args:
        file_path: Current file path
        to_folder: Destination folder
        post_data: Post data to save
    
    Returns:
        True if successful
    """
    new_path = to_folder / file_path.name
    
    with open(new_path, "w", encoding="utf-8") as f:
        json.dump(post_data, f, indent=2)
    
    file_path.unlink()
    return True


def draft_post(content: str, title: str = None, tags: list = None) -> str:
    """
    Create a new LinkedIn post draft.
    
    Saves the draft to the Plans folder with metadata.
    
    Args:
        content: Post text content
        title: Optional title for the post (auto-generated if not provided)
        tags: Optional list of tags for categorization
    
    Returns:
        Human-readable message with post ID and location
    
    Example:
        >>> draft_post("Excited to announce our new feature!", tags=["product", "launch"])
        'Draft created: post_20260307143022 in Plans folder'
    """
    _ensure_folders()
    
    post_id = _generate_post_id()
    
    post_data = {
        "id": post_id,
        "title": title or content[:50] + ("..." if len(content) > 50 else ""),
        "content": content,
        "tags": tags or [],
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "approved_at": None,
        "published_at": None,
        "published_url": None
    }
    
    file_path = FOLDER_PLANS / f"{post_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(post_data, f, indent=2)
    
    return f"Draft created: {post_id} in Plans folder"


def list_posts(status: str = None) -> str:
    """
    List all posts or filter by status/folder.
    
    Args:
        status: Filter by folder: "plans", "pending", "approved", "done"
                If None, lists all posts
    
    Returns:
        Human-readable list of posts
    
    Example:
        >>> list_posts("pending")
        'Pending Approval posts:\\n1. post_001 - Title...'
    """
    _ensure_folders()
    
    folders = {
        "plans": FOLDER_PLANS,
        "pending": FOLDER_PENDING,
        "approved": FOLDER_APPROVED,
        "done": FOLDER_DONE
    }
    
    if status and status.lower() not in folders:
        return f"Invalid status. Choose from: {', '.join(folders.keys())}"
    
    results = []
    
    if status:
        folder = folders[status.lower()]
        folder_name = folder.name
        files = sorted(folder.glob("*.json"))
        
        if not files:
            return f"No posts in {folder_name}"
        
        results.append(f"{folder_name} posts:")
        for i, file_path in enumerate(files, 1):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            results.append(f"{i}. {data['id']} - {data['title']}")
    else:
        for folder_name, folder in folders.items():
            files = list(folder.glob("*.json"))
            if files:
                results.append(f"\n{folder_name}:")
                for file_path in sorted(files):
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    results.append(f"  - {data['id']}: {data['title']}")
    
    if not results:
        return "No posts found"
    
    return "\n".join(results)


def approve_post(post_id: str) -> str:
    """
    Approve a post for publishing.
    
    Moves the post from Pending_Approval folder to Approved folder.
    
    Args:
        post_id: Post identifier to approve
    
    Returns:
        Human-readable approval status message
    
    Example:
        >>> approve_post("post_20260307143022")
        'Post post_20260307143022 approved and moved to Approved folder'
    """
    _ensure_folders()
    
    file_path, post_data = _find_post(post_id)
    
    if not file_path:
        return f"Post not found: {post_id}"
    
    # Check current location
    current_folder = file_path.parent.name
    
    if current_folder == FOLDER_APPROVED.name:
        return f"Post {post_id} is already approved"
    
    if current_folder == FOLDER_DONE.name:
        return f"Post {post_id} is already published (in Done folder)"
    
    # Update post data
    post_data["status"] = "approved"
    post_data["approved_at"] = datetime.now().isoformat()
    post_data["updated_at"] = datetime.now().isoformat()
    
    # Move to Approved folder
    _move_post(file_path, FOLDER_APPROVED, post_data)
    
    return f"Post {post_id} approved and moved to Approved folder"


def submit_for_approval(post_id: str) -> str:
    """
    Submit a draft post for approval.
    
    Moves the post from Plans folder to Pending_Approval folder.
    
    Args:
        post_id: Post identifier to submit
    
    Returns:
        Human-readable submission status message
    
    Example:
        >>> submit_for_approval("post_20260307143022")
        'Post post_20260307143022 submitted for approval'
    """
    _ensure_folders()
    
    file_path, post_data = _find_post(post_id)
    
    if not file_path:
        return f"Post not found: {post_id}"
    
    current_folder = file_path.parent.name
    
    if current_folder == FOLDER_PENDING.name:
        return f"Post {post_id} is already pending approval"
    
    if current_folder == FOLDER_APPROVED.name:
        return f"Post {post_id} is already approved"
    
    if current_folder == FOLDER_DONE.name:
        return f"Post {post_id} is already published (in Done folder)"
    
    # Update post data
    post_data["status"] = "pending_approval"
    post_data["updated_at"] = datetime.now().isoformat()
    
    # Move to Pending_Approval folder
    _move_post(file_path, FOLDER_PENDING, post_data)
    
    return f"Post {post_id} submitted for approval"


def publish_post(post_id: str, linkedin_session=None) -> str:
    """
    Publish a post to LinkedIn.
    
    Moves the post from Approved folder to Done folder after publishing.
    
    Args:
        post_id: Post identifier to publish
        linkedin_session: Optional LinkedInSession object for publishing
                         If None, returns post content for manual publishing
    
    Returns:
        Human-readable publish status message
    
    Example:
        >>> publish_post("post_20260307143022")
        'Post post_20260307143022 published to LinkedIn'
    """
    _ensure_folders()
    
    file_path, post_data = _find_post(post_id)
    
    if not file_path:
        return f"Post not found: {post_id}"
    
    current_folder = file_path.parent.name
    
    if current_folder == FOLDER_DONE.name:
        return f"Post {post_id} is already published"
    
    if current_folder == FOLDER_PLANS.name:
        return f"Post {post_id} must be approved first (currently in Plans)"
    
    if current_folder == FOLDER_PENDING.name:
        return f"Post {post_id} is still pending approval"
    
    # If no LinkedIn session, just mark as ready and move to Done
    if linkedin_session is None:
        post_data["status"] = "published"
        post_data["published_at"] = datetime.now().isoformat()
        post_data["published_url"] = "Pending manual publish"
        post_data["updated_at"] = datetime.now().isoformat()
        
        _move_post(file_path, FOLDER_DONE, post_data)
        
        return f"Post {post_id} moved to Done folder (ready for publishing)"
    
    # Publish via LinkedIn session
    try:
        from tools.linkedin_tool import LinkedInSession
        
        if not linkedin_session.logged_in:
            return f"LinkedIn session not authenticated"
        
        # Use the publish_post function from LinkedInSession
        result = linkedin_session.publish_post(post_data)
        
        if result.get("success"):
            post_data["status"] = "published"
            post_data["published_at"] = datetime.now().isoformat()
            post_data["published_url"] = result.get("url", "Published")
            post_data["updated_at"] = datetime.now().isoformat()
            
            _move_post(file_path, FOLDER_DONE, post_data)
            
            return f"Post {post_id} published to LinkedIn: {result.get('url', 'Success')}"
        else:
            return f"Failed to publish: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"Publish error: {str(e)}"


def get_post(post_id: str) -> str:
    """
    Get full post details.
    
    Args:
        post_id: Post identifier
    
    Returns:
        Human-readable post details
    """
    file_path, post_data = _find_post(post_id)
    
    if not post_data:
        return f"Post not found: {post_id}"
    
    folder = file_path.parent.name
    
    lines = [
        f"Post: {post_data['id']}",
        f"Title: {post_data['title']}",
        f"Status: {post_data['status']} ({folder})",
        f"Created: {post_data['created_at']}",
        f"Tags: {', '.join(post_data['tags']) if post_data['tags'] else 'None'}",
        "",
        "Content:",
        "-" * 40,
        post_data['content']
    ]
    
    if post_data.get('approved_at'):
        lines.append(f"Approved: {post_data['approved_at']}")
    if post_data.get('published_at'):
        lines.append(f"Published: {post_data['published_at']}")
    if post_data.get('published_url'):
        lines.append(f"URL: {post_data['published_url']}")
    
    return "\n".join(lines)


def delete_post(post_id: str) -> str:
    """
    Delete a post permanently.
    
    Args:
        post_id: Post identifier to delete
    
    Returns:
        Human-readable deletion status
    """
    file_path, post_data = _find_post(post_id)
    
    if not file_path:
        return f"Post not found: {post_id}"
    
    file_path.unlink()
    return f"Post {post_id} deleted"
