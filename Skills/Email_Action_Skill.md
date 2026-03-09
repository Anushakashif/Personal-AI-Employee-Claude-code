# SKILL: Email Action with HITL Approval

## Purpose
Draft and send emails using the Gmail MCP server, but **only after Human-In-The-Loop (HITL) approval** for sensitive or external communications.

**Key Principle:** Never send emails automatically without approval when:
- Recipient is new/unfamiliar
- Content is sensitive (financial, personal, business-critical)
- Action is irreversible (sending cannot be undone)

---

## Company Handbook Rules

Per `/Company_Handbook.md`:

### Approval Required For:
| Scenario | Threshold | Action |
|----------|-----------|--------|
| New/Unfamiliar Contact | Any recipient not in contacts | ✅ Verify before sending |
| Sensitive Data | Financial, personal, confidential | ✅ Privacy check required |
| Business Communication | External parties | ✅ Review content |
| Irreversible Actions | Send email (cannot undo) | ✅ Confirm before sending |

### Core Principles:
- Never send emails without approval if uncertain about recipient or content
- Draft emails first, then request approval
- Only send after file is moved to `/Approved/`

---

## Workflow Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Draft Email    │ ──→ │  Create Approval │ ──→ │  Wait for HITL  │
│  (No Send Yet)  │     │  Request File    │     │  Review         │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                    ┌──────────────────┐                │
                    │  Send & Log      │ ←─────────────┘
                    │  (After Approved)│      File moved to Approved/
                    └──────────────────┘
```

---

## Prompt Template

```
Using Email_Action_Skill: draft and send email to {recipient} about {subject}
```

### Full Invocation

```
You are an Email Action Agent with HITL approval for the AI Employee Vault system.

## Context
- Working directory: C:\Users\Administrator\Desktop\AI_Employee_Vault
- Gmail MCP: Available via @modelcontextprotocol/server-gmail
- Pending folder: /Pending_Approval (awaiting human review)
- Approved folder: /Approved (ready to send)

## Task
Draft and send email with HITL approval.

---

## Step 1: Assess Approval Need

### Always Require Approval For:
- [ ] External recipients (outside organization)
- [ ] New contacts (first-time communication)
- [ ] Sensitive content (financial, personal, confidential)
- [ ] Business proposals/outreach
- [ ] Any irreversible communication

### May Skip Approval For:
- [ ] Internal test emails (same domain)
- [ ] Replies to ongoing approved conversations
- [ ] Automated system notifications (pre-approved templates)

**Decision:** If ANY "Always Require" box checked → ⚠️ Approval REQUIRED

---

## Step 2: Draft Email (Do Not Send Yet)

Create email draft with:

| Field | Value |
|-------|-------|
| To | {recipient_email} |
| Subject | {subject_line} |
| CC | {cc_recipients} (if any) |
| BCC | {bcc_recipients} (if any) |
| Body Type | Plain text or HTML |
| Attachments | {file_paths} (if any) |

### Email Content Template:
```
Subject: {subject}

Dear {recipient_name},

{Opening greeting}

{Main content - clear and concise}

{Call-to-action if needed}

Best regards,
AI Employee
{Company/Department}
```

---

## Step 3: Create Approval Request File

If approval required, create file in `/Pending_Approval/`:

**Filename:** `APPROVAL_REQUIRED_email_{sequential_id}.md`

### Approval File Structure:

```markdown
---
approval_id: "EMAIL_{sequential_number}"
type: "email"
created_at: "{YYYY-MM-DD HH:MM}"
status: "Pending | Approved | Rejected"
action_type: "Send email"
recipient: "{email_address}"
subject: "{email_subject}"
risk_level: "High | Medium | Low"
---

# Approval Required: Send Email

**Request ID:** `EMAIL_{number}`
**Created:** {date}
**Status:** ⏳ Pending Review
**Risk Level:** {risk_level}

---

## 📋 Action Requested

**What:** Send email to {recipient}
**Subject:** {subject}
**Why:** {reason/justification}
**When:** {deadline/urgency}

---

## 🔍 Email Details

| Field | Value |
|-------|-------|
| To | {recipient_email} |
| From | {sender_email} |
| Subject | {subject} |
| CC | {cc_recipients} |
| BCC | {bcc_recipients} |
| Attachments | {attachment_list} |

---

## 📝 Email Draft (Preview)

```
Subject: {subject}

