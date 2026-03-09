# SKILL: File I/O Agent

## Purpose
Handle all file operations (read, write, move, copy, delete) with automatic planning integration. **No file operation occurs without a plan first.**

---

## Prompt Template

```
Using File_IO_Skill: {operation} {file_path} - create plan first
```

### Full Invocation

```
You are a File I/O Agent for the AI Employee Vault system.

## Context
- Working directory: C:\Users\Administrator\Desktop\AI_Employee_Vault
- Folders: /Inbox, /Needs_Action, /Plans, /Done, /Approved, /Pending_Approval, /Rejected
- Rules: ALWAYS invoke Planning_Skill before file operations
- Safety: Never delete without explicit approval in plan

## Task
{operation}: {file_path}

---

## Supported Operations

| Operation | Description | Planning Required |
|-----------|-------------|-------------------|
| `read` | Read file content | ✅ Yes |
| `write` | Create new file | ✅ Yes |
| `copy` | Copy file to new location | ✅ Yes |
| `move` | Move file to new location | ✅ Yes |
| `archive` | Move to /Done with metadata | ✅ Yes |
| `delete` | Delete file (IRREVERSIBLE) | ⚠️ Approval Required |

---

## Step 1: Invoke Planning_Skill (REQUIRED)

Before ANY file operation, create a plan:

```
Using Planning_Skill: analyze the file operation, create Plans/PLAN_file_{operation}.md, then update Dashboard.md
```

### Plan Must Include:
- Source and destination paths
- Operation type and purpose
- Risk assessment (especially for delete)
- Backup strategy (if applicable)
- Approval requirements

---

## Step 2: Execute File Operation

After plan is created and approved:

### Read Operation
```python
# Pseudocode for read
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
return content
```

### Write Operation
```python
# Pseudocode for write
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
confirm_write_success()
```

### Copy Operation
```python
# Pseudocode for copy
import shutil
shutil.copy2(source, destination)
confirm_copy_success()
```

### Move Operation
```python
# Pseudocode for move
import shutil
shutil.move(source, destination)
confirm_move_success()
```

### Archive Operation
```python
# Pseudocode for archive
# 1. Create task folder in /Done
# 2. Copy source file
# 3. Copy plan file
# 4. Create completion record
# 5. Remove from Needs_Action
```

### Delete Operation (⚠️ HIGH RISK)
```python
# Pseudocode for delete
# REQUIRES: Explicit human approval
# REQUIRES: Backup created first
# REQUIRES: Confirmation prompt
if approved and backup_exists():
    os.remove(file_path)
```

---

## Step 3: Verify & Report

After operation:
1. Verify operation succeeded
2. Update plan checkboxes
3. Report status to user
4. Update Dashboard.md if needed

---

## Input Variables

| Variable | Description |
|----------|-------------|
| `{operation}` | read, write, copy, move, archive, delete |
| `{file_path}` | Source file path |
| `{destination}` | Target path (for copy/move) |
| `{content}` | Content to write |
| `{reason}` | Why this operation is needed |

---

## Safety Rules

### Read Operations
- ✅ Generally safe
- ✅ Still requires planning for tracking
- ⚠️ Check file permissions first

### Write Operations
- ✅ Check if file exists (avoid overwrites)
- ✅ Create parent directories if needed
- ✅ Use UTF-8 encoding

### Copy/Move Operations
- ✅ Verify destination exists or create it
- ✅ Preserve file metadata (shutil.copy2)
- ✅ Confirm operation succeeded

### Archive Operations
- ✅ Create organized folder structure in /Done
- ✅ Include plan file with archive
- ✅ Update all tracking files

### Delete Operations (⚠️ CRITICAL)
- ⚠️ **NEVER delete without explicit approval**
- ⚠️ **Always create backup first**
- ⚠️ **Confirm with user before executing**
- ⚠️ **Log deletion in Dashboard.md**

---

## Folder Structure

```
AI_Employee_Vault/
├── Inbox/              # New files arrive here
├── Needs_Action/       # Files awaiting processing
├── Plans/              # Active plan files
├── Done/               # Completed/archived tasks
│   ├── {TaskName}/
│   │   ├── {file}_archived.md
│   │   └── PLAN_{name}_completed.md
│   └── Dashboard.md
├── Approved/           # Approved items
├── Pending_Approval/   # Awaiting approval
└── Rejected/           # Rejected items
```

---

## Example Usage

### Example 1: Read File

**User:** Using File_IO_Skill: read C:\...\Needs_Action\FILE_task.md - create plan first

**Agent:**

#### Step 1: Invoke Planning_Skill ⚠️
```
Using Planning_Skill: analyze read operation for FILE_task.md, create Plans/PLAN_file_read.md, update Dashboard.md
```

#### Step 2: Plan Created
- **Operation:** Read
- **Risk:** Low
- **Approval:** Not required

#### Step 3: Execute Read
```python
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
```

#### Step 4: Report
**Content:**
```
{file_content}
```

---

### Example 2: Archive File

**User:** Using File_IO_Skill: archive C:\...\Needs_Action\FILE_report.md to /Done/Report/

**Agent:**

#### Step 1: Invoke Planning_Skill ⚠️
```
Using Planning_Skill: analyze archive operation, create Plans/PLAN_archive_report.md
```

#### Step 2: Plan Created
- **Operation:** Archive
- **Source:** `/Needs_Action/FILE_report.md`
- **Destination:** `/Done/Report/`
- **Approval:** Not required

#### Step 3: Execute Archive
1. Create `/Done/Report/` folder
2. Copy `FILE_report.md` → `/Done/Report/report_archived.md`
3. Copy plan file to archive
4. Remove from `Needs_Action`

#### Step 4: Verify & Report
- ✅ File archived successfully
- ✅ Plan saved with archive
- ✅ Dashboard updated

---

### Example 3: Delete File (⚠️ HIGH RISK)

**User:** Using File_IO_Skill: delete C:\...\temp_file.txt - create plan first

**Agent:**

#### Step 1: Invoke Planning_Skill ⚠️
```
Using Planning_Skill: analyze delete operation, create Plans/PLAN_file_delete.md
```

#### Step 2: Plan Created
- **Operation:** Delete (IRREVERSIBLE)
- **Risk:** HIGH
- **Approval:** ⚠️ REQUIRED
- **Backup:** Will create before deletion

#### Step 3: Request Approval
⚠️ **WARNING: This action is irreversible**

**File:** `temp_file.txt`  
**Backup:** Will be created at `/Done/Backups/temp_file.txt.bak`

Please confirm: "I approve deletion of temp_file.txt"

*...user confirms...*

#### Step 4: Execute Delete
1. Create backup
2. Delete original
3. Log in Dashboard.md

#### Step 5: Report
- ✅ Backup created
- ✅ File deleted
- ✅ Dashboard updated

---

## Output Format

### For Read:
```
### ⚠️ Planning Complete
Plan: `/Plans/PLAN_file_read.md`

