# LinkedIn Post Skill

**Skill ID:** `linkedin_post`
**Version:** 1.0
**Last Updated:** March 6, 2026

---

## Description

Manages LinkedIn posts safely. Drafts professional sales/business content and only posts after explicit human approval.

---

## ⚠️ CRITICAL: Read Company Handbook First

**BEFORE any LinkedIn action, always:**
1. Read `Company_Handbook.md` → Section: "LinkedIn Posting Safety Rules"
2. Follow all rules exactly (NEVER auto-post, draft only, max 2/day, etc.)
3. If handbook is missing, abort and notify user

---

## Key Rules

### 1. Session Management
- Load persistent browser session from `./linkedin_session/`
- Assume user has logged in once via `linkedin_login.py`
- **If session invalid** (logged out/error): Tell user to re-run `python linkedin_login.py`
- Do NOT attempt to auto-login or re-authenticate

### 2. Drafting Posts (Safe - No Auto-Posting)
- Create engaging post text with:
  - Professional tone (business/sales focused)
  - Relevant hashtags (5-10)
  - Clear call-to-action (CTA)
- Save draft to: `Pending_Approval/LinkedIn_Draft_{YYYY-MM-DD}.md`
- **NEVER post automatically from daily tasks or scheduled jobs**
- Update `Dashboard.md`: "LinkedIn draft created for today - review in Pending_Approval"

### 3. Posting (Only After Explicit Approval)
- Check `Approved/` folder for files like: `LinkedIn_Post_{date}.md`
- **If approved file found:**
  1. Load persistent session
  2. Navigate to `https://www.linkedin.com/feed/`
  3. Open post composer (click "Start a post")
  4. Paste post content into editor
  5. Add random delays (5-15 seconds) between all actions
  6. Click "Post" button
  7. Verify post published
  8. Log success/failure to `Logs/linkedin_{date}.log`
  9. Move file to `Done/` folder
  10. Update `Dashboard.md`: "LinkedIn post published on {date}"

### 4. Safety Rules
- **Headless=False** for first few posts (user can see browser actions)
- Maximum **2 posts per day**
- **Abort immediately** on any error - do NOT retry
- Add random delays (5-15s) between all actions
- If session expires, post fails, or detection risk → notify user
- Log every attempt (success or failure)

---

## Python Code Snippets

### Load Persistent Context

```python
from playwright.sync_api import sync_playwright
from pathlib import Path

SESSION_DIR = Path("./linkedin_session")

def load_linkedin_session():
    """Load persistent LinkedIn session."""
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,  # Visible for safety
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()
        page.goto("https://www.linkedin.com/feed/", wait_until='domcontentloaded')
        
        # Check if logged in
        if 'login' in page.url:
            context.close()
            raise Exception("Session invalid. Please run: python linkedin_login.py")
        
        return context, page
```

### Drafting & Saving

```python
from pathlib import Path
from datetime import datetime

def create_linkedin_draft(post_content: str, topic: str = "Business Update"):
    """Create a LinkedIn post draft for approval."""
    now = datetime.now()
    
    draft_content = f"""---
approval_id: "LINKEDIN_DRAFT_{now.strftime('%Y-%m-%d')}"
type: "linkedin_post_draft"
created_at: "{now.strftime('%Y-%m-%d %H:%M')}"
status: "Pending Review"
topic: "{topic}"
---

# LinkedIn Post Draft - {now.strftime('%Y-%m-%d')}

**Status:** ⏳ Awaiting Your Review

---

## 📝 Post Draft

```markdown
{post_content}
```

---

## 📝 Instructions

### To Approve:
1. Review post content above
2. Move this file to: `Approved/`
3. Rename to: `LinkedIn_Post_{now.strftime('%Y%m%d')}.md`
4. Post will be published when you run the posting script

### To Reject:
1. Move this file to: `Rejected/`
2. Post will NOT be published

---

**⚠️ This draft requires your approval before posting.**
"""
    
    # Save to Pending_Approval
    pending_dir = Path("./Pending_Approval")
    pending_dir.mkdir(exist_ok=True)
    
    draft_file = pending_dir / f"LinkedIn_Draft_{now.strftime('%Y-%m-%d')}.md"
    draft_file.write_text(draft_content, encoding='utf-8')
    
    # Update Dashboard
    dashboard_file = Path("Dashboard.md")
    if dashboard_file.exists():
        content = dashboard_file.read_text(encoding='utf-8')
        content += f"\n- [{now.strftime('%Y-%m-%d %H:%M')}] LinkedIn draft created for today - review in Pending_Approval\n"
        dashboard_file.write_text(content, encoding='utf-8')
    
    print("[Daily LinkedIn] Draft created safely")
    return str(draft_file)
```

