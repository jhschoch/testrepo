"""Main policy monitoring orchestrator"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .policy_scraper import PolicyScraper
from .change_detector import ChangeDetector
from .summarizer import PolicySummarizer
from .notifier import Notifier


class PolicyMonitor:
    """Orchestrates the monitoring of AI governance policies"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the policy monitor

        Args:
            config_path: Path to configuration file
        """
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)

        # Initialize components
        monitoring_config = self.config.get('monitoring', {})
        self.scraper = PolicyScraper(
            timeout=monitoring_config.get('timeout_seconds', 30),
            max_retries=monitoring_config.get('max_retries', 3)
        )

        storage_config = self.config.get('storage', {})
        self.detector = ChangeDetector(
            data_dir=storage_config.get('data_dir', './data')
        )

        summarization_config = self.config.get('summarization', {})
        try:
            self.summarizer = PolicySummarizer(
                provider=summarization_config.get('provider', 'anthropic'),
                model=summarization_config.get('model'),
                max_length=summarization_config.get('max_summary_length', 500),
                temperature=summarization_config.get('temperature', 0.3)
            )
            self.summarization_enabled = True
        except Exception as e:
            self.logger.warning(f"Summarization not available: {str(e)}")
            self.summarizer = None
            self.summarization_enabled = False

        notification_config = self.config.get('notifications', {})
        self.notifier = Notifier(notification_config)

        self.policy_sources = self.config.get('policy_sources', [])
        self.logger.info(f"Initialized PolicyMonitor with {len(self.policy_sources)} sources")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/policy_monitor.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            raise

    def check_single_source(self, source: Dict) -> Optional[Dict]:
        """
        Check a single policy source for updates

        Args:
            source: Source configuration dictionary

        Returns:
            Change information if change detected, None otherwise
        """
        if not source.get('enabled', True):
            self.logger.debug(f"Source {source['name']} is disabled")
            return None

        source_name = source['name']
        url = source['url']
        source_type = source.get('type', 'web')

        self.logger.info(f"Checking {source_name}...")

        try:
            # Scrape the source
            content = self.scraper.scrape(url, source_type)

            if not content:
                self.logger.warning(f"No content retrieved from {source_name}")
                return None

            # Add source metadata to content
            content['category'] = source.get('category', '')
            content['region'] = source.get('region', '')

            # Detect changes
            change = self.detector.detect_change(source_name, content)

            if change:
                self.logger.info(f"Change detected in {source_name}")

                # Generate summary if enabled
                summary = None
                if self.summarization_enabled and self.summarizer:
                    self.logger.info(f"Generating summary for {source_name}...")
                    summary = self.summarizer.generate_change_summary(change)

                # Send notification
                self.notifier.notify_change(change, summary)

                # Save detailed change information
                self._save_change_details(change, summary)

                return change
            else:
                self.logger.info(f"No changes detected in {source_name}")

        except Exception as e:
            self.logger.error(f"Error checking {source_name}: {str(e)}")

        return None

    def check_all_sources(self) -> List[Dict]:
        """
        Check all configured policy sources

        Returns:
            List of detected changes
        """
        self.logger.info("Starting policy check across all sources...")
        changes = []

        for source in self.policy_sources:
            change = self.check_single_source(source)
            if change:
                changes.append(change)

        self.logger.info(f"Completed check: {len(changes)} changes detected")

        # Generate digest if there are multiple changes
        if len(changes) > 1 and self.summarization_enabled and self.summarizer:
            self.logger.info("Generating digest of all changes...")
            digest = self.summarizer.generate_digest(changes)
            self.notifier.notify_digest(changes, digest)

        return changes

    def _save_change_details(self, change: Dict, summary: Optional[str]):
        """Save detailed change information to file"""
        try:
            storage_config = self.config.get('storage', {})
            data_dir = Path(storage_config.get('data_dir', './data'))
            data_dir.mkdir(parents=True, exist_ok=True)

            source_name = change.get('source_name', 'unknown')
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

            # Safe filename
            safe_name = "".join(c for c in source_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')

            filename = f"{safe_name}_{timestamp}.txt"
            filepath = data_dir / filename

            content = change.get('content', {})

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Source: {source_name}\n")
                f.write(f"Change Type: {change.get('change_type', 'unknown')}\n")
                f.write(f"Detected: {change.get('detected_at', '')}\n")
                f.write(f"URL: {content.get('url', '')}\n")
                f.write(f"Title: {content.get('title', '')}\n")
                f.write(f"\n{'=' * 80}\n")

                if summary:
                    f.write(f"\nAI SUMMARY:\n{summary}\n")
                    f.write(f"\n{'=' * 80}\n")

                f.write(f"\nFULL CONTENT:\n{content.get('content', '')}\n")

            self.logger.info(f"Saved change details to {filepath}")

        except Exception as e:
            self.logger.error(f"Error saving change details: {str(e)}")

    def get_status(self) -> Dict:
        """Get current monitoring status"""
        all_state = self.detector.get_all_sources_state()
        recent_changes = self.detector.get_recent_changes(limit=10)

        return {
            'total_sources': len(self.policy_sources),
            'monitored_sources': len(all_state),
            'recent_changes': len(recent_changes),
            'summarization_enabled': self.summarization_enabled,
            'last_check': max([s.get('last_checked', '') for s in all_state.values()] or ['Never']),
            'sources_state': all_state
        }

    def run_single_check(self):
        """Run a single check of all sources"""
        self.logger.info("=" * 80)
        self.logger.info("AI GOVERNANCE POLICY MONITOR - Single Check")
        self.logger.info("=" * 80)

        changes = self.check_all_sources()

        self.logger.info("=" * 80)
        self.logger.info(f"Check completed: {len(changes)} change(s) detected")
        self.logger.info("=" * 80)

        return changes
