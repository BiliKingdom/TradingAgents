#!/usr/bin/env python3
"""
Test script to validate JSON handling fixes for Unicode escape errors.
This script tests the JSON loading functionality without requiring all project dependencies.
"""

import os
import sys
import json
import tempfile
import logging

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_json_validator():
    """Test the JSON validator utility functions."""
    logger.info("Testing JSON validator utility...")

    try:
        from tradingagents.dataflows.json_validator import (
            load_json_safe,
            sanitize_json_string,
            validate_json_file,
            validate_jsonl_file
        )
        logger.info("✓ Successfully imported json_validator module")
    except ImportError as e:
        logger.error(f"✗ Failed to import json_validator: {e}")
        return False

    # Test 1: Create a temporary JSON file with valid content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_valid_json = f.name
        json.dump({"test": "data", "value": 123}, f)

    try:
        # Test loading valid JSON
        data = load_json_safe(temp_valid_json)
        if data and data.get("test") == "data":
            logger.info("✓ Successfully loaded valid JSON file")
        else:
            logger.error("✗ Failed to load valid JSON file correctly")
            return False
    finally:
        os.unlink(temp_valid_json)

    # Test 2: Create a temporary JSON file with problematic content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_problem_json = f.name
        # Write JSON with potential Unicode issues (but still parseable)
        f.write('{"text": "Test\\nwith\\nnewlines", "value": 456}')

    try:
        # Test loading potentially problematic JSON
        data = load_json_safe(temp_problem_json)
        if data and data.get("value") == 456:
            logger.info("✓ Successfully handled JSON with escape sequences")
        else:
            logger.error("✗ Failed to handle JSON with escape sequences")
            return False
    finally:
        os.unlink(temp_problem_json)

    # Test 3: Test with non-existent file
    data = load_json_safe("/nonexistent/file.json", default={"fallback": True})
    if data.get("fallback") is True:
        logger.info("✓ Successfully handled non-existent file with default value")
    else:
        logger.error("✗ Failed to return default value for non-existent file")
        return False

    # Test 4: Create JSONL file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
        temp_jsonl = f.name
        f.write('{"line": 1, "data": "first"}\n')
        f.write('{"line": 2, "data": "second"}\n')
        f.write('{"line": 3, "data": "third"}\n')

    try:
        is_valid, errors = validate_jsonl_file(temp_jsonl)
        if is_valid and len(errors) == 0:
            logger.info("✓ Successfully validated JSONL file")
        else:
            logger.error(f"✗ JSONL validation failed: {errors}")
            return False
    finally:
        os.unlink(temp_jsonl)

    return True


def test_finnhub_utils():
    """Test the finnhub_utils module with updated error handling."""
    logger.info("Testing finnhub_utils module...")

    try:
        from tradingagents.dataflows.finnhub_utils import get_data_in_range
        logger.info("✓ Successfully imported finnhub_utils module")
    except ImportError as e:
        logger.error(f"✗ Failed to import finnhub_utils: {e}")
        return False

    # Test with non-existent data (should return empty dict gracefully)
    result = get_data_in_range(
        ticker="TEST",
        start_date="2024-01-01",
        end_date="2024-12-31",
        data_type="news_data",
        data_dir="/nonexistent/path"
    )

    if result == {}:
        logger.info("✓ finnhub_utils handles missing data gracefully")
    else:
        logger.error("✗ finnhub_utils did not handle missing data correctly")
        return False

    return True


def test_reddit_utils():
    """Test the reddit_utils module with updated error handling."""
    logger.info("Testing reddit_utils module...")

    try:
        from tradingagents.dataflows.reddit_utils import fetch_top_from_category
        logger.info("✓ Successfully imported reddit_utils module")
    except ImportError as e:
        logger.error(f"✗ Failed to import reddit_utils: {e}")
        return False

    # Create a temporary reddit data directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = os.path.join(temp_dir, "test_category")
        os.makedirs(category_dir)

        # Create a test JSONL file
        test_file = os.path.join(category_dir, "test_subreddit.jsonl")
        with open(test_file, 'w', encoding='utf-8') as f:
            # Write some test data
            import time
            current_time = int(time.time())
            f.write(json.dumps({
                "title": "Test post",
                "selftext": "Test content",
                "url": "https://example.com",
                "ups": 100,
                "created_utc": current_time
            }) + '\n')

        try:
            from datetime import datetime
            today = datetime.utcfromtimestamp(current_time).strftime("%Y-%m-%d")

            result = fetch_top_from_category(
                category="test_category",
                date=today,
                max_limit=10,
                data_path=temp_dir
            )

            if isinstance(result, list):
                logger.info("✓ reddit_utils handles data fetching without errors")
            else:
                logger.error("✗ reddit_utils did not return expected result")
                return False
        except Exception as e:
            logger.error(f"✗ reddit_utils raised unexpected error: {e}")
            return False

    return True


def test_config():
    """Test that configuration is properly set up."""
    logger.info("Testing configuration...")

    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        logger.info("✓ Successfully imported DEFAULT_CONFIG")
    except ImportError as e:
        logger.error(f"✗ Failed to import DEFAULT_CONFIG: {e}")
        return False

    # Check that data_dir is now using environment variable or relative path
    data_dir = DEFAULT_CONFIG.get("data_dir")
    if data_dir and not data_dir.startswith("/Users/"):
        logger.info(f"✓ Configuration updated to use flexible data_dir: {data_dir}")
    else:
        logger.warning(f"⚠ data_dir still uses hardcoded path: {data_dir}")

    # Check other essential config values
    if "llm_provider" in DEFAULT_CONFIG:
        logger.info(f"✓ LLM provider configured: {DEFAULT_CONFIG['llm_provider']}")

    if "online_tools" in DEFAULT_CONFIG:
        logger.info(f"✓ Online tools setting: {DEFAULT_CONFIG['online_tools']}")

    return True


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("TradingAgents JSON Handling Fix Validation")
    logger.info("=" * 60)
    logger.info("")

    all_tests = [
        ("JSON Validator", test_json_validator),
        ("FinnHub Utils", test_finnhub_utils),
        ("Reddit Utils", test_reddit_utils),
        ("Configuration", test_config),
    ]

    results = {}
    for test_name, test_func in all_tests:
        logger.info("")
        logger.info(f"Running: {test_name}")
        logger.info("-" * 60)
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"✗ {test_name} raised exception: {e}")
            results[test_name] = False
        logger.info("")

    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info("")
    logger.info(f"Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("✓ All tests passed! JSON handling fixes are working correctly.")
        return 0
    else:
        logger.error("✗ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