### Posting Only If Approved File Exists

```python
from pathlib import Path
import time
import random
from datetime import datetime

def post_to_linkedin_if_approved():
    """Post to LinkedIn ONLY if approved file exists."""
    
    # Check Company Handbook first
    handbook_path = Path("Company_Handbook.md")
    if handbook_path.exists():
        content = handbook_path.read_text(encoding='utf-8')
        if "NEVER auto-post" not in content:
            print("⚠️ Warning: Company Handbook may not have safety rules")
    
    # Check for approved files
    approved_dir = Path("./Approved")
    if not approved_dir.exists():
        print("No Approved/ folder found - no posts to publish")
        return
    
    approved_files = list(approved_dir.glob("LinkedIn_Post_*.md"))
    if not approved_files:
        print("No approved LinkedIn posts found in Approved/ folder")
        print("Drafts must be moved from Pending_Approval/ to Approved/ first")
        return
    
    # Process each approved file
    for approved_file in approved_files:
        result = post_to_linkedin(approved_file)
        
        if result['success']:
            # Move to Done
            done_dir = Path("./Done")
            done_dir.mkdir(exist_ok=True)
            approved_file.rename(done_dir / approved_file.name)
            
            # Update Dashboard
            dashboard_file = Path("Dashboard.md")
            if dashboard_file.exists():
                content = dashboard_file.read_text(encoding='utf-8')
                content += f"\n- [{datetime.now().strftime('%Y-%m-%d %H:%M')}] LinkedIn post published on {datetime.now().strftime('%Y-%m-%d')}\n"
                dashboard_file.write_text(content, encoding='utf-8')
        else:
            if result.get('session_invalid'):
                print("\n❌ Session invalid. Please run: python linkedin_login.py")
                return
            else:
                # Move to Needs_Action
                needs_action_dir = Path("./Needs_Action")
                needs_action_dir.mkdir(exist_ok=True)
                approved_file.rename(needs_action_dir / approved_file.name)
                print(f"\n⚠️ Post failed. File moved to Needs_Action/")
                print(f"   Error: {result.get('error')}")

def post_to_linkedin(approved_file: Path) -> dict:
    """Actually post to LinkedIn with all safety measures."""
    
    content = approved_file.read_text(encoding='utf-8')
    
    # Extract post content from markdown block
    import re
    post_match = re.search(r'```markdown\s*(.*?)\s*```', content, re.DOTALL)
    if not post_match:
        return {'success': False, 'error': 'Could not extract post content'}
    
    post_content = post_match.group(1).strip()
    approval_id = re.search(r'approval_id: "([^"]+)"', content)
    approval_id = approval_id.group(1) if approval_id else "UNKNOWN"
    
    print(f"\nProcessing approved post: {approval_id}")
    
    # Load session
    try:
        context, page = load_linkedin_session()
    except Exception as e:
        return {'success': False, 'error': str(e), 'session_invalid': True}
    
    try:
        # Random delay before starting
        time.sleep(random.uniform(5, 10))
        
        # Navigate to feed
        page.goto("https://www.linkedin.com/feed/", wait_until='domcontentloaded')
        time.sleep(random.uniform(5, 10))
        
        # Click "Start a post"
        page.get_by_text("Start a post", exact=False).first.click()
        time.sleep(random.uniform(5, 10))
        
        # Find editor and fill content
        dialog = page.locator('div[role="dialog"]').first
        dialog.wait_for(state='visible', timeout=10000)
        
        editor = dialog.locator('div[role="textbox"][contenteditable="true"]').first
        editor.wait_for(state='visible', timeout=10000)
        editor.fill(post_content)
        time.sleep(random.uniform(5, 10))
        
        # Click Post button
        post_button = page.get_by_text("Post", exact=True).last
        post_button.scroll_into_view_if_needed()
        time.sleep(random.uniform(3, 7))
        post_button.click()
        
        # Wait for post to publish
        time.sleep(random.uniform(5, 10))
        
        # Log success
        log_action(approval_id, "SUCCESS", f"Post URL: {page.url}")
        
        return {'success': True, 'post_url': page.url, 'approval_id': approval_id}
        
    except Exception as e:
        log_action(approval_id, "ERROR", str(e))
        return {'success': False, 'error': str(e)}
    finally:
        context.close()

def log_action(approval_id: str, status: str, details: str):
    """Log action to Logs folder."""
    from pathlib import Path
    from datetime import datetime
    
    logs_dir = Path("./Logs")
    logs_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"\n---\n## {approval_id} - {timestamp} - {status}\n{details}\n"
    
    log_file = logs_dir / f"linkedin_{datetime.now().strftime('%Y%m%d')}.log"
    content = log_file.read_text(encoding='utf-8') + log_entry if log_file.exists() else f"# LinkedIn Logs\n{log_entry}"
    log_file.write_text(content, encoding='utf-8')
```

