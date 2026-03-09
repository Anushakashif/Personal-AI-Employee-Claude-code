# Personal AI Employee

**Your 24/7 Digital Full-Time AI Employee**  
Local-first | Autonomous | Human-in-the-loop

A powerful, privacy-focused AI system that runs on your own machine and proactively handles real business & personal tasks — email monitoring, file processing, daily social media drafts, email sending, planning, and more — all while keeping you in full control.

### Core Capabilities

- **Always-On Monitoring**  
  - Watches local `Inbox/` folder for new files → automatically creates structured metadata and moves to `Needs_Action/`  
  - Continuously scans Gmail for unread/important emails → converts them into actionable `.md` files

- **Intelligent Task Processing**  
  - Automatically reads new items → generates detailed `Plan.md` files with checkboxes, timelines, dependencies, and approval flags  
  - Applies custom business rules from `Company_Handbook.md` (e.g. flag payments > $500, prioritize urgent keywords)  
  - Updates real-time `Dashboard.md` with summaries, activity logs, and pending items

- **LinkedIn Automation (Safe & Controlled)**  
  - Generates daily professional business/sales posts at 8 AM  
  - Saves drafts securely in `Pending_Approval/` — never posts automatically  
  - After manual review & approval (file moved to `Approved/`), posts using saved browser session (Playwright) with human-like delays

- **Email Automation (Secure)**  
  - Drafts replies, thank-yous, invoices, and follow-ups using Gmail MCP integration  
  - Requires explicit human approval for sending (via file move)  
  - Full audit trail and logging for every action

- **Human-in-the-Loop Safety**  
  - Sensitive actions (sending money-related emails, posting online, etc.) always pause and create approval files  
  - You decide — move to `Approved/` to proceed or `Rejected/` to cancel

- **Daily Orchestration**  
  - Runs scheduled tasks at 8:00 AM: generate LinkedIn draft, process pending items, create summaries  
  - Can be fully automated via `orchestrator.py` or triggered manually

### How It Runs (Terminal + VS Code)

```bash
# Start the three watchers
python file_watcher.py
python gmail_watcher.py
python linked_login.py

# Start the daily orchestrator
python orchestrator.py