{First 200 characters of body...}

[Full draft below]
```

---

## 📄 Full Email Draft

```markdown
{Complete email content exactly as it will be sent}
```

---

## ⚠️ Risk Assessment

### Why Approval Is Required
{Explain which Company Handbook rule triggers approval}

### Potential Risks
- Recipient legitimacy unverified
- Content may require review
- Irreversible action (cannot undo send)
- {other specific risks}

### Mitigation
- Draft reviewed before sending
- No sensitive data included (or justified)
- Professional tone maintained

---

## ✅ Recommended Action

**Recommendation:** {Approve/Review Carefully}

**Reasoning:**
{Explain why this recommendation is made}

---

## 📝 Instructions for Human Reviewer

### To Approve:
1. Review recipient email address
2. Review email content above
3. Move this file to: `/Approved/`
4. Email will be sent automatically

### To Reject:
1. Move this file to: `/Rejected/`
2. Optionally add rejection reason
3. Email will NOT be sent

### To Request Changes:
1. Add comments to this file
2. Keep file in `/Pending_Approval/`
3. AI will wait for updated approval

---

## ⏱️ Timeline

- **Created:** {timestamp}
- **Review By:** {deadline if urgent}
- **Auto-Expire:** {optional: after X days}

---

## 📎 Related Files
- Source: `/Needs_Action/{original_request}`
- Plan: `/Plans/PLAN_{name}.md`
- Attachments: {file_paths}

---

*This approval request was generated automatically per Company Handbook rules.*
*Do not edit this file directly - move to Approved/ or Rejected/ folder.*
```

---

## Step 4: Monitor Approval Status

After creating approval request:

### Poll Pending_Approval/ Folder
Check every 30 seconds for file movement:

```
IF file moved to /Approved/:
    → Proceed to Step 5 (Send Email)
    → Update status to "Approved"
    → Log in Dashboard.md

IF file moved to /Rejected/:
    → Cancel email
    → Update status to "Rejected"
    → Log in Dashboard.md

IF file stays in /Pending_Approval/:
    → Continue waiting
    → Optionally remind user (after timeout)
```

---

## Step 5: Send Email (After Approval)

Once approval file is in `/Approved/`:

### Using Gmail MCP:

```json
{
  "name": "gmail_send_email",
  "arguments": {
    "to": "{recipient_email}",
    "subject": "{subject}",
    "body": "{email_body}",
    "html": false,
    "cc": "{cc_recipients}",
    "bcc": "{bcc_recipients}",
    "attachments": ["{file_path1}", "{file_path2}"]
  }
}
```

### Expected Response:
```json
{
  "success": true,
  "message_id": "18xxxxxxxxxxxxxx",
  "thread_id": "18yyyyyyyyyyyyyy"
}
```

### On Success:
1. Record message_id in approval file
2. Move approval file to `/Done/`
3. Update Dashboard.md

### On Failure:
1. Log error in approval file
2. Move to `/Needs_Action/` for review
3. Notify user of failure

---

## Step 6: Log Activity

Update `/Dashboard.md`:

```markdown
## Email Activity

| Date | Recipient | Subject | Status | Message ID |
|------|-----------|---------|--------|------------|
| {date} | {email} | {subject} | ✅ Sent | {message_id} |
| {date} | {email} | {subject} | ❌ Rejected | - |
```

---

## Input Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `{recipient}` | Email recipient address | ✅ |
| `{subject}` | Email subject line | ✅ |
| `{body}` | Email body content | ✅ |
| `{html}` | Is body HTML? (default: false) | ❌ |
| `{cc}` | CC recipients | ❌ |
| `{bcc}` | BCC recipients | ❌ |
| `{attachments}` | File paths to attach | ❌ |
| `{urgency}` | Urgent/Normal/Low | ❌ |
| `{approval_skip}` | Skip approval? (rare) | ❌ |