---

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    LinkedIn Post Skill                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │ Read Company Handbook   │
              │ (LinkedIn Safety Rules) │
              └─────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   Daily Task (8 AM)     │
              │  create_linkedin_draft()│
              └─────────────────────────┘
                            │
                            ▼
              Save to Pending_Approval/
              Print: "Draft created safely"
                            │
                            ▼
              ┌─────────────────────────┐
              │  WAIT FOR USER REVIEW   │
              └─────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
    User approves                  User rejects
    (move to Approved/)            (move to Rejected/)
            │                               │
            ▼                               │
    ┌───────────────────┐                  │
    │ Check Approved/   │                  │
    │ for LinkedIn_Post │                  │
    └───────────────────┘                  │
            │                               │
            ▼                               ▼
    ┌───────────────────┐          ┌──────────────┐
    │ Load Session      │          │ END (No post)│
    │ Navigate to feed  │          └──────────────┘
    │ Open composer     │
    │ Paste content     │
    │ Add delays        │
    │ Click Post        │
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Log to Logs/      │
    │ Update Dashboard  │
    │ Move to Done/     │
    └───────────────────┘
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Session invalid | Tell user: "Please run `python linkedin_login.py`" |
| Post button not found | Log error, move file to Needs_Action/, notify user |
| Content not entered | Take screenshot, log error, abort |
| Network timeout | Log error, abort (no retry) |
| Detection risk | Abort immediately, notify user |

---

## Files Modified

- `Pending_Approval/LinkedIn_Draft_{date}.md` - Draft created here
- `Approved/LinkedIn_Post_{date}.md` - User moves approved draft here
- `Done/LinkedIn_Post_{date}.md` - Successfully posted file moved here
- `Logs/linkedin_{date}.log` - All attempts logged here
- `Dashboard.md` - Updated with draft/post status

---

## Testing

To test the skill safely:

```python
# Test drafting (safe - no posting)
from Skills.linkedin_post_skill import create_linkedin_draft
create_linkedin_draft("Test post content", "Test Topic")

# Test posting (only if you have an approved file)
from Skills.linkedin_post_skill import post_to_linkedin_if_approved
post_to_linkedin_if_approved()
```

---

*This skill follows the Company Handbook LinkedIn Posting Safety Rules exactly.*
*Never modify this skill without reviewing those rules first.*
