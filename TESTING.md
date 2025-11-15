# Testing Guide

## Automated Tests

### Component Tests

Run the component test suite to verify all core functionality:

```bash
python test_system.py
```

This tests:
- ✓ **Policy Scraper**: HTML parsing and content extraction
- ✓ **Change Detector**: State management and change detection logic
- ✓ **Configuration Loading**: YAML parsing and source management

**Expected Output**: All tests should pass (3/3)

## Manual Testing

### 1. Basic Functionality (No API Keys Required)

**Status Check**:
```bash
python main.py status
```

Expected: Shows system status with 8 configured sources

**Help Command**:
```bash
python main.py --help
```

Expected: Displays usage information and examples

### 2. Testing with API Keys

To test the full system including AI summarization:

1. **Set up API key**:
   ```bash
   # Edit .env and add one of:
   ANTHROPIC_API_KEY=your_key_here
   # OR
   OPENAI_API_KEY=your_key_here
   ```

2. **Run a single check**:
   ```bash
   python main.py check
   ```

   This will:
   - Scrape all enabled policy sources
   - Detect any changes (first run establishes baseline)
   - Generate AI summaries of changes
   - Display results in console
   - Save detailed reports to `data/`

3. **Check specific source**:
   ```bash
   python main.py check --source "EU AI Act"
   ```

4. **View status after check**:
   ```bash
   python main.py status
   ```

   Should show:
   - Last check time
   - Number of monitored sources
   - Recent changes

### 3. Testing Change Detection

To verify change detection works:

1. Run an initial check:
   ```bash
   python main.py check
   ```

2. Wait for a policy source to actually update (or modify test data)

3. Run check again:
   ```bash
   python main.py check
   ```

   Changes should be detected and summarized

### 4. Testing Continuous Monitoring

Start the monitor in the background:

```bash
# Terminal 1
python main.py monitor
```

This will:
- Run an initial check immediately
- Schedule checks every 24 hours (configurable)
- Continue running until stopped (Ctrl+C)

## Verification Checklist

After running tests, verify these artifacts exist:

- [ ] `logs/policy_monitor.log` - Application logs
- [ ] `data/policy_state.json` - Current state of all sources
- [ ] `data/policy_changes.json` - Log of detected changes
- [ ] `data/<source>_<timestamp>.txt` - Detailed change reports (if changes detected)

## Expected Behavior

### First Run
- All sources marked as "new"
- Baseline established (content hashes saved)
- No changes reported (nothing to compare against)
- State files created

### Subsequent Runs
- Sources compared against saved state
- Changes detected if content differs
- Summaries generated for changes
- Notifications sent
- State updated

### Network Issues
- Retries up to 3 times (configurable)
- Logs warnings for failed sources
- Continues with other sources
- Doesn't crash on single source failure

### Missing API Keys
- System starts successfully
- Scraping and change detection work normally
- Summarization disabled (logged as warning)
- No summaries generated, but raw content still saved

## Troubleshooting Tests

### Component Tests Fail

**Scraper Test Fails**:
- Verify BeautifulSoup is installed: `pip install beautifulsoup4`
- Check `test_page.html` exists
- Review error message in output

**Change Detector Test Fails**:
- Verify `test_data/` directory is writable
- Check for JSON serialization errors
- Review traceback for specific issue

**Configuration Test Fails**:
- Verify `config.yaml` exists and is valid YAML
- Check for syntax errors in config
- Ensure policy_sources key exists

### Main Program Issues

**Import Errors**:
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Permission Errors**:
```bash
# Ensure directories are writable
chmod 755 data logs archive
```

**Summarization Errors**:
- Verify API key is set in `.env`
- Check API key validity
- Review `logs/policy_monitor.log` for specific errors
- Test API key directly with provider's test script

## Performance Testing

### Memory Usage
Monitor memory during long runs:
```bash
python main.py monitor &
watch -n 5 'ps aux | grep main.py'
```

### Response Time
Check how long sources take to scrape:
```bash
time python main.py check --source "EU AI Act"
```

### State File Growth
Monitor state file sizes:
```bash
ls -lh data/
```

## Test Coverage

Current test coverage:

- **Scraper**: ✓ HTML parsing, ✓ Content extraction, ✗ RSS feeds (optional), ✗ Network requests (environment restricted)
- **Change Detection**: ✓ New source, ✓ No change, ✓ Updated source, ✓ State persistence
- **Configuration**: ✓ YAML loading, ✓ Source parsing, ✓ Settings validation
- **Monitoring**: Manual testing required (integration)
- **Summarization**: Requires API keys (integration)
- **Notifications**: Manual testing required (integration)

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Run component tests
python test_system.py

# Exit code 0 = all passed
# Exit code 1 = failures
```

Add to `.github/workflows/test.yml` or similar.

## Test Data Cleanup

Remove test artifacts:
```bash
# Remove test data
rm -rf test_data/

# Remove test files
rm test_page.html test_system.py

# Reset monitoring state (optional)
rm -rf data/*.json
```

## Reporting Issues

When reporting bugs, include:

1. Python version: `python --version`
2. Installed packages: `pip list`
3. Error messages from `logs/policy_monitor.log`
4. Command that caused the issue
5. Expected vs actual behavior

---

**Last Updated**: 2025-11-15
