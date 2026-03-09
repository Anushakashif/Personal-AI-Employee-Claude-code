"""
Task Management Tool for AI Employee Vault

Provides task management with workflow-based folder system:
- create_task(task_name) - Create new task in Inbox
- move_task(task_name, destination_folder) - Move task between folders
- list_tasks(folder) - List tasks in a specific folder

Task Workflow Folders:
    Inbox → Needs_Action → Pending_Approval → Approved → Done
                                         ↓
                                      Rejected

Folder Descriptions:
    - Inbox: New tasks that need to be reviewed
    - Needs_Action: Tasks requiring active work or attention
    - Pending_Approval: Tasks waiting for approval/review
    - Approved: Tasks that have been approved for execution
    - Done: Completed tasks
    - Rejected: Tasks that were rejected/cancelled

Usage:
    from tools.task_tool import create_task, move_task, list_tasks
    
    # Create a new task
    create_task("Review Q1 report")
    
    # Move task through workflow
    move_task("Review Q1 report", "Needs_Action")
    move_task("Review Q1 report", "Done")
    
    # List tasks in a folder
    list_tasks("Inbox")
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Base directory for task folders (project root)
BASE_DIR = Path(__file__).parent.parent
TASKS_BASE = BASE_DIR / "tasks"

# Workflow folders - defines the task lifecycle
FOLDER_INBOX = TASKS_BASE / "Inbox"
FOLDER_NEEDS_ACTION = TASKS_BASE / "Needs_Action"
FOLDER_PENDING_APPROVAL = TASKS_BASE / "Pending_Approval"
FOLDER_APPROVED = TASKS_BASE / "Approved"
FOLDER_DONE = TASKS_BASE / "Done"
FOLDER_REJECTED = TASKS_BASE / "Rejected"

# Map folder names to paths for easy lookup
FOLDERS = {
    "Inbox": FOLDER_INBOX,
    "Needs_Action": FOLDER_NEEDS_ACTION,
    "Pending_Approval": FOLDER_PENDING_APPROVAL,
    "Approved": FOLDER_APPROVED,
    "Done": FOLDER_DONE,
    "Rejected": FOLDER_REJECTED
}

# Valid workflow transitions
# A task can move from any folder to any other folder for flexibility
VALID_FOLDERS = list(FOLDERS.keys())


def _ensure_folders():
    """Create all workflow folders if they don't exist."""
    for folder in FOLDERS.values():
        folder.mkdir(parents=True, exist_ok=True)


