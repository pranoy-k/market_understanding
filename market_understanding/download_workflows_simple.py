#!/usr/bin/env python3
"""
Simple script to download n8n workflow JSON files from thevibemarketer.com
Visits each URL and clicks "Download Workflow JSON" button.
"""
import json
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def login(page, email, password):
    """Login to the site"""
    print("Logging in...")
    page.goto("https://www.thevibemarketer.com/members/workflows")
    time.sleep(2)
    
    # Check if already logged in
    if "/members/workflows" in page.url and page.locator("text=Download").count() > 0:
        print("Already logged in!")
        return
    
    # Fill login form
    page.fill("input[type='email']", email)
    page.fill("input[type='password']", password)
    page.press("input[type='password']", "Enter")
    time.sleep(3)
    print("Login successful!")

def download_workflow(page, url, output_dir):
    """Visit URL and download the workflow JSON"""
    try:
        print(f"Visiting: {url}")
        page.goto(url, timeout=30000)
        time.sleep(2)
        
        # Find and click download button
        download_selectors = [
            "text=Download Workflow JSON",
            "a:has-text('Download')",
            "button:has-text('Download')",
        ]
        
        clicked = False
        for selector in download_selectors:
            if page.locator(selector).count() > 0:
                with page.expect_download(timeout=30000) as download_info:
                    page.locator(selector).first.click()
                download = download_info.value
                
                # Save file
                workflow_id = url.split("/")[-1]
                filename = f"workflow_{workflow_id}.json"
                filepath = output_dir / filename
                download.save_as(filepath)
                print(f"✓ Downloaded: {filename}")
                clicked = True
                break
        
        if not clicked:
            print(f"✗ Could not find download button on {url}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error downloading {url}: {e}")
        return False

def main():
    # Configuration
    email = os.environ.get("VIBE_USER")
    password = os.environ.get("VIBE_PASS")
    
    if not email or not password:
        print("Error: Please set VIBE_USER and VIBE_PASS environment variables")
        sys.exit(1)
    
    urls_file = "data/workflow_urls.json"
    output_dir = Path("downloaded_workflows")
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Load URLs
    with open(urls_file, "r") as f:
        urls = json.load(f)
    
    print(f"Found {len(urls)} workflows to download")
    
    # Start browser
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        
        # Login
        login(page, email, password)
        
        # Download each workflow
        success_count = 0
        fail_count = 0
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}]", end=" ")
            if download_workflow(page, url, output_dir):
                success_count += 1
            else:
                fail_count += 1
            
            # Small delay between requests
            time.sleep(1)
        
        browser.close()
    
    print(f"\n\nComplete!")
    print(f"✓ Success: {success_count}")
    print(f"✗ Failed: {fail_count}")
    print(f"Files saved to: {output_dir}")

if __name__ == "__main__":
    main()
