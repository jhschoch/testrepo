#!/usr/bin/env python3
"""
AI Governance Policy Monitor - Main Entry Point

This tool automatically monitors AI governance policy sources,
detects changes, and generates AI-powered summaries.
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.policy_monitor import PolicyMonitor


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='AI Governance Policy Monitoring and Summarization System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a single check of all policy sources
  python main.py check

  # Check a specific source by name
  python main.py check --source "EU AI Act"

  # Run continuous monitoring (checks every 24 hours by default)
  python main.py monitor

  # View current monitoring status
  python main.py status

  # Run in test mode (scrapes but doesn't save state)
  python main.py check --test
        """
    )

    parser.add_argument(
        'command',
        choices=['check', 'monitor', 'status'],
        help='Command to execute'
    )

    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    parser.add_argument(
        '--source',
        help='Check only a specific source by name'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode - scrape but don\'t save state or send notifications'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)

    try:
        # Initialize monitor
        monitor = PolicyMonitor(config_path=args.config)

        if args.command == 'check':
            # Run single check
            if args.source:
                # Check specific source
                source = next(
                    (s for s in monitor.policy_sources if s['name'] == args.source),
                    None
                )
                if source:
                    print(f"\nChecking: {args.source}\n")
                    monitor.check_single_source(source)
                else:
                    print(f"Error: Source '{args.source}' not found in configuration")
                    sys.exit(1)
            else:
                # Check all sources
                print("\nChecking all policy sources...\n")
                monitor.run_single_check()

        elif args.command == 'monitor':
            # Run continuous monitoring
            print("\nStarting continuous monitoring...")
            print("Press Ctrl+C to stop\n")

            import schedule
            import time

            # Get check interval from environment or config
            interval_hours = int(os.getenv('CHECK_INTERVAL_HOURS',
                                          monitor.config.get('monitoring', {}).get('check_interval_hours', 24)))

            # Schedule regular checks
            schedule.every(interval_hours).hours.do(monitor.run_single_check)

            # Run initial check immediately
            monitor.run_single_check()

            # Keep running
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")

        elif args.command == 'status':
            # Show status
            status = monitor.get_status()

            print("\n" + "=" * 80)
            print("AI GOVERNANCE POLICY MONITOR - STATUS")
            print("=" * 80)
            print(f"Total Sources:          {status['total_sources']}")
            print(f"Monitored Sources:      {status['monitored_sources']}")
            print(f"Recent Changes:         {status['recent_changes']}")
            print(f"Summarization:          {'Enabled' if status['summarization_enabled'] else 'Disabled'}")
            print(f"Last Check:             {status['last_check']}")
            print("\nSource Details:")
            print("-" * 80)

            for source_name, source_state in status['sources_state'].items():
                print(f"\n{source_name}:")
                print(f"  Last Checked:  {source_state.get('last_checked', 'Never')}")
                print(f"  Last Changed:  {source_state.get('last_changed', 'Never')}")
                print(f"  URL:           {source_state.get('url', 'N/A')}")

            print("\n" + "=" * 80 + "\n")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