def _generate_task_id() -> str:
    """Generate unique task ID based on timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"task_{timestamp}"


def _sanitize_task_name(name: str) -> str:
    """
    Sanitize task name for use as filename.
    
    Removes or replaces characters that are invalid in filenames.
    """
    # Replace problematic characters with underscores
    sanitized = name.replace("/", "_").replace("\\", "_")
    sanitized = sanitized.replace(":", "_").replace("*", "_")
    sanitized = sanitized.replace("?", "_").replace('"', "_")
    sanitized = sanitized.replace("<", "_").replace(">", "_").replace("|", "_")
    return sanitized.strip()


def _find_task(task_name: str) -> tuple:
    """
    Find a task file and return its path and data.
    
    Searches all workflow folders for the task.
    
    Args:
        task_name: Task name (or partial name for matching)
    
    Returns:
        Tuple of (file_path, task_data) or (None, None) if not found
    """
    for folder in FOLDERS.values():
        # Try exact match first
        file_path = folder / f"{task_name}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return file_path, data
        
        # Try partial match (case-insensitive)
        for json_file in folder.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if task_name.lower() in data.get("name", "").lower():
                return json_file, data
    
    return None, None


def _get_task_folder(file_path: Path) -> str:
    """Get the folder name for a task file path."""
    return file_path.parent.name


def _move_task_file(file_path: Path, to_folder: Path, task_data: dict) -> bool:
    """
    Move task file to a different folder.
    
    Args:
        file_path: Current file path
        to_folder: Destination folder
        task_data: Task data to save
    
    Returns:
        True if successful
    """
    new_path = to_folder / file_path.name
    
    with open(new_path, "w", encoding="utf-8") as f:
        json.dump(task_data, f, indent=2)
    
    file_path.unlink()
    return True


def create_task(task_name: str, description: str = None, priority: str = "medium", tags: list = None) -> str:
    """
    Create a new task in the Inbox folder.
    
    New tasks always start in the Inbox for initial review.
    
    Args:
        task_name: Name/title of the task
        description: Optional detailed description
        priority: Task priority - "low", "medium", or "high" (default: medium)
        tags: Optional list of tags for categorization
    
    Returns:
        Human-readable creation message with task ID
    
    Example:
        >>> create_task("Review Q1 financial report", priority="high", tags=["finance", "urgent"])
        'Task created: Review Q1 financial report (task_20260307143022) in Inbox'
    """
    _ensure_folders()
    
    task_id = _generate_task_id()
    safe_name = _sanitize_task_name(task_name)
    
    task_data = {
        "id": task_id,
        "name": task_name,
        "description": description or "",
        "priority": priority,
        "tags": tags or [],
        "status": "inbox",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "moved_at": None,
        "completed_at": None,
        "history": [
            {
                "action": "created",
                "folder": "Inbox",
                "timestamp": datetime.now().isoformat()
            }
        ]
    }
    
    file_path = FOLDER_INBOX / f"{safe_name}.json"
    
    # Handle duplicate names
    counter = 1
    original_safe_name = safe_name
    while file_path.exists():
        safe_name = f"{original_safe_name}_{counter}"
        file_path = FOLDER_INBOX / f"{safe_name}.json"
        counter += 1
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(task_data, f, indent=2)
    
    return f"Task created: {task_name} ({task_id}) in Inbox"


def move_task(task_name: str, destination_folder: str) -> str:
    """
    Move a task to a different workflow folder.
    
    Tasks can move between any folders for flexibility.
    The task's history is updated to track the movement.
    
    Args:
        task_name: Task name (or partial name for matching)
        destination_folder: Target folder name. Valid options:
                           - Inbox
                           - Needs_Action
                           - Pending_Approval
                           - Approved
                           - Done
                           - Rejected
    
    Returns:
        Human-readable move status message
    
    Example:
        >>> move_task("Review Q1 report", "Needs_Action")
        'Task "Review Q1 report" moved from Inbox to Needs_Action'
    """
    _ensure_folders()
    
    # Validate destination folder
    if destination_folder not in VALID_FOLDERS:
        return f"Invalid folder: {destination_folder}. Valid options: {', '.join(VALID_FOLDERS)}"
    
    # Find the task
    file_path, task_data = _find_task(task_name)
    
    if not file_path:
        return f"Task not found: {task_name}"
    
    # Get current folder
    current_folder = _get_task_folder(file_path)
    
    # Check if already in destination
    if current_folder == destination_folder:
        return f"Task \"{task_data['name']}\" is already in {destination_folder}"
    
    # Update task data
    task_data["status"] = destination_folder.lower()
    task_data["updated_at"] = datetime.now().isoformat()
    task_data["moved_at"] = datetime.now().isoformat()
    
    if destination_folder == "Done":
        task_data["completed_at"] = datetime.now().isoformat()
    
    # Add to history
    task_data["history"].append({
        "action": "moved",
        "from": current_folder,
        "to": destination_folder,
        "timestamp": datetime.now().isoformat()
    })
    
    # Move the file
    dest_path = FOLDERS[destination_folder]
    _move_task_file(file_path, dest_path, task_data)
    
    return f"Task \"{task_data['name']}\" moved from {current_folder} to {destination_folder}"


def list_tasks(folder: str = None) -> str:
    """
    List tasks in a specific folder or all folders.
    
    Args:
        folder: Folder name to list tasks from. Options:
                - Inbox
                - Needs_Action
                - Pending_Approval
                - Approved
                - Done
                - Rejected
                - None (lists all folders)
    
    Returns:
        Human-readable list of tasks with their details
    
    Example:
        >>> list_tasks("Inbox")
        'Inbox tasks (2):
        1. [HIGH] Review Q1 report - Created: 2026-03-07
        2. [MEDIUM] Update documentation - Created: 2026-03-06'
        
        >>> list_tasks()
        'Inbox (2):
          - Review Q1 report
          - Update documentation
        Needs_Action (1):
          - Fix bug #123
        Done (5):
          - ...'
    """
    _ensure_folders()
    
    if folder:
        # List specific folder
        if folder not in VALID_FOLDERS:
            return f"Invalid folder: {folder}. Valid options: {', '.join(VALID_FOLDERS)}"
        
        folder_path = FOLDERS[folder]
        task_files = sorted(folder_path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not task_files:
            return f"No tasks in {folder}"
        
        lines = [f"{folder} tasks ({len(task_files)}):"]
        
        for i, file_path in enumerate(task_files, 1):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            priority_marker = f"[{data.get('priority', 'medium').upper()}]"
            created_date = data.get("created_at", "")[:10]
            tags_str = f" ({', '.join(data.get('tags', []))})" if data.get("tags") else ""
            
            lines.append(f"{i}. {priority_marker} {data['name']}{tags_str} - Created: {created_date}")
        
        return "\n".join(lines)
    
    else:
        # List all folders
        results = []
        
        for folder_name in VALID_FOLDERS:
            folder_path = FOLDERS[folder_name]
            task_files = list(folder_path.glob("*.json"))
            
            if task_files:
                results.append(f"\n{folder_name} ({len(task_files)}):")
                for file_path in sorted(task_files):
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    results.append(f"  - {data['name']}")
        
        if not results:
            return "No tasks found in any folder"
        
        return "\n".join(results)


def get_task(task_name: str) -> str:
    """
    Get full details of a specific task.
    
    Args:
        task_name: Task name (or partial name for matching)
    
    Returns:
        Human-readable task details including history
    
    Example:
        >>> get_task("Review Q1 report")
        'Task: Review Q1 report
        ID: task_20260307143022
        Status: Needs_Action
        Priority: HIGH
        Created: 2026-03-07 14:30:22
        ...'
    """
    file_path, task_data = _find_task(task_name)
    
    if not task_data:
        return f"Task not found: {task_name}"
    
    current_folder = _get_task_folder(file_path)
    
    lines = [
        f"Task: {task_data['name']}",
        f"ID: {task_data['id']}",
        f"Status: {task_data['status']} ({current_folder})",
        f"Priority: {task_data.get('priority', 'medium').upper()}",
        f"Created: {task_data['created_at']}",
        f"Last Updated: {task_data['updated_at']}",
        f"Tags: {', '.join(task_data.get('tags', [])) if task_data.get('tags') else 'None'}",
        "",
        "Description:",
        "-" * 40,
        task_data.get('description', 'No description')
    ]
    
    if task_data.get('completed_at'):
        lines.append(f"Completed: {task_data['completed_at']}")
    
    # Add movement history
    if task_data.get('history') and len(task_data['history']) > 1:
        lines.append("")
        lines.append("History:")
        for event in task_data['history']:
            if event['action'] == 'created':
                lines.append(f"  - Created in {event['folder']} ({event['timestamp'][:19]})")
            elif event['action'] == 'moved':
                lines.append(f"  - Moved: {event['from']} → {event['to']} ({event['timestamp'][:19]})")
    
    return "\n".join(lines)


def delete_task(task_name: str) -> str:
    """
    Delete a task permanently.
    
    Use with caution - this cannot be undone.
    
    Args:
        task_name: Task name to delete
    
    Returns:
        Human-readable deletion status
    
    Example:
        >>> delete_task("Old task")
        'Task "Old task" deleted'
    """
    file_path, task_data = _find_task(task_name)
    
    if not file_path:
        return f"Task not found: {task_name}"
    
    task_name_display = task_data.get('name', task_name)
    file_path.unlink()
    
    return f"Task \"{task_name_display}\" deleted"


def get_summary() -> str:
    """
    Get summary statistics of all tasks.
    
    Returns:
        Human-readable summary with counts per folder
    
    Example:
        >>> get_summary()
        'Task Summary:
        Total: 15
        Inbox: 3
        Needs_Action: 4
        Pending_Approval: 2
        Approved: 1
        Done: 4
        Rejected: 1'
    """
    _ensure_folders()
    
    counts = {}
    total = 0
    
    for folder_name, folder_path in FOLDERS.items():
        count = len(list(folder_path.glob("*.json")))
        counts[folder_name] = count
        total += count
    
    lines = [
        "Task Summary:",
        f"Total: {total}",
        ""
    ]
    
    for folder_name in VALID_FOLDERS:
        lines.append(f"  {folder_name}: {counts[folder_name]}")
    
    return "\n".join(lines)
