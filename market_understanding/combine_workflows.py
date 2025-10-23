#!/usr/bin/env python3
"""
Combine workflow metadata with actual n8n workflow JSON files.
Creates enriched workflow files with both metadata and n8n workflow definition.
"""
import json
import os
from pathlib import Path

def combine_workflows():
    """Combine metadata and workflow JSON files"""
    
    # Paths
    metadata_dir = Path("workflow_metadata")
    workflows_dir = Path("downloaded_workflows")
    output_dir = Path("combined_workflows")
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Get all metadata files
    metadata_files = list(metadata_dir.glob("workflow_*_enriched.json"))
    
    print(f"Found {len(metadata_files)} metadata files")
    
    success_count = 0
    missing_workflow_count = 0
    error_count = 0
    
    for metadata_file in metadata_files:
        try:
            # Extract workflow ID from filename
            # Format: workflow_0a3e65f3_enriched.json -> 0a3e65f3
            workflow_id = metadata_file.stem.replace("workflow_", "").replace("_enriched", "")
            
            # Find corresponding workflow file
            workflow_file = workflows_dir / f"workflow_{workflow_id}.json"
            
            if not workflow_file.exists():
                print(f"⚠️  Missing workflow file for {workflow_id}")
                missing_workflow_count += 1
                continue
            
            # Load metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Load workflow
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            # Combine them
            combined = metadata.copy()
            combined["n8n_workflow"] = workflow_data
            
            # Save combined file
            output_file = output_dir / f"workflow_{workflow_id}_combined.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(combined, f, indent=2, ensure_ascii=False)
            
            success_count += 1
            
            if success_count % 100 == 0:
                print(f"✓ Processed {success_count} workflows...")
                
        except Exception as e:
            print(f"✗ Error processing {metadata_file.name}: {e}")
            error_count += 1
    
    print(f"\n🎉 Complete!")
    print(f"✓ Successfully combined: {success_count}")
    print(f"⚠️  Missing workflow files: {missing_workflow_count}")
    print(f"✗ Errors: {error_count}")
    print(f"📁 Output directory: {output_dir}")
    
    # Create a summary file
    summary = {
        "total_processed": success_count,
        "missing_workflows": missing_workflow_count,
        "errors": error_count,
        "output_directory": str(output_dir),
        "description": "Combined workflow files containing both metadata and n8n workflow definitions"
    }
    
    with open(output_dir / "summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    return success_count, missing_workflow_count, error_count

if __name__ == "__main__":
    combine_workflows()