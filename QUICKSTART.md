# Quick Start Guide

Get up and running with the AI Governance Policy Monitor in 5 minutes.

## Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Configure API Key

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# You need either ANTHROPIC_API_KEY or OPENAI_API_KEY
```

Example `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
# OR
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

## Step 3: Run Your First Check

```bash
python main.py check
```

This will:
1. Check all configured AI governance policy sources
2. Detect any changes since last run
3. Generate AI summaries of changes
4. Display results in the console

## Step 4: Check the Results

After the first run, you'll see:

- **Console output**: Summary of what was found
- **Data files**: Created in `data/` directory
  - `policy_state.json`: Current state of all sources
  - `policy_changes.json`: Log of changes
  - Individual change files with full details

## Step 5: View Status

```bash
python main.py status
```

This shows:
- How many sources are being monitored
- When each source was last checked
- Recent changes detected

## Next Steps

### Configure Sources

Edit `config.yaml` to:
- Enable/disable specific sources
- Add your own policy sources
- Adjust monitoring frequency

### Enable Continuous Monitoring

```bash
python main.py monitor
```

This runs continuously, checking sources every 24 hours (configurable).

### Set Up Email Notifications

1. Edit `.env` with SMTP settings:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   NOTIFICATION_EMAIL=recipient@example.com
   ```

2. Edit `config.yaml`:
   ```yaml
   notifications:
     email_enabled: true
   ```

3. Run check:
   ```bash
   python main.py check
   ```

### Run as a Daily Cron Job

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/testrepo && /path/to/venv/bin/python main.py check
```

## Example Output

When changes are detected, you'll see output like:

```
================================================================================
🔔 POLICY CHANGE DETECTED
================================================================================
Source:       EU AI Act
Type:         UPDATED
Title:        European Parliament adopts AI Act amendments
URL:          https://artificialintelligenceact.eu/latest-updates/
Detected:     2025-11-15T10:30:00
--------------------------------------------------------------------------------

SUMMARY:
The European Parliament has adopted significant amendments to the AI Act,
strengthening transparency requirements for high-risk AI systems. Key changes
include mandatory disclosure of AI-generated content, enhanced oversight for
general-purpose AI models, and revised timelines for compliance. Organizations
deploying high-risk AI systems must now conduct more rigorous conformity
assessments. The amendments affect AI providers across all member states,
with new compliance deadlines set for Q2 2026.

================================================================================
```

## Common Commands

```bash
# Check all sources once
python main.py check

# Check a specific source
python main.py check --source "EU AI Act"

# View current status
python main.py status

# Run continuous monitoring
python main.py monitor

# Get help
python main.py --help
```

## Troubleshooting

**Problem**: "API key not found"
- **Solution**: Make sure `.env` file exists and contains your API key

**Problem**: No changes detected on first run
- **Solution**: This is normal! The system establishes a baseline on first run. Changes will be detected on subsequent runs.

**Problem**: "Error scraping source"
- **Solution**: Check your internet connection and verify the source URL is accessible

## Getting Help

- Check the full [README.md](README.md) for detailed documentation
- Review `logs/policy_monitor.log` for detailed error messages
- Open an issue on GitHub for bug reports or questions

Happy monitoring!
