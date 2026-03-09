from playwright.sync_api import sync_playwright
import os
import time

SESSION_DIR = "linkedin_session"  # Folder to save cookies/state

os.makedirs(SESSION_DIR, exist_ok=True)

with sync_playwright() as p:
    # Launch persistent context (saves state)
    context = p.chromium.launch_persistent_context(
        user_data_dir=SESSION_DIR,
        headless=False,  # Visible browser so you can log in
        viewport={'width': 1920, 'height': 1080},
        ignore_https_errors=True,
        bypass_csp=True,
    )

    page = context.new_page()
    print("Opening LinkedIn... Please log in manually in the browser window.")
    print("After logging in, wait 10–20 seconds, then press Enter here to save and close.")

    # Navigate with longer timeout and slower navigation
    try:
        page.goto("https://www.linkedin.com/login", timeout=60000, wait_until="domcontentloaded")
    except Exception as e:
        print(f"Navigation warning: {e}")
        print("Trying to continue anyway...")
        page.goto("https://www.linkedin.com", timeout=60000, wait_until="domcontentloaded")

    # Wait for manual login
    input("Press Enter AFTER you are fully logged in and see your feed...")

    # Optional: Go to feed to confirm logged in
    try:
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        time.sleep(5)  # Give time to load
    except Exception as e:
        print(f"Feed navigation warning: {e}")
        print("Session may still be valid, continuing...")

    print("Saving session...")
    context.close()
    print(f"Session saved to: {SESSION_DIR}")
    print("You can now close the browser. Do NOT delete this folder!")