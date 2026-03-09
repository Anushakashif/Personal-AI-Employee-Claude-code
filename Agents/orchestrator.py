#!/usr/bin/env python3
"""
Orchestrator Script for AI Employee Vault

Automatically processes files in /Needs_Action:
1. Reads file content and extracts task info
2. Updates Dashboard.md with new activity
3. Moves completed files to /Done folder with completion status

Loop interval: 60 seconds

Daily Schedule (8 AM):
- Monday: Generate CEO Morning Briefing, create LinkedIn post draft, process all Needs_Action
- Tuesday-Friday: Process all Needs_Action, daily briefing
"""

import os
import time
import shutil
import json
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict


class VaultOrchestrator:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.needs_action_dir = self.base_dir / "Needs_Action"
        self.done_dir = self.base_dir / "Done"
        self.dashboard_path = self.base_dir / "Done" / "Dashboard.md"
        self.plans_dir = self.base_dir / "Plans"
        self.pending_approval_dir = self.base_dir / "Pending_Approval"
        self.poll_interval = 60  # seconds
        self.daily_run_hour = 8  # 8 AM

        # Track processed files to avoid duplicate processing
        self.processed_files = set()

        # Track last daily run to avoid duplicate daily tasks
        self.last_daily_run = None

        # Ensure directories exist
        self.needs_action_dir.mkdir(parents=True, exist_ok=True)
        self.done_dir.mkdir(parents=True, exist_ok=True)
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.pending_approval_dir.mkdir(parents=True, exist_ok=True)

    def get_pending_files(self):
        """Get list of .md files in Needs_Action that haven't been processed yet."""
        pending = []
        for file_path in self.needs_action_dir.iterdir():
            # Skip non-files and metadata files
            if not file_path.is_file():
                continue
            if file_path.suffix != '.md':
                continue
            if '_metadata.md' in file_path.name:
                continue
            if file_path.name not in self.processed_files:
                pending.append(file_path)
        return pending

    def should_run_daily_tasks(self) -> bool:
        """Check if daily tasks should run (8 AM, not yet run today)."""
        now = datetime.now()
        today = now.date()
        
        # Check if already ran today
        if self.last_daily_run and self.last_daily_run.date() == today:
            return False
        
        # Check if it's the daily run hour (8 AM)
        if now.hour != self.daily_run_hour:
            return False
        
        # Check if within the first 10 minutes of the hour (to avoid multiple triggers)
        if now.minute > 10:
            return False
        
        return True

    def generate_ceo_briefing(self) -> str:
        """Generate Monday Morning CEO Briefing."""
        now = datetime.now()
        week_num = now.isocalendar()[1]
        
        # Gather metrics from Done folder
        completed_tasks = []
        if self.done_dir.exists():
            for item in self.done_dir.iterdir():
                if item.is_dir():
                    completed_tasks.append(item.name.replace("_", " "))
        
        # Check Pending_Approval for pending items
        pending_approvals = []
        for item in self.pending_approval_dir.iterdir():
            if item.is_file() and item.suffix == '.md':
                pending_approvals.append(item.name)
        
        # Check Needs_Action for pending items
        needs_action_count = len(self.get_pending_files())
        
        # Read Company Handbook for business goals
        handbook_path = self.base_dir / "Company_Handbook.md"
        business_goals = []
        if handbook_path.exists():
            with open(handbook_path, 'r') as f:
                content = f.read()
                if "Generate sales leads" in content:
                    business_goals.append("Generate sales leads via LinkedIn")
                if "Track invoices" in content:
                    business_goals.append("Track invoices and payments")
        
        briefing_content = f"""---
briefing_id: "CEO_BRIEF_{now.strftime('%Y%m%d')}"
type: "ceo_briefing"
generated_at: "{now.strftime('%Y-%m-%d %H:%M')}"
period: "Week {week_num}, {now.strftime('%B %Y')}"
---

# 📊 CEO Morning Briefing

**Generated:** {now.strftime('%A, %B %d, %Y at %I:%M %p')}
**Period:** Week {week_num} of {now.year}

---

## 🎯 Executive Summary

Good morning! Here's your business overview for this week.

---

## 📈 Key Metrics

| Metric | Value |
|--------|-------|
| Tasks Completed (Last Week) | {len(completed_tasks)} |
| Pending Approvals | {len(pending_approvals)} |
| Items Needing Action | {needs_action_count} |
| Current Week | {week_num} |

---

## ✅ Recent Accomplishments

"""
        
        if completed_tasks:
            for task in completed_tasks[:10]:  # Show last 10
                briefing_content += f"- {task}\n"
        else:
            briefing_content += "- No completed tasks recorded\n"
        
        briefing_content += f"""
---

## ⏳ Pending Approvals

"""
        
        if pending_approvals:
            for approval in pending_approvals[:5]:  # Show up to 5
                briefing_content += f"- ⏳ {approval}\n"
        else:
            briefing_content += "- ✅ No pending approvals\n"
        
        briefing_content += f"""
---

## 🎯 Business Goals Progress

"""
        
        for goal in business_goals:
            briefing_content += f"- 📌 {goal}\n"
        
        briefing_content += f"""
---

## 📋 Priority Actions for This Week

"""
        
        if needs_action_count > 0:
            briefing_content += f"- ⚠️ {needs_action_count} item(s) in Needs_Action require attention\n"
        else:
            briefing_content += "- ✅ All items processed\n"
        
        if len(pending_approvals) > 0:
            briefing_content += f"- ⏳ Review {len(pending_approvals)} pending approval(s)\n"
        
        briefing_content += f"""
---

## 💡 Recommended Focus

1. **Review Pending Approvals** - Move files from `/Pending_Approval/` to `/Approved/` or `/Rejected/`
2. **Process Needs_Action** - Items are being processed automatically
3. **LinkedIn Engagement** - Review and approve drafted posts for lead generation

---

## 📅 Today's Schedule

- **{now.strftime('%I:%M %p')}** - Review this briefing
- **Morning** - Approve pending items
- **Afternoon** - Focus on high-priority tasks

---

## 🔔 Reminders

- Files in `/Pending_Approval/` require your review before actions are taken
- LinkedIn posts are drafted for your approval before publishing
- All activity is logged in `/Dashboard.md`

---

*Briefing generated automatically by AI Employee Vault*
*Next briefing: Monday {now + timedelta(days=7):%B %d, %Y}*
"""
        
        # Save briefing to Plans folder
        briefing_file = self.plans_dir / f"CEO_BRIEF_{now.strftime('%Y%m%d')}.md"
        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write(briefing_content)
        
        return str(briefing_file)

    def create_linkedin_post_draft(self) -> str:
        """Create a LinkedIn post draft for approval."""
        now = datetime.now()
        
        # Read Company Handbook for business context
        handbook_path = self.base_dir / "Company_Handbook.md"
        business_goals = []
        if handbook_path.exists():
            with open(handbook_path, 'r') as f:
                content = f.read()
                if "Generate sales leads" in content:
                    business_goals.append("lead_generation")
        
        # Create professional LinkedIn post draft
        post_content = f"""---
approval_id: "LINKEDIN_{now.strftime('%Y%m%d')}_001"
type: "linkedin_post"
created_at: "{now.strftime('%Y-%m-%d %H:%M')}"
status: "Pending"
action_type: "Publish LinkedIn post"
platform: "LinkedIn"
risk_level: "Medium"
---

# Approval Required: LinkedIn Post - Weekly Business Update

**Request ID:** `LINKEDIN_{now.strftime('%Y%m%d')}_001`
**Created:** {now.strftime('%Y-%m-%d %H:%M')}
**Status:** ⏳ Pending Review
**Risk Level:** Medium

---

## 📋 Action Requested

**What:** Publish weekly business update post to LinkedIn
**Topic:** Business automation and efficiency
**Why:** Generate sales leads (per Company Handbook business goals)
**When:** Suggested post time: {now.strftime('%A')} at 10:00 AM

---

## 🔍 Post Details

| Field | Value |
|-------|-------|
| Platform | LinkedIn |
| Character Count | ~250 |
| Hashtags | 5 |
| Media | None (can add) |

---

## 📝 Post Draft (Preview)

```
💡 Is Your Team Spending Too Much Time on Manual Tasks?

Here's what we're seeing in 2026:

→ 60% of work hours spent on repetitive tasks
→ Teams overwhelmed by email, documents, scheduling
→ Business leaders missing strategic opportunities

The solution? Intelligent automation.

Our AI Employee Vault helps businesses:
✅ Automate email management
✅ Process documents intelligently
✅ Plan and schedule automatically

Result? Your team focuses on what matters most.

Ready to transform your workflow? Let's connect!

#BusinessAutomation #AI #Productivity #DigitalTransformation #SmallBusiness
```

---

## ⚠️ Risk Assessment

### Why Approval Is Required
Per Company Handbook: Public posts require review before publishing.

### Potential Risks
- Public-facing communication affects brand
- Content may be misinterpreted

### Mitigation
- Content follows professional guidelines
- Value-focused, not spammy
- Professional tone maintained

---

## ✅ Recommended Action

**Recommendation:** Approve

**Reasoning:**
- Post aligns with business goals (lead generation)
- Content provides value, not pure promotion
- Professional tone maintained
- Includes clear CTA

---

## 📝 Instructions for Human Reviewer

### To Approve:
1. Review post content above
2. Move this file to: `/Approved/`
3. Post will be published automatically

### To Reject:
1. Move this file to: `/Rejected/`
2. Optionally add rejection reason
3. Post will NOT be published

---

*This approval request was generated automatically per Company Handbook rules.*
*Do not edit this file directly - move to Approved/ or Rejected/ folder.*
"""
        
        # Save draft to Pending_Approval folder
        draft_file = self.pending_approval_dir / f"APPROVAL_REQUIRED_linkedin_{now.strftime('%Y%m%d')}_001.md"
        with open(draft_file, 'w', encoding='utf-8') as f:
            f.write(post_content)
        
        return str(draft_file)

    def process_all_needs_action(self) -> Dict:
        """Process all files in Needs_Action folder."""
        results = {
            'processed': 0,
            'errors': 0,
            'files': []
        }
        
        pending_files = self.get_pending_files()
        
        for file_path in pending_files:
            try:
                self.process_file(file_path)
                results['processed'] += 1
                results['files'].append({
                    'file': file_path.name,
                    'status': 'processed'
                })
            except Exception as e:
                results['errors'] += 1
                results['files'].append({
                    'file': file_path.name,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results

    def run_daily_tasks(self):
        """Execute daily scheduled tasks at 8 AM."""
        now = datetime.now()
        print(f"\n{'='*60}")
        print(f"📅 DAILY SCHEDULED TASKS - {now.strftime('%A, %B %d, %Y')}")
        print(f"{'='*60}\n")
        
        tasks_completed = []
        
        # Task 1: Generate CEO Briefing (every day, more detailed on Monday)
        print("📊 Generating CEO Morning Briefing...")
        try:
            briefing_file = self.generate_ceo_briefing()
            print(f"  ✅ Briefing created: {briefing_file}")
            tasks_completed.append("CEO Briefing Generated")
        except Exception as e:
            print(f"  ❌ Briefing failed: {e}")
        
        # Task 2: Create LinkedIn Post Draft (especially important on Monday)
        print("\n📝 Creating LinkedIn Post Draft...")
        try:
            draft_file = self.create_linkedin_post_draft()
            print(f"  ✅ Draft created: {draft_file}")
            print(f"  📍 Saved to: /Pending_Approval/")
            print(f"  ⏳ Awaiting your approval to publish")
            tasks_completed.append("LinkedIn Post Draft Created")
        except Exception as e:
            print(f"  ❌ LinkedIn draft failed: {e}")

        # Task 3: Daily LinkedIn Draft (safe - no auto-posting)
        print("\n🔗 Running daily LinkedIn draft at 8 AM...")
        try:
            draft_file = self.daily_linkedin_draft()
            print(f"  📍 Saved to: /Pending_Approval/")
            print(f"  ⏳ Awaiting your review")
            tasks_completed.append("Daily LinkedIn Draft Created")
        except Exception as e:
            print(f"  ❌ Daily LinkedIn draft failed: {e}")

        # Task 4: Process All Needs_Action Items
        print("\n📋 Processing Needs_Action Items...")
        try:
            results = self.process_all_needs_action()
            print(f"  ✅ Processed: {results['processed']} files")
            if results['errors'] > 0:
                print(f"  ⚠️ Errors: {results['errors']}")
            tasks_completed.append(f"Processed {results['processed']} Needs_Action items")
        except Exception as e:
            print(f"  ❌ Processing failed: {e}")
        
        # Log daily tasks to Dashboard
        self.log_daily_tasks(tasks_completed)
        
        # Mark daily run as complete
        self.last_daily_run = now
        
        print(f"\n{'='*60}")
        print(f"✅ DAILY TASKS COMPLETE")
        print(f"{'='*60}\n")

    def log_daily_tasks(self, tasks_completed: List[str]):
        """Log daily task completion to Dashboard."""
        now = datetime.now()
        log_entry = f"""
## Daily Automated Tasks - {now.strftime('%Y-%m-%d %H:%M')}

**Tasks Completed:**
"""
        for task in tasks_completed:
            log_entry += f"- ✅ {task}\n"
        
        log_entry += f"\n---\n"
        
        if self.dashboard_path.exists():
            with open(self.dashboard_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        else:
            dashboard_content = f"""# Task Dashboard

Last Updated: {now.strftime('%Y-%m-%d %H:%M:%S')}

{log_entry}
"""
            with open(self.dashboard_path, 'w', encoding='utf-8') as f:
                f.write(dashboard_content)

    def read_file_content(self, file_path: Path) -> str:
        """Read content from a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_task_info(self, file_path: Path, content: str) -> dict:
        """Extract task information from file content."""
        # Try to find task name from filename or content
        filename = file_path.stem  # e.g., "FILE_test.txt" from "FILE_test.txt.md"
        if filename.startswith("FILE_"):
            original_name = filename[5:]  # Remove "FILE_" prefix
        else:
            original_name = filename

        # Extract message/content for task description
        lines = content.strip().split('\n')
        message = ""
        from_field = ""
        
        for line in lines:
            # Handle both "From:" and "From :" formats
            if line.lower().startswith("from") and ":" in line:
                from_field = line.split(":", 1)[1].strip()
            elif line.lower().startswith("message") and ":" in line:
                message = line.split(":", 1)[1].strip()
        
        if not message:
            message = content.strip()

        return {
            "task_name": original_name.replace(".txt", "").replace("_", " ").title(),
            "original_name": original_name,
            "from": from_field,
            "message": message,
            "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def update_dashboard(self, task_info: dict):
        """Update Dashboard.md with the new task (as pending item)."""
        dashboard_entry = f"""
## {task_info['task_name']}
- **Status:** [PENDING] Processing
- **Received:** {task_info['processed_at']}
- **From:** {task_info['from'] if task_info['from'] else 'N/A'}
- **Message:** {task_info['message']}

---
"""
        if self.dashboard_path.exists():
            # Append to existing dashboard
            with open(self.dashboard_path, 'a', encoding='utf-8') as f:
                f.write(dashboard_entry)
        else:
            # Create new dashboard
            dashboard_content = f"""# Task Dashboard

Last Updated: {task_info['processed_at']}

---
{dashboard_entry}
"""
            with open(self.dashboard_path, 'w', encoding='utf-8') as f:
                f.write(dashboard_content)

        print(f"[OK] Dashboard updated with task: {task_info['task_name']}")

    def archive_to_done(self, file_path: Path, metadata_path: Path, task_info: dict):
        """Move file and its metadata to Done folder with completion status."""
        # Create task-specific folder in Done
        task_folder = self.done_dir / task_info['task_name'].replace(" ", "_")
        task_folder.mkdir(parents=True, exist_ok=True)

        # Create completion record
        completion_content = f"""---
task_name: "{task_info['task_name']}"
status: Completed
completed_at: "{task_info['processed_at']}"
original_file: "{task_info['original_name']}"
from: "{task_info['from']}"
---

# Task Completed: {task_info['task_name']}

**Status:** [COMPLETED]  
**Completed At:** {task_info['processed_at']}  
**From:** {task_info['from'] if task_info['from'] else 'N/A'}  
**Message:** {task_info['message']}

---

## Original File Content
"""
        # Write completion record with original content
        original_content = self.read_file_content(file_path)
        with open(task_folder / f"{task_info['task_name'].replace(' ', '_')}_completed.md", 'w', encoding='utf-8') as f:
            f.write(completion_content + original_content)

        # Copy metadata if exists
        if metadata_path.exists():
            shutil.copy(metadata_path, task_folder / f"{task_info['original_name']}_metadata.md")

        # Remove from Needs_Action
        file_path.unlink()
        if metadata_path.exists():
            metadata_path.unlink()

        print(f"[OK] Archived to Done/{task_folder.name}")

    def process_file(self, file_path: Path):
        """Handle automatic processing of a single file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Processing: {file_path.name}")

        try:
            # Step 1: Read file content
            content = self.read_file_content(file_path)
            print(f"  [READ] Read file content")

            # Step 2: Extract task information
            task_info = self.extract_task_info(file_path, content)
            print(f"  [EXTRACT] Extracted task: {task_info['task_name']}")

            # Step 3: Update Dashboard.md
            self.update_dashboard(task_info)

            # Step 4: Find and archive with metadata
            metadata_path = file_path.parent / f"{file_path.stem}_metadata.md"
            self.archive_to_done(file_path, metadata_path, task_info)

            # Mark file as processed
            self.processed_files.add(file_path.name)
            print(f"[OK] File {file_path.name} processing cycle complete.\n")

        except Exception as e:
            print(f"[ERROR] Error processing {file_path.name}: {str(e)}")

    def daily_linkedin_draft(self):
        """
        Create a daily LinkedIn post draft for approval.
        Runs every day at 8:00 AM.
        Saves draft to Pending_Approval/ - NEVER posts automatically.
        """
        now = datetime.now()
        
        # Read Company Handbook for business context
        handbook_path = self.base_dir / "Company_Handbook.md"
        business_context = ""
        if handbook_path.exists():
            content = handbook_path.read_text(encoding='utf-8')
            if "Generate sales leads" in content:
                business_context = "lead_generation"
            if "AI Employee" in content:
                business_context += ", AI automation services"
        
        # Read Dashboard for recent activity context
        dashboard_context = ""
        if self.dashboard_path.exists():
            dashboard_content = self.dashboard_path.read_text(encoding='utf-8')
            # Extract recent accomplishments for post inspiration
            if "Completed" in dashboard_content:
                dashboard_context = "recent_task_completions"
        
        # Create professional business sales post
        post_content = f"""---
approval_id: "LINKEDIN_DRAFT_{now.strftime('%Y-%m-%d')}"
type: "linkedin_post_draft"
created_at: "{now.strftime('%Y-%m-%d %H:%M')}"
status: "Pending Review"
action_type: "Review and approve for LinkedIn posting"
platform: "LinkedIn"
risk_level: "Medium"
---

# LinkedIn Post Draft - {now.strftime('%Y-%m-%d')}

**Created:** {now.strftime('%Y-%m-%d %H:%M')}
**Status:** ⏳ Awaiting Your Review
**Action Required:** Move to `/Approved/` to publish, or `/Rejected/` to discard

---

## 📝 Post Draft

```markdown
🚀 Transform Your Business with AI Automation

Is your team spending too much time on:
❌ Manual email management
❌ Document processing
❌ Scheduling & coordination
❌ Repetitive administrative tasks?

The future of work is here. AI Employee Vault helps businesses:

✅ Automate 60%+ of routine tasks
✅ Process documents & emails intelligently
✅ Schedule meetings automatically
✅ Track invoices and payments seamlessly

Real results from businesses using AI Employee Vault:
→ 3x faster response times
→ 50% reduction in admin overhead
→ Teams focused on high-value work

Ready to work smarter?

📩 DM us to learn how AI Employee Vault can transform your workflow.

#BusinessAutomation #AI #Productivity #DigitalTransformation #SmallBusiness #AIEmployee #WorkflowAutomation
```

---

## 📊 Post Details

| Metric | Value |
|--------|-------|
| Character Count | ~750 |
| Hashtags | 7 |
| Tone | Professional, value-focused |
| CTA | Clear (DM for more info) |

---

## ✅ Why This Post Works

- **Value-first approach** - Highlights pain points before solution
- **Social proof** - Includes measurable results
- **Clear CTA** - Easy next step for interested prospects
- **Professional tone** - Appropriate for LinkedIn B2B audience
- **Relevant hashtags** - Improves discoverability

---

## 📝 Instructions for Human Reviewer

### To Approve & Publish:
1. Review the post content above
2. Move this file to: `/Approved/`
3. Rename to: `LinkedIn_Post_{now.strftime('%Y%m%d')}.md`
4. Post will be published automatically by the LinkedIn agent

### To Reject:
1. Move this file to: `/Rejected/`
2. Optionally add rejection reason
3. Post will NOT be published

### To Request Changes:
1. Add comments to this file
2. Keep file in `/Pending_Approval/`
3. AI will revise on next run

---

**⚠️ Important:** This draft is saved for your review only. 
No post will be published without your explicit approval.

*Generated automatically by AI Employee Vault - Daily LinkedIn Draft*
"""
        
        # Save draft to Pending_Approval folder
        draft_file = self.pending_approval_dir / f"LinkedIn_Draft_{now.strftime('%Y-%m-%d')}.md"
        with open(draft_file, 'w', encoding='utf-8') as f:
            f.write(post_content)
        
        # Update Dashboard.md
        dashboard_entry = f"\n- [{now.strftime('%Y-%m-%d %H:%M')}] LinkedIn draft created for today - review in Pending_Approval\n"
        
        dashboard_file = self.base_dir / "Dashboard.md"
        if dashboard_file.exists():
            content = dashboard_file.read_text(encoding='utf-8')
            content += dashboard_entry
            dashboard_file.write_text(content, encoding='utf-8')
        else:
            dashboard_file.write_text(f"# Dashboard\n{dashboard_entry}", encoding='utf-8')
        
        print("[Daily LinkedIn] Draft created safely")
        
        return str(draft_file)

    def run(self):
        """Main orchestration loop with scheduled daily tasks at 8:00 AM."""
        print("=" * 60)
        print("AI Employee Vault Orchestrator")
        print("=" * 60)
        print(f"Monitoring: {self.needs_action_dir}")
        print(f"Daily tasks scheduled: 8:00 AM")
        print(f"Poll interval: {self.poll_interval} seconds")
        print("Press Ctrl+C to stop")
        print("=" * 60)

        # Schedule daily tasks at 8:00 AM
        schedule.every().day.at("08:00").do(self.run_daily_tasks)

        print("\n📅 Scheduled: Daily tasks at 08:00 AM")
        print("📝 Scheduled: Daily LinkedIn draft at 08:00 AM (included in daily tasks)\n")

        try:
            while True:
                # Run scheduled tasks (checks if 8:00 AM daily tasks should run)
                schedule.run_pending()

                # Process pending files in Needs_Action
                pending_files = self.get_pending_files()

                if pending_files:
                    for file_path in pending_files:
                        self.process_file(file_path)
                else:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] No pending files. Checking again in {self.poll_interval}s...")

                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print("\n\nOrchestrator stopped by user.")


def main():
    orchestrator = VaultOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
