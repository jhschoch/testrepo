#!/usr/bin/env python3
"""
Example: Analyze historical policy changes

This example shows how to access and analyze the stored
policy change data.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.change_detector import ChangeDetector


def main():
    """Analyze stored policy changes"""

    # Initialize the change detector
    detector = ChangeDetector(data_dir='../data')

    # Get recent changes
    recent_changes = detector.get_recent_changes(limit=50)

    if not recent_changes:
        print("\nNo changes recorded yet. Run 'python main.py check' first.\n")
        return

    print("\n" + "=" * 80)
    print("POLICY CHANGE ANALYSIS")
    print("=" * 80)

    # Basic statistics
    print(f"\nTotal Changes Recorded: {len(recent_changes)}")

    # Count changes by source
    source_counts = Counter(c['source_name'] for c in recent_changes)
    print("\nChanges by Source:")
    print("-" * 80)
    for source, count in source_counts.most_common():
        print(f"  {source}: {count}")

    # Count changes by type
    type_counts = Counter(c['change_type'] for c in recent_changes)
    print("\nChanges by Type:")
    print("-" * 80)
    for change_type, count in type_counts.items():
        print(f"  {change_type.upper()}: {count}")

    # Get all sources state
    all_state = detector.get_all_sources_state()

    print("\nMonitored Sources Status:")
    print("-" * 80)
    for source_name, state in all_state.items():
        last_checked = state.get('last_checked', 'Never')
        last_changed = state.get('last_changed', 'Never')

        # Parse dates if available
        if last_checked != 'Never':
            try:
                dt = datetime.fromisoformat(last_checked)
                last_checked = dt.strftime('%Y-%m-%d %H:%M UTC')
            except:
                pass

        print(f"\n  {source_name}:")
        print(f"    Last Checked: {last_checked}")
        print(f"    Last Changed: {last_changed}")

    # Show most recent changes
    print("\n\nMost Recent Changes (Last 5):")
    print("=" * 80)

    for i, change in enumerate(recent_changes[-5:], 1):
        source = change.get('source_name', 'Unknown')
        change_type = change.get('change_type', 'update')
        detected = change.get('detected_at', '')
        title = change.get('title', 'No title')

        print(f"\n{i}. {source} ({change_type.upper()})")
        print(f"   Title: {title}")
        print(f"   Detected: {detected}")

    print("\n" + "=" * 80 + "\n")

    # Show data directory contents
    data_dir = Path('../data')
    if data_dir.exists():
        change_files = list(data_dir.glob('*.txt'))
        if change_files:
            print(f"Detailed change reports available: {len(change_files)} files")
            print(f"Location: {data_dir.absolute()}")
            print("\nRecent files:")
            for f in sorted(change_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                print(f"  - {f.name}")

    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    main()
