import json
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def validate_json_file(file_path: str) -> bool:
    """
    Validate that a JSON file can be properly loaded.

    Args:
        file_path: Path to the JSON file to validate

    Returns:
        True if file is valid JSON, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error validating {file_path}: {e}")
        return False


def load_json_safe(file_path: str, default: Any = None) -> Optional[Dict]:
    """
    Safely load a JSON file with multiple fallback strategies.

    Args:
        file_path: Path to the JSON file
        default: Default value to return if loading fails

    Returns:
        Loaded JSON data or default value
    """
    if not os.path.exists(file_path):
        logger.warning(f"File not found: {file_path}")
        return default

    # Strategy 1: Try normal loading with strict=False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f, strict=False)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error in {file_path}: {e}")
    except Exception as e:
        logger.warning(f"Error loading {file_path}: {e}")

    # Strategy 2: Try with error-ignoring encoding
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return json.load(f, strict=False)
    except Exception as e:
        logger.warning(f"Failed with ignore errors strategy: {e}")

    # Strategy 3: Try to sanitize and reload
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            # Replace common problematic patterns
            content = sanitize_json_string(content)
            return json.loads(content, strict=False)
    except Exception as e:
        logger.error(f"All strategies failed for {file_path}: {e}")

    return default


def sanitize_json_string(json_string: str) -> str:
    """
    Sanitize a JSON string to fix common Unicode and escape sequence issues.

    Args:
        json_string: The JSON string to sanitize

    Returns:
        Sanitized JSON string
    """
    # Replace null bytes which can cause issues
    json_string = json_string.replace('\x00', '')

    # Fix common escape sequence issues
    # Note: This is a basic implementation and may need refinement
    # based on specific error patterns encountered

    return json_string


def validate_jsonl_file(file_path: str, max_errors: int = 10) -> tuple[bool, list]:
    """
    Validate a JSONL (JSON Lines) file.

    Args:
        file_path: Path to the JSONL file
        max_errors: Maximum number of errors to collect before stopping

    Returns:
        Tuple of (is_valid, list of error line numbers)
    """
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False, []

    error_lines = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue

                try:
                    json.loads(line, strict=False)
                except json.JSONDecodeError as e:
                    error_lines.append(i)
                    logger.debug(f"Line {i} has JSON error: {e}")

                    if len(error_lines) >= max_errors:
                        logger.warning(f"Stopped validation at {max_errors} errors")
                        break
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return False, error_lines

    is_valid = len(error_lines) == 0
    if not is_valid:
        logger.warning(f"Found {len(error_lines)} invalid lines in {file_path}")

    return is_valid, error_lines


def validate_data_directory(data_dir: str) -> Dict[str, Any]:
    """
    Validate all JSON and JSONL files in a data directory.

    Args:
        data_dir: Path to the data directory

    Returns:
        Dictionary with validation results
    """
    if not os.path.exists(data_dir):
        logger.error(f"Data directory does not exist: {data_dir}")
        return {"valid": False, "error": "Directory not found"}

    results = {
        "valid": True,
        "json_files": {"total": 0, "valid": 0, "invalid": []},
        "jsonl_files": {"total": 0, "valid": 0, "invalid": []},
    }

    # Walk through all files in directory
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)

            if file.endswith(".json"):
                results["json_files"]["total"] += 1
                if validate_json_file(file_path):
                    results["json_files"]["valid"] += 1
                else:
                    results["json_files"]["invalid"].append(file_path)
                    results["valid"] = False

            elif file.endswith(".jsonl"):
                results["jsonl_files"]["total"] += 1
                is_valid, error_lines = validate_jsonl_file(file_path)
                if is_valid:
                    results["jsonl_files"]["valid"] += 1
                else:
                    results["jsonl_files"]["invalid"].append({
                        "file": file_path,
                        "error_lines": error_lines
                    })
                    results["valid"] = False

    return results