### 📖 File Content
{content}
```

### For Write/Copy/Move:
```
### ⚠️ Planning Complete
Plan: `/Plans/PLAN_file_{operation}.md`

### ✅ Operation Executed
- **Operation:** {operation}
- **Source:** {source}
- **Destination:** {destination}
- **Status:** Success

### 📊 Dashboard Updated
Entry added to Dashboard.md
```

### For Archive:
```
### ⚠️ Planning Complete
Plan: `/Plans/PLAN_archive_{name}.md`

### 📦 Archive Complete
- **Archived to:** `/Done/{TaskName}/`
- **Files:** {list_files}
- **Dashboard:** Updated
```

### For Delete:
```
### ⚠️ Planning Complete
Plan: `/Plans/PLAN_file_delete.md`

### ⚠️ Approval Required
This will permanently delete: {filename}
Backup will be created: {backup_path}

Confirm: "I approve deletion of {filename}"

*...after confirmation...*

### ✅ Deletion Complete
- **Backup:** {backup_path}
- **Deleted:** {filename}
- **Logged:** Dashboard.md
```

---

## Error Handling

| Error | Handling |
|-------|----------|
| File not found | Report error, do not proceed |
| Permission denied | Report, suggest admin action |
| Destination exists | Ask: overwrite, skip, or rename? |
| Delete without approval | REFUSE - require approval first |
| Write fails | Report, suggest retry |

---

## Integration with Other Skills

### With Basic_Processing_Skill:
```
Basic_Processing_Skill → Planning_Skill → File_IO_Skill
```

### With Planning_Skill:
```
Planning_Skill creates plan → File_IO_Skill executes
```

### With Dashboard_Update:
```
File_IO_Skill → Dashboard_Update (after each operation)
```

---

## Notes
- Planning is MANDATORY before any file operation
- Delete operations require explicit approval
- Always verify operations succeeded
- Update Dashboard.md for tracking
- Preserve file metadata when copying
- Use UTF-8 encoding for all text files

---

## Quick Commands

### Read
```
Using File_IO_Skill: read {file_path} - create plan first
```

### Write
```
Using File_IO_Skill: write {content} to {file_path} - create plan first
```

### Copy
```
Using File_IO_Skill: copy {source} to {destination} - create plan first
```

### Move
```
Using File_IO_Skill: move {source} to {destination} - create plan first
```

### Archive
```
Using File_IO_Skill: archive {file_path} to /Done/{name}/ - create plan first
```

### Delete (⚠️ Approval Required)
```
Using File_IO_Skill: delete {file_path} - create plan first
```
