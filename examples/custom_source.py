#!/usr/bin/env python3
"""
Example: How to add and monitor a custom policy source

This example demonstrates how to programmatically add a custom
policy source and monitor it.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.policy_monitor import PolicyMonitor


def main():
    """Monitor a custom AI policy source"""

    # Load environment variables
    load_dotenv()

    # Create a custom source configuration
    custom_source = {
        'name': 'AI Policy Lab - Latest Research',
        'url': 'https://www.aipolicyhub.org/latest',
        'type': 'web',
        'enabled': True,
        'category': 'research',
        'region': 'International'
    }

    # Initialize the monitor (this loads existing config)
    monitor = PolicyMonitor(config_path='../config.yaml')

    # Add the custom source to the monitor
    # In practice, you would add this to config.yaml instead
    monitor.policy_sources.append(custom_source)

    print("\n" + "=" * 80)
    print("CUSTOM SOURCE MONITORING EXAMPLE")
    print("=" * 80)
    print(f"\nMonitoring custom source: {custom_source['name']}")
    print(f"URL: {custom_source['url']}\n")

    # Check the custom source
    change = monitor.check_single_source(custom_source)

    if change:
        print(f"\n✓ Change detected in {custom_source['name']}")
    else:
        print(f"\n✓ No changes detected (baseline established on first run)")

    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    main()