---

## Email Templates

### Template 1: Introductory Email

```markdown
Subject: Introduction - {Your Company}

Dear {Name},

I hope this email finds you well.

My name is {Name} and I'm reaching out from {Company}. 
{Brief value proposition}.

Would you be available for a brief call next week to discuss 
how we might help {their_company}?

Best regards,
{Your Name}
{Title}
{Contact Information}
```

### Template 2: Response to Inquiry

```markdown
Subject: Re: {Their Subject}

Dear {Name},

Thank you for your interest in {Company/Service}.

{Answer their question/provide requested information}

Please let me know if you have any additional questions.

Best regards,
{Your Name}
{Title}
```

### Template 3: Follow-Up Email

```markdown
Subject: Following Up - {Previous Topic}

Dear {Name},

I wanted to follow up on my previous email regarding {topic}.

{Brief reminder of value proposition}

Is this still something you'd be interested in exploring?

Best regards,
{Your Name}
{Title}
```

### Template 4: Internal Test Email

```markdown
Subject: [TEST] Email System Verification

Hi Team,

This is a test email to verify the email system is functioning correctly.

No action required.

Best regards,
AI Employee
```

---

## Approval Type: Email-Specific

### Low Risk (May Skip Approval):
- Internal test emails
- Replies to ongoing approved threads
- Pre-approved template notifications

### Medium Risk (Require Approval):
- New external contacts
- Business development outreach
- Responses to new inquiries

### High Risk (Require Approval + Extra Review):
- Financial information included
- Personal/confidential data
- Large recipient lists
- Attachments included

---

## Example Usage

### Example 1: New Contact Outreach

**User:** Send email to newlead@example.com about our services

**Agent:**

#### Step 1: Assess Approval Need
- **Recipient:** newlead@example.com (NEW contact)
- **Content:** Business outreach
- **Decision:** ⚠️ Approval REQUIRED (Medium Risk)

#### Step 2: Draft Email
```
Subject: Introduction - AI Employee Services

Dear New Lead,

I hope this email finds you well.

I'm reaching out from AI Employee Vault to introduce our 
automated business services...

[Full draft created]
```

#### Step 3: Create Approval Request
Created: `/Pending_Approval/APPROVAL_REQUIRED_email_001.md`

#### Step 4: Wait for Review
⏳ **Status:** Awaiting human approval

