#!/usr/bin/env python3
"""
Publish Approved LinkedIn Post

Usage:
    python publish_linkedin.py

This script:
1. Checks Approved/ folder for LinkedIn_Post_*.md files
2. Publishes each post to LinkedIn using saved browser session
3. Moves published posts to Done/ folder
4. Updates Dashboard.md

Requires:
- Valid LinkedIn session (run: python linkedin_login.py first)
- playwright installed in venv
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import random
import re
from datetime import datetime

SESSION_DIR = Path("./linkedin_session")
APPROVED_DIR = Path("./Approved")
DONE_DIR = Path("./Done")

def load_linkedin_session():
    """Load persistent LinkedIn session."""
    playwright = sync_playwright().start()
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR),
        headless=False,
        viewport={'width': 1280, 'height': 720}
    )
    page = context.new_page()
    page.goto("https://www.linkedin.com/feed/", wait_until='domcontentloaded', timeout=60000)
    
    if 'login' in page.url:
        context.close()
        playwright.stop()
        raise Exception("Session invalid. Please run: python linkedin_login.py")
    
    return playwright, context, page

def publish_post():
    """Find and publish approved LinkedIn post."""
    
    # Find approved files
    approved_files = list(APPROVED_DIR.glob("LinkedIn_Post_*.md"))
    if not approved_files:
        print("No approved LinkedIn posts found in Approved/ folder")
        print("Drafts must be moved from Pending_Approval/ to Approved/ first")
        return
    
    for approved_file in approved_files:
        content = approved_file.read_text(encoding='utf-8')
        
        # Extract post content from markdown block
        post_match = re.search(r'```markdown\s*(.*?)\s*```', content, re.DOTALL)
        if not post_match:
            print(f"Could not extract post content from {approved_file.name}")
            continue
        
        post_content = post_match.group(1).strip()
        approval_id = re.search(r'approval_id: "([^"]+)"', content)
        approval_id = approval_id.group(1) if approval_id else "UNKNOWN"
        
        print(f"\nPublishing: {approval_id}")
        print("-" * 50)
        print(f"Content preview: {post_content[:100]}...")
        
        try:
            playwright, context, page = load_linkedin_session()
            
            # Wait for page to fully load
            time.sleep(random.uniform(5, 8))
            
            # Click "Start a post" button
            print("Looking for 'Start a post' button...")
            try:
                start_post = page.get_by_text("Start a post", exact=False).first
                start_post.click(timeout=10000)
                print("✓ Clicked 'Start a post'")
                time.sleep(random.uniform(4, 7))
            except Exception as e:
                print(f"Could not click 'Start a post': {e}")
                context.close()
                playwright.stop()
                continue
            
            # Wait for dialog and find editor
            print("Waiting for post dialog...")
            dialog = page.locator('div[role="dialog"]').first
            
            try:
                # Wait for aria-hidden to be removed
                time.sleep(3)
                
                # Try waiting with different conditions
                try:
                    dialog.wait_for(state='visible', timeout=20000)
                except:
                    # If still not visible, wait for aria-hidden to be false
                    print("Dialog not visible, waiting for aria-hidden removal...")
                    page.wait_for_selector('div[role="dialog"][aria-hidden="false"]', timeout=20000)
                    time.sleep(2)
                
                print("✓ Post dialog visible/ready")
                
                # Find the editor textbox - try multiple selectors
                editor_selectors = [
                    'div[contenteditable="true"]',
                    'div[role="textbox"]',
                    '.ql-editor',
                    '[data-id="inline-compose-editor"]'
                ]
                
                editor = None
                for selector in editor_selectors:
                    try:
                        editor = dialog.locator(selector).first
                        editor.wait_for(state='visible', timeout=5000)
                        print(f"✓ Found editor with selector: {selector}")
                        break
                    except:
                        continue
                
                if editor is None:
                    print("Could not find editor")
                    context.close()
                    playwright.stop()
                    continue
                
                # Click to focus
                editor.click()
                time.sleep(1)
                
                # Type content using keyboard (more reliable than fill)
                print("Typing post content...")
                for char in post_content:
                    editor.type(char)
                    time.sleep(random.uniform(0.01, 0.03))
                
                time.sleep(random.uniform(2, 3))
                print("✓ Content entered")
                
                # Find and click Post button
                print("Looking for Post button...")
                
                # Wait for button to appear and be enabled
                time.sleep(3)
                
                post_button = None
                button_selectors = [
                    lambda d: d.get_by_role("button", name=re.compile(r"^Post$", re.IGNORECASE)).first,
                    lambda d: d.locator('button:has-text("Post")').first,
                    lambda d: d.locator('button[aria-label*="Post"]').first,
                ]
                
                for btn_selector in button_selectors:
                    try:
                        post_button = btn_selector(dialog)
                        post_button.wait_for(state='attached', timeout=10000)
                        if post_button.is_enabled():
                            print("✓ Post button found and enabled")
                            break
                    except Exception as e:
                        print(f"Trying next button selector... ({e})")
                        continue
                
                if post_button is None or not post_button.is_enabled():
                    print("Post button not found or not enabled")
                    context.close()
                    playwright.stop()
                    continue
                
                post_button.click()
                print("✓ Post button clicked")
                
                # Wait for post to complete
                time.sleep(random.uniform(5, 8))
                
                # Close dialog if still open
                try:
                    page.keyboard.press("Escape")
                except:
                    pass
                
                print(f"✓ Published successfully: {approval_id}")
                
                # Move to Done folder
                DONE_DIR.mkdir(exist_ok=True)
                approved_file.rename(DONE_DIR / approved_file.name)
                print(f"✓ Moved to Done/: {approved_file.name}")
                
                # Update Dashboard
                dashboard_file = Path("Dashboard.md")
                if dashboard_file.exists():
                    dash_content = dashboard_file.read_text(encoding='utf-8')
                    dash_content += f"\n- [{datetime.now().strftime('%Y-%m-%d %H:%M')}] LinkedIn post published: {approval_id}\n"
                    dashboard_file.write_text(dash_content, encoding='utf-8')
                    print("✓ Dashboard updated")
                
                context.close()
                playwright.stop()
                
            except Exception as e:
                print(f"Error in dialog handling: {e}")
                context.close()
                playwright.stop()
                continue
            
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    publish_post()
