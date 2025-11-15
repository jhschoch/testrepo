# AI Governance Policy Monitor

An automated system to monitor, detect, and summarize AI governance policy updates from major regulatory bodies and organizations worldwide.

## Features

- **Automated Monitoring**: Continuously monitors multiple AI governance policy sources
- **Change Detection**: Identifies when policies are updated or new policies are published
- **AI-Powered Summarization**: Generates concise summaries of policy changes using Claude or GPT models
- **Multi-Source Support**: Monitors EU AI Act, US Executive Orders, NIST, OECD, UNESCO, ISO, and more
- **Flexible Notifications**: Console output and optional email notifications
- **Configurable**: Easy YAML-based configuration for sources and settings
- **Comprehensive Logging**: Detailed logs of all monitoring activities

## Monitored Sources

The system monitors the following AI governance sources by default:

- **European Union**: EU AI Act, Official AI Strategy Portal
- **United States**: White House AI Executive Orders, NIST AI Risk Management Framework
- **United Kingdom**: UK AI Regulation and Pro-Innovation Approach
- **International**: OECD AI Principles, UNESCO AI Ethics
- **Standards**: ISO/IEC AI Standards

Additional sources can be easily added via the configuration file.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- API key for either OpenAI or Anthropic (for summarization)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd testrepo
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```
   # At least one is required for summarization
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here

   # Optional: Email notifications
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   NOTIFICATION_EMAIL=recipient@example.com
   ```

5. **Review and customize configuration**:

   Edit `config.yaml` to:
   - Enable/disable specific policy sources
   - Add new sources
   - Configure summarization settings
   - Set monitoring intervals
   - Configure notification preferences

## Usage

### Run a Single Check

Check all policy sources once:

```bash
python main.py check
```

Check a specific source:

```bash
python main.py check --source "EU AI Act"
```

### Continuous Monitoring

Run continuous monitoring (checks every 24 hours by default):

```bash
python main.py monitor
```

The monitoring interval can be adjusted in `config.yaml` or via the `CHECK_INTERVAL_HOURS` environment variable.

### View Status

Check the current monitoring status:

```bash
python main.py status
```

This displays:
- Total number of configured sources
- Number of monitored sources
- Recent changes detected
- Last check time for each source

### Test Mode

Run in test mode (scrapes content but doesn't save state):

```bash
python main.py check --test
```

## Configuration

### Adding New Policy Sources

Edit `config.yaml` and add a new source:

```yaml
policy_sources:
  - name: "Your Policy Source"
    url: "https://example.com/ai-policy"
    type: "web"  # or "rss"
    enabled: true
    category: "regulation"  # or "framework", "ethics", "standards"
    region: "US"  # or "EU", "UK", "International"
```

### Configuring Summarization

Choose your AI provider and model in `config.yaml`:

```yaml
summarization:
  provider: "anthropic"  # or "openai"
  model: "claude-3-5-sonnet-20241022"  # or "gpt-4-turbo"
  max_summary_length: 500
  temperature: 0.3
```

### Email Notifications

To enable email notifications:

1. Set email credentials in `.env`
2. Update `config.yaml`:
   ```yaml
   notifications:
     enabled: true
     email_enabled: true
     console_enabled: true
   ```

## Output and Data

### Directory Structure

```
testrepo/
├── data/              # Stored policy states and detailed changes
├── logs/              # Application logs
├── archive/           # Archived old changes
├── src/               # Source code
├── config.yaml        # Configuration file
├── .env               # Environment variables (create from .env.example)
└── main.py            # Main entry point
```

### Stored Data

- **Policy State**: `data/policy_state.json` - Current state and hashes of all monitored policies
- **Changes Log**: `data/policy_changes.json` - Recent changes detected
- **Detailed Changes**: `data/<source>_<timestamp>.txt` - Full content and summaries of changes
- **Application Logs**: `logs/policy_monitor.log` - Detailed execution logs

## How It Works

1. **Scraping**: The system fetches content from configured policy sources (web pages or RSS feeds)

2. **Change Detection**: Content is hashed and compared with previous versions to detect changes

3. **Summarization**: When changes are detected, an AI model generates a concise summary highlighting:
   - Main topic and scope
   - Key requirements or recommendations
   - Important deadlines
   - Affected stakeholders
   - Significant changes from previous versions

4. **Notification**: Changes are reported via:
   - Console output with formatted summaries
   - Email notifications (if configured)
   - Saved detailed reports in the `data/` directory

5. **State Management**: The system maintains state to track which policies have been checked and when changes were detected

## Advanced Usage

### Running as a Service

For production deployment, you can run the monitor as a system service:

#### Linux (systemd)

Create `/etc/systemd/system/ai-policy-monitor.service`:

```ini
[Unit]
Description=AI Governance Policy Monitor
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/testrepo
ExecStart=/path/to/venv/bin/python main.py monitor
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable ai-policy-monitor
sudo systemctl start ai-policy-monitor
```

#### Using cron

Add to crontab to run daily at 9 AM:

```bash
0 9 * * * cd /path/to/testrepo && /path/to/venv/bin/python main.py check
```

### Custom Processing

You can extend the system by modifying the source code:

- **Custom scrapers**: Add new scraping logic in `src/policy_scraper.py`
- **Custom notifications**: Extend `src/notifier.py` for Slack, Discord, etc.
- **Custom analysis**: Modify `src/summarizer.py` for specialized analysis

## Troubleshooting

### Common Issues

**"No API key found"**
- Ensure `.env` file exists and contains valid API keys
- Source the environment: `source .env` or use `python-dotenv`

**"Error scraping source"**
- Check internet connectivity
- Verify the URL is accessible
- Some sites may block automated scrapers - consider adding headers or delays

**"Summarization disabled"**
- Verify API keys are correct
- Check API quota/billing
- Review logs for specific error messages

**"Email notifications not working"**
- Verify SMTP credentials
- For Gmail, use an App Password, not your regular password
- Check firewall/network settings

## Contributing

Contributions are welcome! Areas for improvement:

- Additional policy sources
- Support for more notification channels (Slack, Discord, etc.)
- Enhanced change detection (diff generation)
- Web dashboard for monitoring
- API endpoints for integration

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is for informational purposes only. Always verify policy information from official sources. The AI-generated summaries are meant to assist with understanding but should not replace reading the full policy documents.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Author**: Jason Schoch
**Version**: 1.0.0
**Last Updated**: 2025-11-15
