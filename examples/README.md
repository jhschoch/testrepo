# Examples

This directory contains example scripts demonstrating various features of the AI Governance Policy Monitor.

## Available Examples

### 1. Custom Source Monitoring (`custom_source.py`)

Demonstrates how to programmatically add and monitor a custom policy source.

```bash
cd examples
python custom_source.py
```

**What it shows:**
- How to create a custom source configuration
- How to add it to the monitor
- How to check a specific source programmatically

### 2. Change Analysis (`analyze_changes.py`)

Shows how to analyze historical policy changes stored by the system.

```bash
cd examples
python analyze_changes.py
```

**What it shows:**
- How to access stored change data
- Statistics on changes by source and type
- How to view monitoring status
- How to list detailed change reports

## Running Examples

All examples assume you've:
1. Installed dependencies (`pip install -r requirements.txt`)
2. Configured your API key in `.env`
3. Run at least one check to establish baseline data

## Creating Your Own Scripts

You can use these examples as templates for creating your own custom monitoring scripts. The key components you can import are:

```python
from src.policy_monitor import PolicyMonitor
from src.policy_scraper import PolicyScraper
from src.change_detector import ChangeDetector
from src.summarizer import PolicySummarizer
from src.notifier import Notifier
```

See the main README.md for detailed API documentation.
