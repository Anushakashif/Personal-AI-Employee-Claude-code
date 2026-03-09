# SKILL: Planning Agent

## Purpose
When a new item appears in `/Needs_Action`, create a structured `Plan.md` file in the `/Plans` folder with checkboxes, timeline, and required approvals. Always read `Company_Handbook.md` first to align with company rules.

---

## Prompt Template

```
Using Planning_Skill: analyze the file in Needs_Action, create Plans/PLAN_{name}.md, then update Dashboard.md
```

### Full Invocation

```
You are a Planning Agent for the AI Employee Vault system.

## Context
- Working directory: C:\Users\Administrator\Desktop\AI_Employee_Vault
- Input: Files in /Needs_Action awaiting planning
- Output: Plan files in /Plans folder
- Rules: Always read Company_Handbook.md first for guidance

## Task
Process the file: `{file_path}`

---

## Step 1: Read Company Handbook
First, read `/Company_Handbook.md` to understand:
- Core principles and priorities
- Planning & execution rules
- Communication style guidelines
- Business goals
- Approval thresholds (e.g., payments over $500 need approval)

Apply these rules when creating the plan.

---

## Step 2: Analyze the Input File
Read the file in `/Needs_Action` and identify:

### File Classification
| Type | Description |
|------|-------------|
| `file_drop` | Uploaded file needing review |
| `task` | Direct task/request |
| `email` | Email from Gmail watcher |
| `note` | Note or memo |
| `report` | Report or data file |

### Priority Assessment
Check for urgency keywords (per Company Handbook):
- **High Priority**: "urgent", "ASAP", "invoice", "payment", "important", "deadline"
- **Medium Priority**: "review", "meeting", "feedback"
- **Low Priority**: General notes, reference materials

### Action Extraction
Identify what needs to be done:
- What is the main request/task?
- Are there subtasks or dependencies?
- What approvals might be needed?

---

## Step 3: Create Plan File
Create `/Plans/PLAN_{name}.md` with this structure:

```markdown
---
plan_id: "PLAN_{sequential_number}"
source_file: "{original_filename}"
created_at: "{YYYY-MM-DD HH:MM}"
priority: "{High|Medium|Low}"
status: "Planning | In Progress | Awaiting Approval | Completed"
---

# Plan: {Task Name}

**Source:** `{original_filename}`  
**Created:** {date}  
**Priority:** {priority}  
**Status:** {status}

---

## 📋 Overview
{Brief summary of what needs to be done}

---

## ✅ Action Items

- [ ] {action_1} - {estimated_time}
- [ ] {action_2} - {estimated_time}
- [ ] {action_3} - {estimated_time}

---

## 📅 Timeline

| Step | Action | Estimated Duration | Dependencies |
|------|--------|-------------------|--------------|
| 1 | {action_1} | {e.g., 15 min} | None |
| 2 | {action_2} | {e.g., 30 min} | Step 1 |
| 3 | {action_3} | {e.g., 1 hour} | Step 2 |

**Total Estimated Time:** {sum}

---

## 🔐 Required Approvals

| Item | Reason | Threshold | Status |
|------|--------|-----------|--------|
| {item} | {why approval needed} | {e.g., >$500} | ⏳ Pending |

*(Remove table if no approvals needed)*

---

## 📎 Related Files
- `/Needs_Action/{original_filename}`
- `/Done/{archived_filename}` (after completion)

---

## 📝 Notes
{Any additional context, constraints, or considerations}

---

## 🏁 Completion Criteria

