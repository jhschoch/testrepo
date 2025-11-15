"""Change detection module for monitoring policy updates"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ChangeDetector:
    """Detects changes in policy content by comparing content hashes"""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / "policy_state.json"
        self.changes_file = self.data_dir / "policy_changes.json"
        self.logger = logging.getLogger(__name__)
        self._load_state()

    def _load_state(self):
        """Load the current state of monitored policies"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading state: {str(e)}")
                self.state = {}
        else:
            self.state = {}

    def _save_state(self):
        """Save the current state of monitored policies"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving state: {str(e)}")

    def detect_change(self, source_name: str, content_data: Dict) -> Optional[Dict]:
        """
        Detect if content has changed from last check

        Args:
            source_name: Name of the policy source
            content_data: Dictionary containing content and metadata

        Returns:
            Dictionary with change information if changed, None otherwise
        """
        current_hash = content_data.get('content_hash')
        if not current_hash:
            self.logger.warning(f"No content hash for {source_name}")
            return None

        # Get previous state
        previous_state = self.state.get(source_name, {})
        previous_hash = previous_state.get('content_hash')

        # First time seeing this source
        if not previous_hash:
            self.logger.info(f"First time monitoring {source_name}")
            self._update_state(source_name, content_data)
            return {
                'source_name': source_name,
                'change_type': 'new',
                'detected_at': datetime.utcnow().isoformat(),
                'content': content_data
            }

        # Check if content has changed
        if current_hash != previous_hash:
            self.logger.info(f"Change detected in {source_name}")
            change_info = {
                'source_name': source_name,
                'change_type': 'updated',
                'detected_at': datetime.utcnow().isoformat(),
                'previous_hash': previous_hash,
                'current_hash': current_hash,
                'previous_check': previous_state.get('last_checked'),
                'content': content_data
            }

            self._update_state(source_name, content_data)
            self._log_change(change_info)
            return change_info

        # No change detected
        self.logger.debug(f"No change detected in {source_name}")
        self._update_state(source_name, content_data, changed=False)
        return None

    def _update_state(self, source_name: str, content_data: Dict, changed: bool = True):
        """Update the state for a policy source"""
        self.state[source_name] = {
            'content_hash': content_data.get('content_hash'),
            'last_checked': datetime.utcnow().isoformat(),
            'last_changed': datetime.utcnow().isoformat() if changed else
                           self.state.get(source_name, {}).get('last_changed'),
            'url': content_data.get('url'),
            'title': content_data.get('title')
        }
        self._save_state()

    def _log_change(self, change_info: Dict):
        """Log a detected change to the changes file"""
        changes = []
        if self.changes_file.exists():
            try:
                with open(self.changes_file, 'r') as f:
                    changes = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading changes log: {str(e)}")

        # Add new change (store minimal info to avoid huge files)
        changes.append({
            'source_name': change_info['source_name'],
            'change_type': change_info['change_type'],
            'detected_at': change_info['detected_at'],
            'current_hash': change_info.get('current_hash'),
            'url': change_info['content'].get('url'),
            'title': change_info['content'].get('title')
        })

        # Keep only last 100 changes
        changes = changes[-100:]

        try:
            with open(self.changes_file, 'w') as f:
                json.dump(changes, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving changes log: {str(e)}")

    def get_recent_changes(self, limit: int = 10) -> List[Dict]:
        """Get recent changes"""
        if not self.changes_file.exists():
            return []

        try:
            with open(self.changes_file, 'r') as f:
                changes = json.load(f)
                return changes[-limit:]
        except Exception as e:
            self.logger.error(f"Error reading changes: {str(e)}")
            return []

    def get_source_state(self, source_name: str) -> Optional[Dict]:
        """Get the current state of a specific source"""
        return self.state.get(source_name)

    def get_all_sources_state(self) -> Dict:
        """Get the state of all monitored sources"""
        return self.state.copy()
