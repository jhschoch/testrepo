"""Notification module for policy updates"""

import logging
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional


class Notifier:
    """Sends notifications about policy changes"""

    def __init__(self, config: Dict):
        """
        Initialize the notifier

        Args:
            config: Configuration dictionary with notification settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.email_enabled = config.get('email_enabled', False)
        self.console_enabled = config.get('console_enabled', True)

        # Email settings
        if self.email_enabled:
            self.smtp_server = os.getenv('SMTP_SERVER')
            self.smtp_port = int(os.getenv('SMTP_PORT', 587))
            self.smtp_username = os.getenv('SMTP_USERNAME')
            self.smtp_password = os.getenv('SMTP_PASSWORD')
            self.notification_email = os.getenv('NOTIFICATION_EMAIL')

            if not all([self.smtp_server, self.smtp_username,
                       self.smtp_password, self.notification_email]):
                self.logger.warning("Email settings incomplete, email notifications disabled")
                self.email_enabled = False

    def notify_change(self, change_info: Dict, summary: Optional[str] = None):
        """
        Send notification about a policy change

        Args:
            change_info: Dictionary containing change information
            summary: Optional AI-generated summary
        """
        if self.console_enabled:
            self._notify_console(change_info, summary)

        if self.email_enabled:
            self._notify_email(change_info, summary)

    def notify_digest(self, changes: List[Dict], digest: Optional[str] = None):
        """
        Send a digest notification of multiple changes

        Args:
            changes: List of change information dictionaries
            digest: Optional AI-generated digest
        """
        if self.console_enabled:
            self._notify_console_digest(changes, digest)

        if self.email_enabled:
            self._notify_email_digest(changes, digest)

    def _notify_console(self, change_info: Dict, summary: Optional[str] = None):
        """Print notification to console"""
        source_name = change_info.get('source_name', 'Unknown')
        change_type = change_info.get('change_type', 'update')
        detected_at = change_info.get('detected_at', '')
        content = change_info.get('content', {})
        title = content.get('title', 'No title')
        url = content.get('url', '')

        print("\n" + "=" * 80)
        print(f"🔔 POLICY CHANGE DETECTED")
        print("=" * 80)
        print(f"Source:       {source_name}")
        print(f"Type:         {change_type.upper()}")
        print(f"Title:        {title}")
        print(f"URL:          {url}")
        print(f"Detected:     {detected_at}")
        print("-" * 80)

        if summary:
            print("\nSUMMARY:")
            print(summary)
        else:
            # Show first 500 chars of content
            content_text = content.get('content', '')
            if content_text:
                print("\nCONTENT PREVIEW:")
                print(content_text[:500] + "..." if len(content_text) > 500 else content_text)

        print("=" * 80 + "\n")

    def _notify_console_digest(self, changes: List[Dict], digest: Optional[str] = None):
        """Print digest notification to console"""
        print("\n" + "=" * 80)
        print(f"📊 POLICY UPDATES DIGEST - {datetime.utcnow().strftime('%Y-%m-%d')}")
        print("=" * 80)
        print(f"Total Updates: {len(changes)}\n")

        if digest:
            print("SUMMARY:")
            print(digest)
            print("\n" + "-" * 80 + "\n")

        print("DETAILED UPDATES:")
        for i, change in enumerate(changes, 1):
            source_name = change.get('source_name', 'Unknown')
            change_type = change.get('change_type', 'update')
            content = change.get('content', {})
            title = content.get('title', 'No title')
            url = content.get('url', '')

            print(f"\n{i}. {source_name} ({change_type.upper()})")
            print(f"   Title: {title}")
            print(f"   URL:   {url}")

        print("\n" + "=" * 80 + "\n")

    def _notify_email(self, change_info: Dict, summary: Optional[str] = None):
        """Send email notification"""
        try:
            source_name = change_info.get('source_name', 'Unknown')
            change_type = change_info.get('change_type', 'update')
            content = change_info.get('content', {})
            title = content.get('title', 'No title')
            url = content.get('url', '')

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"AI Governance Policy {change_type.upper()}: {source_name}"
            msg['From'] = self.smtp_username
            msg['To'] = self.notification_email

            # Create email body
            text_body = f"""
AI Governance Policy Change Detected

Source: {source_name}
Type: {change_type.upper()}
Title: {title}
URL: {url}
Detected: {change_info.get('detected_at', '')}

"""
            if summary:
                text_body += f"\nSUMMARY:\n{summary}\n"

            text_body += f"\nView full details: {url}"

            # HTML version
            html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; }}
        .content {{ padding: 20px; }}
        .summary {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🔔 AI Governance Policy {change_type.upper()}</h2>
    </div>
    <div class="content">
        <p><strong>Source:</strong> {source_name}</p>
        <p><strong>Title:</strong> {title}</p>
        <p><strong>Type:</strong> {change_type.upper()}</p>
        <p><strong>URL:</strong> <a href="{url}">{url}</a></p>
        <p><strong>Detected:</strong> {change_info.get('detected_at', '')}</p>
"""
            if summary:
                html_body += f'<div class="summary"><h3>Summary</h3><p>{summary}</p></div>'

            html_body += f"""
        <p><a href="{url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; margin-top: 20px;">View Full Policy</a></p>
        <div class="footer">
            <p>This is an automated notification from the AI Governance Policy Monitor</p>
        </div>
    </div>
</body>
</html>
"""

            # Attach parts
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            self.logger.info(f"Email notification sent for {source_name}")

        except Exception as e:
            self.logger.error(f"Error sending email notification: {str(e)}")

    def _notify_email_digest(self, changes: List[Dict], digest: Optional[str] = None):
        """Send digest email notification"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"AI Governance Policy Digest - {len(changes)} Updates"
            msg['From'] = self.smtp_username
            msg['To'] = self.notification_email

            # Create email body
            text_body = f"AI Governance Policy Digest\n\n"
            text_body += f"Total Updates: {len(changes)}\n\n"

            if digest:
                text_body += f"SUMMARY:\n{digest}\n\n"

            text_body += "UPDATES:\n"
            for i, change in enumerate(changes, 1):
                source_name = change.get('source_name', 'Unknown')
                content = change.get('content', {})
                title = content.get('title', 'No title')
                url = content.get('url', '')
                text_body += f"\n{i}. {source_name}\n   {title}\n   {url}\n"

            # HTML version
            html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .header {{ background-color: #2196F3; color: white; padding: 20px; }}
        .content {{ padding: 20px; }}
        .summary {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; }}
        .update {{ border-left: 3px solid #2196F3; padding-left: 15px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>📊 AI Governance Policy Digest</h2>
        <p>{len(changes)} Updates - {datetime.utcnow().strftime('%Y-%m-%d')}</p>
    </div>
    <div class="content">
"""
            if digest:
                html_body += f'<div class="summary"><h3>Summary</h3><p>{digest}</p></div>'

            html_body += '<h3>Updates</h3>'
            for i, change in enumerate(changes, 1):
                source_name = change.get('source_name', 'Unknown')
                content = change.get('content', {})
                title = content.get('title', 'No title')
                url = content.get('url', '')

                html_body += f"""
        <div class="update">
            <h4>{i}. {source_name}</h4>
            <p><strong>{title}</strong></p>
            <p><a href="{url}">View Policy</a></p>
        </div>
"""

            html_body += """
    </div>
</body>
</html>
"""

            # Attach parts
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            self.logger.info(f"Digest email sent with {len(changes)} updates")

        except Exception as e:
            self.logger.error(f"Error sending digest email: {str(e)}")