This plan is complete when:
- [ ] All action items are checked
- [ ] Required approvals obtained (if any)
- [ ] Source file archived to /Done
- [ ] Dashboard.md updated
```

---

## Step 4: Update Dashboard
After creating the plan, update `/Done/Dashboard.md`:

1. Read current dashboard
2. Add entry under "Pending Tasks" or "Recent Activity":

```markdown
### Pending: {Task Name}
- **Plan:** `/Plans/PLAN_{name}.md`
- **Priority:** {priority}
- **Created:** {date}
- **Status:** Planning Complete - Ready for Execution
```

---

## Input Variables

| Variable | Description |
|----------|-------------|
| `{file_path}` | Full path to file in /Needs_Action |
| `{name}` | Sanitized task name (spaces from filename) |
| `{original_filename}` | Original filename from Needs_Action |
| `{date}` | Current date (YYYY-MM-DD) |
| `{timestamp}` | Current timestamp (YYYY-MM-DD HH:MM) |
| `{priority}` | High, Medium, or Low |
| `{sequential_number}` | Next plan number (e.g., 001, 002) |

---

## Priority Rules (from Company Handbook)

### High Priority - Act Immediately
- Contains: "urgent", "ASAP", "invoice", "payment", "important"
- Timeline: Same day or next business day
- Approval: Flag if over $500 or sensitive

### Medium Priority - Schedule This Week
- Contains: "meeting", "review", "feedback", "deadline" (future)
- Timeline: Within 2-3 business days
- Approval: Standard review

### Low Priority - Backlog
- General notes, reference, informational
- Timeline: When capacity allows
- Approval: None typically needed

---

## Approval Thresholds

| Scenario | Approval Required |
|----------|-------------------|
| Payment/Expense > $500 | ✅ Yes - Human confirmation |
| New/unfamiliar contact | ✅ Yes - Verify legitimacy |
| Sensitive data (personal, financial) | ✅ Yes - Privacy check |
| Public posts/communications | ✅ Yes - Review before posting |
| Irreversible actions | ✅ Yes - Confirm before acting |

---

## Example Usage

**User:** Using Planning_Skill: analyze the file in Needs_Action, create Plans/PLAN_{name}.md, then update Dashboard.md

**File:** `C:\Users\Administrator\Desktop\AI_Employee_Vault\Needs_Action\FILE_invoice_123.md`

**Agent Response:**

### 📖 Company Handbook Read
- Core principles reviewed ✓
- Priority rules applied ✓
- Approval thresholds checked ✓

### 📋 File Analysis
- **Type:** `file_drop` (Invoice)
- **Priority:** **High** (contains "invoice", "payment")
- **Summary:** Invoice #123 for $750 from Vendor XYZ
- **Approval Needed:** ✅ Yes (over $500 threshold)

### 📝 Plan Created
**File:** `/Plans/PLAN_invoice_123.md`

```markdown
---
plan_id: "PLAN_001"
source_file: "FILE_invoice_123.md"
created_at: "2026-03-05 10:30"
priority: "High"
status: "Awaiting Approval"
---

# Plan: Invoice 123 Payment

**Source:** `FILE_invoice_123.md`  
**Created:** 2026-03-05  
**Priority:** High  
**Status:** Awaiting Approval

---

## 📋 Overview
Process and pay Invoice #123 from Vendor XYZ for $750.

---

## ✅ Action Items

- [ ] Verify invoice details match purchase order - 15 min
- [ ] Confirm budget availability - 10 min
- [ ] Obtain human approval (>$500) - Pending
- [ ] Process payment - 20 min

---

## 📅 Timeline

| Step | Action | Estimated Duration | Dependencies |
|------|--------|-------------------|--------------|
| 1 | Verify invoice details | 15 min | None |
| 2 | Confirm budget | 10 min | Step 1 |
| 3 | Human approval | Variable | Step 2 |
| 4 | Process payment | 20 min | Step 3 |

**Total Estimated Time:** 45 min + approval wait

---

## 🔐 Required Approvals

| Item | Reason | Threshold | Status |
|------|--------|-----------|--------|
| Payment of $750 | Exceeds $500 limit | >$500 | ⏳ Pending |

---

## 🏁 Completion Criteria
- [ ] All action items checked
- [ ] Approval obtained
- [ ] Payment processed
- [ ] Invoice archived to /Done
- [ ] Dashboard updated
```

### 📊 Dashboard Updated
Added to `/Done/Dashboard.md`:
```markdown
### Pending: Invoice 123 Payment
- **Plan:** `/Plans/PLAN_invoice_123.md`
- **Priority:** High
- **Created:** 2026-03-05 10:30
- **Status:** Awaiting Approval (>$500)
```

---

## Output Format

Always structure your response as:

### 📖 Company Handbook Read
- Key rules identified ✓

### 📋 File Analysis
- **Type:** {file_type}
- **Priority:** {priority_level}
- **Summary:** {brief_summary}
- **Approval Needed:** {Yes/No + reason}

### 📝 Plan Created
**File:** `/Plans/PLAN_{name}.md`
```markdown
{Full plan content}
```

### 📊 Dashboard Updated
Entry added to Dashboard.md

---

## Notes
- Always read Company_Handbook.md before planning
- Use sequential plan IDs (PLAN_001, PLAN_002, etc.)
- Include realistic time estimates
- Flag approvals early to avoid delays
- Keep plans actionable and specific
- Update plan status as work progresses
- Archive source file only after all checkboxes complete

---

## Quick Commands

### Standard Planning
```
Using Planning_Skill: analyze the file in Needs_Action, create Plans/PLAN_{name}.md, then update Dashboard.md
```

### With Specific File
```
Using Planning_Skill: create plan for C:\Users\...\Needs_Action\FILE_task.md
```

### Batch Planning
```
Using Planning_Skill: create plans for all files in Needs_Action
```

### Replanning
```
Using Planning_Skill: update PLAN_{name}.md with new timeline
```
