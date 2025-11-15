#!/usr/bin/env python3
"""Test script to verify the policy monitoring system works"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.policy_scraper import PolicyScraper
from src.change_detector import ChangeDetector

def test_scraper():
    """Test the policy scraper"""
    print("\n" + "=" * 80)
    print("TEST 1: Policy Scraper")
    print("=" * 80)

    # Test with local HTML file
    test_file = "test_page.html"
    print(f"\nTesting scraper with local file...")

    try:
        # Test BeautifulSoup parsing directly
        from bs4 import BeautifulSoup
        import hashlib

        with open(test_file, 'r') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        title = soup.title.string if soup.title else None

        if text and title and 'artificial intelligence' in text.lower():
            print("✓ Scraper successfully parsed HTML content")
            print(f"  - Title: {title}")
            print(f"  - Content length: {len(text)} chars")
            print(f"  - Contains AI keywords: Yes")

            # Test content extraction
            test_scraper = PolicyScraper()
            sections = test_scraper.extract_policy_sections(text)

            if sections and 'relevant_content' in sections:
                print("✓ Policy section extraction works")
                return True

        return False

    except Exception as e:
        print(f"✗ Scraper test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_change_detector():
    """Test the change detector"""
    print("\n" + "=" * 80)
    print("TEST 2: Change Detector")
    print("=" * 80)

    detector = ChangeDetector(data_dir="./test_data")

    # Create test content
    test_content = {
        'content': 'This is test policy content',
        'content_hash': 'abc123',
        'url': 'https://example.com/test',
        'title': 'Test Policy'
    }

    print("\nTesting change detection...")

    try:
        # First check - should detect as "new"
        change1 = detector.detect_change("Test Source", test_content)

        if change1 and change1['change_type'] == 'new':
            print("✓ First check correctly detected as 'new'")
        else:
            print("✗ First check failed")
            return False

        # Second check - same content, should detect no change
        change2 = detector.detect_change("Test Source", test_content)

        if change2 is None:
            print("✓ Second check correctly detected no change")
        else:
            print("✗ Second check incorrectly detected change")
            return False

        # Third check - different content, should detect as "updated"
        test_content['content'] = 'This is updated policy content'
        test_content['content_hash'] = 'def456'
        change3 = detector.detect_change("Test Source", test_content)

        if change3 and change3['change_type'] == 'updated':
            print("✓ Third check correctly detected as 'updated'")
        else:
            print("✗ Third check failed")
            return False

        # Check state retrieval
        state = detector.get_source_state("Test Source")
        if state:
            print("✓ State retrieval works")
            print(f"  - Current hash: {state.get('content_hash')}")

        return True

    except Exception as e:
        print(f"✗ Change detector error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_config_loading():
    """Test configuration loading"""
    print("\n" + "=" * 80)
    print("TEST 3: Configuration Loading")
    print("=" * 80)

    try:
        import yaml

        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        sources = config.get('policy_sources', [])
        print(f"\n✓ Configuration loaded successfully")
        print(f"  - Policy sources configured: {len(sources)}")

        enabled_sources = [s for s in sources if s.get('enabled', True)]
        print(f"  - Enabled sources: {len(enabled_sources)}")

        if enabled_sources:
            print("\n  Sample sources:")
            for source in enabled_sources[:3]:
                print(f"    - {source['name']} ({source.get('region', 'N/A')})")

        return True

    except Exception as e:
        print(f"✗ Configuration loading error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("AI GOVERNANCE POLICY MONITOR - COMPONENT TESTS")
    print("=" * 80)

    results = []

    # Run tests
    results.append(("Scraper", test_scraper()))
    results.append(("Change Detector", test_change_detector()))
    results.append(("Configuration", test_config_loading()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20s} {status}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 80)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 80 + "\n")

    # Cleanup test data
    import shutil
    test_data = Path("test_data")
    if test_data.exists():
        shutil.rmtree(test_data)
        print("Test data cleaned up\n")

    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
