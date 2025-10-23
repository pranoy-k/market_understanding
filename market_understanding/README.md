# n8n Workflow Scraper

A Python-based tool to scrape and download n8n workflow JSON files and metadata from thevibemarketer.com.

## Features

- 🔐 Automated login and session management
- 📥 Bulk download of workflow JSON files
- 📊 Metadata extraction from workflow pages
- 🤖 Browser automation using Playwright

## Project Structure

```
.
├── download_workflows_simple.py    # Download workflow JSON files
├── scrape_workflow_metadata.py     # Scrape workflow metadata
├── data/
│   ├── workflow_urls.json          # List of workflow URLs
│   └── all_workflows_metadata.json # Combined metadata
├── downloaded_workflows/           # Downloaded JSON files (2000+ workflows)
└── workflow_metadata/              # Individual metadata files
```

## Setup

1. Install dependencies:
```bash
pip install playwright
playwright install chromium
```

2. Set environment variables:
```bash
export VIBE_USER="your_email@example.com"
export VIBE_PASS="your_password"
```

Or create a `.env` file (not tracked in git):
```
VIBE_USER=your_email@example.com
VIBE_PASS=your_password
```

## Usage

### Download Workflow JSON Files

```bash
python download_workflows_simple.py
```

This will:
- Login to thevibemarketer.com
- Visit each workflow URL
- Click the "Download Workflow JSON" button
- Save files to `downloaded_workflows/`

### Scrape Workflow Metadata

```bash
python scrape_workflow_metadata.py
```

This will:
- Login to thevibemarketer.com
- Visit each workflow page
- Extract metadata (name, category, difficulty, tools, etc.)
- Save individual JSON files to `workflow_metadata/`
- Create a combined `all_workflows.json` file

## Data

The repository contains:
- **2000+ workflow JSON files** - Complete n8n workflow definitions
- **Workflow metadata** - Structured information about each workflow including:
  - Workflow name and ID
  - Category and difficulty level
  - Tools and integrations used
  - Use cases and benefits
  - Setup time estimates
  - Tags and author information

## Requirements

- Python 3.7+
- playwright
- Valid thevibemarketer.com account

## Security Note

⚠️ Never commit credentials to the repository. Always use environment variables or a `.env` file (which is gitignored).

## License

This project is for educational and research purposes. Please respect the terms of service of thevibemarketer.com.
