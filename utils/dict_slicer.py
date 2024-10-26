"""Slicing a nested dictionary by a list of keys.

"""
from typing import Sequence, Dict, Any, Union


def slice_dict(data: Dict, key_paths: Sequence[Sequence[str]]) -> Dict:
    """
    Extract specific nested values from a dictionary based on key paths.

    Args:
        data: The source dictionary to slice
        key_paths: List of key paths, where each path is a list of keys to traverse
                  Example: [["user", "name"], ["user", "address", "city"]]

    Returns:
        A new dictionary containing only the requested paths

    Example:
        data = {
            "user": {
                "name": "John",
                "address": {
                    "city": "New York",
                    "zip": "10001"
                },
                "orders": [1, 2, 3]
            },
            "metadata": {
                "version": "1.0"
            }
        }

        paths = [["user", "name"], ["user", "address", "city"]]
        result = slice_dict(data, paths)
        # Returns: {"user": {"name": "John", "address": {"city": "New York"}}}
    """

    def get_nested_value(d: Dict, path: List[str]) -> Union[Dict, Any]:
        """Helper function to get a value from a nested dictionary."""
        current = d
        for key in path[:-1]:  # All but the last key
            if key not in current:
                return {}
            current = current[key]
            if not isinstance(current, dict):
                return {}

        if path[-1] not in current:  # Check last key
            return {}

        return {path[-1]: current[path[-1]]}

    def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
        """Helper function to deeply merge two dictionaries."""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value
        return result

    def build_nested_dict(path: List[str], value: Any) -> Dict:
        """Helper function to build a nested dictionary from a path and value."""
        if not path:
            return value
        return {path[0]: build_nested_dict(path[1:], value)}

    result = {}
    for path in key_paths:
        if not path:
            continue

        # Get the value for this path
        nested_value = get_nested_value(data, path)
        if not nested_value:
            continue

        # Build the nested structure
        current_dict = build_nested_dict(path[:-1], nested_value)

        # Merge with existing result
        result = merge_dicts(result, current_dict)

    return result
