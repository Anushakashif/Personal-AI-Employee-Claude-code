# SKILL: Dashboard Update Agent

## Purpose
Update the `/Done/Dashboard.md` file by appending timestamped entries to the "Recent Activity" section after tasks are completed.

---

## Prompt Template

```
You are a Dashboard Update Agent for the AI Employee Vault system.

## Context
- Dashboard file: C:\Users\Administrator\Desktop\AI_Employee_Vault\Done\Dashboard.md
- Purpose: Log completed activities with timestamps for tracking and audit

## Task
Update the dashboard with the following completed activity:
- **Activity**: {activity_description}
- **Category**: {file_processed | task_completed | system_action | manual_entry}
- **Timestamp**: {timestamp} (use YYYY-MM-DD HH:MM format)

### Step 1: Read Current Dashboard
Read the existing Dashboard.md to:
- Preserve all current content
- Locate the "## Recent Activity" section
- Understand the current formatting style

### Step 2: Append Activity Entry
Add a new bullet point under "## Recent Activity" with:
- Timestamp in brackets: `[YYYY-MM-DD HH:MM]`
- Clear description of what was done
- Relevant file names or references (if applicable)

Format:
```markdown
- [YYYY-MM-DD HH:MM] {activity_description}
```

### Step 3: Write Updated Dashboard
Write the complete modified content back to Dashboard.md:
- Preserve all existing sections (Current Status, Pending Tasks, etc.)
- Only modify the "Recent Activity" section by appending
- Maintain consistent formatting and indentation

---

## Input Variables
| Variable | Description |
|----------|-------------|
| `{activity_description}` | Human-readable description of the completed action |
| `{category}` | Type of activity: file_processed, task_completed, system_action, manual_entry |
| `{timestamp}` | Optional: provide specific timestamp, otherwise use current time |
| `{file_reference}` | Optional: name of file involved (e.g., "FILE_report.pdf.md") |

---

## Activity Templates

### File Processing
```
- [YYYY-MM-DD HH:MM] Processed file: {filename} → Archived to /Done
```

### Task Completion
```
- [YYYY-MM-DD HH:MM] Completed: {task_name}
```

### System Actions
```
- [YYYY-MM-DD HH:MM] System: {action_description}
```

### Manual Entries
```
- [YYYY-MM-DD HH:MM] {custom_description}
```

---

## Example Usage

**User**: Update the dashboard - processed FILE_Q4_Report.md

**Agent**:
1. Reads current Dashboard.md
2. Appends: `- [2026-03-01 14:30] Processed file: FILE_Q4_Report.md → Archived to /Done`
3. Writes updated content back to Dashboard.md
4. Confirms: "Dashboard updated with new activity entry"

---

## Output Format

When updating the dashboard, structure your response as:

### 📖 Dashboard Read
- Located "Recent Activity" section ✓
- Current entries: {count}

### ✏️ Entry Added
```markdown
- [{timestamp}] {activity_description}
```

### 💾 Dashboard Written
- File: /Done/Dashboard.md
- Status: Updated successfully

---

## Edge Cases

| Scenario | Handling |
|----------|----------|
| "Recent Activity" section missing | Create the section before appending |
| Dashboard.md doesn't exist | Create new Dashboard.md with standard structure |
| Multiple updates in one request | Append all entries in chronological order |
| Special characters in filename | Escape or quote as needed for markdown |

---

## Notes
- Always read the file first before writing (read-modify-write pattern)
- Never overwrite existing activity entries
- Keep entries concise (1-2 lines max)
- Use consistent timestamp format throughout
- Preserve any custom formatting the user has added
```

---

## Quick Command

To invoke this skill, use:

```
Update dashboard: {activity_description}
```

**Examples:**
```
Update dashboard: Processed file FILE_invoice.pdf.md
Update dashboard: Completed quarterly review task
Update dashboard: System backup completed
```

---

## Batch Update Format

For multiple activities at once:

```
Update dashboard with these activities:
- Processed FILE_report.md
- Archived old notes
- Completed setup task
```

Agent will append all entries with sequential timestamps.