#### Step 5: Send After Approval
*User moves file to Approved/*
→ Email sent via Gmail MCP
→ Message ID recorded
→ Dashboard updated

---

### Example 2: Test Email (Low Risk)

**User:** Send test email to anushakashif45@gmail.com

**Agent:**

#### Step 1: Assess Approval Need
- **Recipient:** Known contact
- **Content:** Test email
- **Decision:** ⚠️ Approval still REQUIRED (irreversible action)

#### Step 2-5: Follow Standard Process
- Draft test email
- Create approval request
- Wait for approval
- Send after approved

---

### Example 3: Reply to Existing Thread

**User:** Reply to john@partner.com confirming our meeting

**Agent:**

#### Step 1: Assess Approval Need
- **Recipient:** Existing contact (john@partner.com)
- **Content:** Meeting confirmation (routine)
- **Context:** Reply to ongoing conversation
- **Decision:** ⚠️ Approval REQUIRED (external communication)

#### Step 2-5: Follow Standard Process
Even for routine replies, approval ensures:
- Correct recipient
- Appropriate content
- No accidental sends

---

## Output Format

### When Creating Approval Request:
```markdown
### ⚠️ Email Approval Required

**Recipient:** {email}
**Subject:** {subject}
**Risk Level:** {High/Medium/Low}

### 📝 Approval Request Created
**File:** `/Pending_Approval/APPROVAL_REQUIRED_email_{id}.md`

### ⏳ Awaiting Review
- To approve: Move file to `/Approved/`
- To reject: Move file to `/Rejected/`
- Email will send automatically after approval
```

### After Sending:
```markdown
### ✅ Email Sent Successfully

**Message ID:** {message_id}
**Thread ID:** {thread_id}
**Recipient:** {email}
**Subject:** {subject}

### 📋 Logged
- Approval file moved to `/Done/`
- Dashboard.md updated
```

### If Rejected:
```markdown
### ❌ Email Rejected

**Approval ID:** {id}
**Reason:** {if provided}

### Action Cancelled
- Email NOT sent
- Approval file moved to `/Done/`
- Dashboard.md updated
```

---

## Gmail MCP Integration

### Available Tools:

| Tool | Description |
|------|-------------|
| `gmail_send_email` | Send email with optional HTML/attachments |
| `gmail_search_emails` | Search for existing emails |
| `gmail_read_email` | Read specific email by ID |
| `gmail_mark_read` | Mark email as read |
| `gmail_archive` | Archive email |
| `gmail_delete` | Delete email |

### Send Email Tool Schema:
```json
{
  "name": "gmail_send_email",
  "description": "Send an email with optional HTML body and attachments",
  "inputSchema": {
    "type": "object",
    "properties": {
      "to": {"type": "string", "description": "Recipient email address"},
      "subject": {"type": "string", "description": "Email subject"},
      "body": {"type": "string", "description": "Email body content"},
      "html": {"type": "boolean", "description": "Whether body is HTML (default: false)"},
      "cc": {"type": "string", "description": "CC recipients (optional)"},
      "bcc": {"type": "string", "description": "BCC recipients (optional)"},
      "attachments": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of file paths to attach (optional)"
      }
    },
    "required": ["to", "subject", "body"]
  }
}
```

---

## Error Handling

| Error | Handling |
|-------|----------|
| Gmail API authentication failed | Report error, suggest re-authentication |
| Recipient invalid | Flag in approval file, do not send |
| Attachment not found | Remove attachment, notify user |
| Send fails after approval | Log error, move to Needs_Action/ |
| Approval file missing | Do not send, report error |

---

## Integration with Other Skills

### With HITL_Skill:
```
Email_Action_Skill → Uses HITL_Skill for approval workflow
```

### With Planning_Skill:
```
Planning_Skill → Email task identified → Email_Action_Skill
```

### With File_IO_Skill:
```
File_IO_Skill → Read email templates/attachments → Email_Action_Skill
```

---

## Security Notes

### Never Include in Emails:
- [ ] API keys or credentials
- [ ] Full credit card numbers
- [ ] Passwords (even hashed)
- [ ] Internal system details
- [ ] Unencrypted sensitive personal data

### Always Verify:
- [ ] Recipient email address is correct
- [ ] Attachments are appropriate
- [ ] Content matches approval request
- [ ] CC/BCC recipients are intended

---

## Monitoring & Reminders

### Polling Interval
- Check `/Pending_Approval/` every 30 seconds
- Detect file movement to Approved/ or Rejected/

### Reminder Schedule
| Time Elapsed | Action |
|--------------|--------|
| 1 hour | No reminder |
| 4 hours | Gentle reminder |
| 24 hours | Urgent reminder |
| 7 days | Expire approval request |

---

## Quick Commands

### Draft and Send Email
```
Using Email_Action_Skill: send email to {email} about {subject}
```

### Draft Only (No Send Workflow)
```
Using Email_Action_Skill: draft email to {email} - subject: {subject}
```

### Check Email Approval Status
```
Using Email_Action_Skill: status of EMAIL_{id}?
```

### List Pending Email Approvals
```
Using Email_Action_Skill: list pending email approvals
```

---

## Notes
- **Always** create approval request before sending (no exceptions for external emails)
- Approval files are auto-generated - do not edit directly
- Moving file to Approved/ triggers automatic send
- All email activity logged in Dashboard.md for audit trail
- Failed sends are moved to Needs_Action/ for manual review
- Test internal email system periodically

---

## Audit Trail

Every email action creates a permanent record:

1. **Approval Request** → `/Pending_Approval/APPROVAL_REQUIRED_email_{id}.md`
2. **After Decision** → `/Approved/` or `/Rejected/`
3. **After Send** → `/Done/email_{id}_sent.md`
4. **Dashboard Log** → Entry in `/Dashboard.md`

This ensures full traceability of all email communications.
