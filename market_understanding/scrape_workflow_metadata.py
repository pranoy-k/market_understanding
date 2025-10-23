#!/usr/bin/env python3
"""
Scrape all workflow metadata from thevibemarketer.com workflow pages
"""
import json
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def login(page, email, password):
    """Login to the site - copied from working download script"""
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

def scrape_workflow_page(page, url):
    """Visit URL and scrape all the metadata"""
    try:
        print(f"Visiting: {url}")
        page.goto(url, timeout=30000)
        time.sleep(2)
        
        workflow_id = url.split("/")[-1]
        metadata = {
            "url": url,
            "workflow_id": workflow_id,
        }
        
        # Get the entire page text content
        try:
            page_text = page.locator("body").inner_text()
            
            # Parse out the fields by looking for labels
            lines = page_text.split("\n")
            
            # Fields to extract
            field_mapping = {
                "Workflow ID": "workflow_id_display",
                "Workflow Name": "workflow_name",
                "Category": "category",
                "Difficulty": "difficulty",
                "Total Nodes": "total_nodes",
                "Tools & Integrations": "tools_integrations",
                "Tags": "tags",
                "Author": "author",
                "Primary Use Case": "primary_use_case",
                "Setup Time": "setup_time",
                "Use Cases": "use_cases",
                "Key Benefits": "key_benefits",
            }
            
            for i, line in enumerate(lines):
                line = line.strip()
                for label, key in field_mapping.items():
                    if line == label and i + 1 < len(lines):
                        value = lines[i + 1].strip()
                        if value:
                            metadata[key] = value
            
            # Store full page text for reference
            metadata["full_page_text"] = page_text
            
        except Exception as e:
            print(f"Error extracting text: {e}")
        
        # Get page title
        try:
            metadata["page_title"] = page.title()
        except:
            pass
        
        # Get page HTML for more detailed parsing if needed
        try:
            metadata["page_html"] = page.content()
        except:
            pass
        
        print(f"✓ Scraped: {metadata.get('workflow_name', workflow_id)}")
        return metadata
        
    except Exception as e:
        print(f"✗ Error scraping {url}: {e}")
        return {
            "url": url,
            "workflow_id": url.split("/")[-1],
            "error": str(e)
        }

def main():
    # Configuration
    email = os.environ.get("VIBE_USER")
    password = os.environ.get("VIBE_PASS")
    
    if not email or not password:
        print("Error: Please set VIBE_USER and VIBE_PASS environment variables")
        import sys
        sys.exit(1)
    
    urls_file = "data/workflow_urls.json"
    output_dir = Path("workflow_metadata")
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Load URLs
    with open(urls_file, "r") as f:
        urls = json.load(f)
    
    print(f"Found {len(urls)} workflows to scrape")
    
    # Start browser
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Login
        login(page, email, password)
        
        # Scrape each workflow
        success_count = 0
        fail_count = 0
        all_metadata = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}]", end=" ")
            metadata = scrape_workflow_page(page, url)
            
            if "error" not in metadata or metadata.get("workflow_name"):
                success_count += 1
            else:
                fail_count += 1
            
            all_metadata.append(metadata)
            
            # Save individual file
            workflow_id = url.split("/")[-1]
            output_file = output_dir / f"workflow_{workflow_id}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Save progress to combined file every 10 workflows
            if i % 10 == 0:
                with open(output_dir / "all_workflows.json", "w", encoding="utf-8") as f:
                    json.dump(all_metadata, f, indent=2, ensure_ascii=False)
                print(f" [Progress saved]")
            
            # Small delay between requests
            time.sleep(1)
        
        # Final save
        with open(output_dir / "all_workflows.json", "w", encoding="utf-8") as f:
            json.dump(all_metadata, f, indent=2, ensure_ascii=False)
        
        browser.close()
    
    print(f"\n\nComplete!")
    print(f"✓ Success: {success_count}")
    print(f"✗ Failed: {fail_count}")
    print(f"Files saved to: {output_dir}")
    print(f"Combined file: {output_dir / 'all_workflows.json'}")

if __name__ == "__main__":
    main()
