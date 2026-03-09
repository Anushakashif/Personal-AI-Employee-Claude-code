import os
import time
import traceback
from datetime import datetime
from pathlib import Path


class FileWatcher:
    def __init__(self, inbox_dir, needs_action_dir):
        self.inbox_dir = Path(inbox_dir)
        self.needs_action_dir = Path(needs_action_dir)
        self.poll_interval = 2  # Check every 2 seconds
        
        # Create destination directory if it doesn't exist
        self.needs_action_dir.mkdir(parents=True, exist_ok=True)
        
        # Track processed files to avoid duplication
        self.processed_files = set()
        
        # Track file sizes to detect complete writes
        self.file_sizes = {}

    def get_inbox_files(self):
        """Get all files in inbox directory."""
        files = []
        if self.inbox_dir.exists():
            for f in self.inbox_dir.iterdir():
                if f.is_file():
                    files.append(f)
        return files

    def is_file_complete(self, file_path):
        """Check if file write is complete by monitoring size."""
        try:
            current_size = file_path.stat().st_size
            if file_path in self.file_sizes:
                if self.file_sizes[file_path] == current_size:
                    return True
            self.file_sizes[file_path] = current_size
            return False
        except (OSError, FileNotFoundError):
            return False

    def handle_new_file(self, file_path):
        """Process a new file detected in the inbox"""
        try:
            print(f"[WATCHER] New file detected: {file_path.name}")

            # Get file stats
            stat = file_path.stat()
            file_size = stat.st_size
            creation_time = datetime.fromtimestamp(stat.st_ctime)

            # Generate new filename
            original_name = file_path.name
            new_filename = f"FILE_{original_name}.md"
            new_file_path = self.needs_action_dir / new_filename

            # Copy the original file content to the new location with .md extension
            with open(file_path, 'rb') as src:
                with open(new_file_path, 'wb') as dst:
                    dst.write(src.read())

            # Create metadata file with YAML frontmatter
            metadata_filename = f"FILE_{original_name}_metadata.md"
            metadata_path = self.needs_action_dir / metadata_filename

            metadata_content = f"""---
type: file_drop
original_name: "{original_name}"
size: {file_size}
creation_time: "{creation_time.isoformat()}"
detected_at: "{datetime.now().isoformat()}"
original_path: "{file_path.as_posix()}"
---

# Metadata for {original_name}

This file was automatically generated when {original_name} was dropped in the Inbox.

## Details
- Original file: `{original_name}`
- Size: {file_size} bytes
- Creation time: {creation_time.strftime('%Y-%m-%d %H:%M:%S')}
- Detected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write(metadata_content)

            print(f"[WATCHER] Copied {original_name} to {new_filename} and created metadata file")

        except Exception as e:
            print(f"[WATCHER ERROR] Error processing file {file_path}: {str(e)}")
            print(traceback.format_exc())

    def check_for_new_files(self):
        """Poll inbox for new files."""
        files = self.get_inbox_files()
        for file_path in files:
            # Skip already processed files
            if file_path.name in self.processed_files:
                continue
            
            # Check if file write is complete
            if not self.is_file_complete(file_path):
                continue
            
            # Mark as being processed
            self.processed_files.add(file_path.name)
            self.handle_new_file(file_path)

    def run(self):
        """Main watcher loop with polling."""
        print("=" * 60)
        print("File Watcher Started")
        print("=" * 60)
        print(f"Monitoring: {self.inbox_dir}")
        print(f"Destination: {self.needs_action_dir}")
        print(f"Poll interval: {self.poll_interval} seconds")
        print("Press Ctrl+C to stop.")
        print("=" * 60)
        
        # Process existing files on startup
        print("Checking for existing files in Inbox...")
        for existing_file in self.get_inbox_files():
            print(f"  Found: {existing_file.name}")
            self.handle_new_file(existing_file)
            self.processed_files.add(existing_file.name)
        
        print("Starting polling loop...")
        
        try:
            while True:
                self.check_for_new_files()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print("\n\nStopping file watcher...")


def main():
    current_dir = Path.cwd()
    inbox_dir = current_dir / "Inbox"
    needs_action_dir = current_dir / "Needs_Action"
    
    watcher = FileWatcher(inbox_dir, needs_action_dir)
    watcher.run()


if __name__ == "__main__":
    main()
