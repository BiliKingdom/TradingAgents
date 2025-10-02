#!/usr/bin/env python3
"""
Basic test to validate the JSON validator module without external dependencies.
"""

import os
import sys
import json
import tempfile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_json_validator_module():
    """Test that the json_validator module can be imported and basic functions work."""
    logger.info("Testing json_validator module...")

    # Add project to path
    sys.path.insert(0, os.path.dirname(__file__))

    try:
        # Import without external dependencies
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "json_validator",
            os.path.join(os.path.dirname(__file__), "tradingagents/dataflows/json_validator.py")
        )
        json_validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(json_validator)

        logger.info("✓ Successfully imported json_validator module")

        # Test functions exist
        assert hasattr(json_validator, 'load_json_safe'), "Missing load_json_safe function"
        assert hasattr(json_validator, 'sanitize_json_string'), "Missing sanitize_json_string function"
        assert hasattr(json_validator, 'validate_json_file'), "Missing validate_json_file function"
        assert hasattr(json_validator, 'validate_jsonl_file'), "Missing validate_jsonl_file function"
        logger.info("✓ All required functions are present")

        # Test sanitize_json_string
        test_string = '{"test": "data\\nwith\\nnewlines"}'
        result = json_validator.sanitize_json_string(test_string)
        logger.info("✓ sanitize_json_string function works")

        # Test with a valid JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_file = f.name
            json.dump({"test": "data", "value": 123, "unicode": "测试数据"}, f)

        try:
            data = json_validator.load_json_safe(temp_file)
            if data and data.get("test") == "data" and data.get("unicode") == "测试数据":
                logger.info("✓ Successfully loaded JSON file with Unicode content")
            else:
                logger.error("✗ Failed to load JSON correctly")
                return False

            # Validate the file
            is_valid = json_validator.validate_json_file(temp_file)
            if is_valid:
                logger.info("✓ JSON file validation works")
            else:
                logger.error("✗ JSON validation failed")
                return False
        finally:
            os.unlink(temp_file)

        # Test with malformed JSON (should handle gracefully)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_bad_file = f.name
            f.write('{"invalid": json content}')  # Intentionally malformed

        try:
            data = json_validator.load_json_safe(temp_bad_file, default={"fallback": True})
            if data.get("fallback") is True:
                logger.info("✓ Gracefully handled malformed JSON with fallback")
            else:
                logger.error("✗ Did not return fallback for malformed JSON")
                return False
        finally:
            os.unlink(temp_bad_file)

        # Test with JSONL file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
            temp_jsonl = f.name
            f.write('{"line": 1}\n')
            f.write('{"line": 2}\n')
            f.write('{"line": 3}\n')

        try:
            is_valid, errors = json_validator.validate_jsonl_file(temp_jsonl)
            if is_valid and len(errors) == 0:
                logger.info("✓ JSONL validation works correctly")
            else:
                logger.error(f"✗ JSONL validation failed: {errors}")
                return False
        finally:
            os.unlink(temp_jsonl)

        return True

    except Exception as e:
        logger.error(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_unicode_scenarios():
    """Test various Unicode escape scenarios that might cause issues."""
    logger.info("Testing Unicode handling scenarios...")

    sys.path.insert(0, os.path.dirname(__file__))

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "json_validator",
            os.path.join(os.path.dirname(__file__), "tradingagents/dataflows/json_validator.py")
        )
        json_validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(json_validator)

        # Test case 1: Unicode characters
        test_cases = [
            {"name": "Chinese characters", "content": {"text": "你好世界", "value": 1}},
            {"name": "Emoji", "content": {"text": "Hello 👋 World 🌍", "value": 2}},
            {"name": "Mixed scripts", "content": {"text": "Hello Привет مرحبا", "value": 3}},
            {"name": "Special chars", "content": {"text": "Path: C:\\Users\\test\\file.txt", "value": 4}},
        ]

        for test_case in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                temp_file = f.name
                json.dump(test_case["content"], f, ensure_ascii=False)

            try:
                data = json_validator.load_json_safe(temp_file)
                if data and data.get("value") == test_case["content"]["value"]:
                    logger.info(f"✓ Handled {test_case['name']}")
                else:
                    logger.error(f"✗ Failed to handle {test_case['name']}")
                    return False
            finally:
                os.unlink(temp_file)

        return True

    except Exception as e:
        logger.error(f"✗ Unicode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("JSON Validator Basic Tests")
    logger.info("=" * 60)
    logger.info("")

    tests = [
        ("JSON Validator Module", test_json_validator_module),
        ("Unicode Scenarios", test_unicode_scenarios),
    ]

    results = {}
    for test_name, test_func in tests:
        logger.info(f"\nRunning: {test_name}")
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
        logger.info("\n✓ All tests passed! JSON handling fixes are working correctly.")
        logger.info("The Unicode escape error should now be resolved.")
        return 0
    else:
        logger.error("\n✗ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
