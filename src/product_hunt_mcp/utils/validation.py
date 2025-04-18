"""
Parameter and schema validation utilities
"""

import inspect
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

logger = logging.getLogger("ph_mcp")

# Type variables for function decorators
F = TypeVar("F", bound=Callable[..., Dict[str, Any]])


class ParameterValidator:
    """Handles validation of parameters for MCP tools"""

    @staticmethod
    def validate(
        param_value: Any,
        param_name: str,
        required: bool = False,
        valid_values: List[str] = None,
        min_value: int = None,
        max_value: int = None,
        expected_type: type = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Validate a parameter with various constraints.

        Args:
            param_value: The parameter value to validate
            param_name: Name of the parameter (for error messages)
            required: Whether the parameter is required
            valid_values: List of acceptable values (for enum-like parameters)
            min_value: Minimum acceptable value (for numeric parameters)
            max_value: Maximum acceptable value (for numeric parameters)
            expected_type: Expected type for the parameter

        Returns:
            None if validation passes, or an error dictionary if validation fails
        """
        # Required parameter check
        if required and (param_value is None or param_value == ""):
            return {
                "success": False,
                "error": {"code": "MISSING_PARAMETER", "message": f"{param_name} is required"},
            }

        # Skip other validations if the parameter is None/empty and not required
        if param_value is None or param_value == "":
            return None

        # Type validation if expected_type is provided
        if expected_type is not None and not isinstance(param_value, expected_type):
            type_name = expected_type.__name__
            # Special handling for boolean type
            if expected_type is bool:
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_PARAMETER",
                        "message": f"{param_name} must be a boolean (true or false)",
                    },
                }
            return {
                "success": False,
                "error": {
                    "code": "INVALID_PARAMETER",
                    "message": f"{param_name} must be a {type_name}",
                },
            }

        # Valid values check (enum-like parameters)
        if valid_values is not None and param_value not in valid_values:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_PARAMETER",
                    "message": f"{param_name} must be one of: {', '.join(valid_values)}",
                },
            }

        # Numeric range checks
        if (min_value is not None or max_value is not None) and isinstance(
            param_value, (int, float)
        ):
            error_parts = []

            if min_value is not None and param_value < min_value:
                error_parts.append(f"greater than or equal to {min_value}")

            if max_value is not None and param_value > max_value:
                error_parts.append(f"less than or equal to {max_value}")

            if error_parts:
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_PARAMETER",
                        "message": f"{param_name} must be {' and '.join(error_parts)}",
                    },
                }

        return None

    @staticmethod
    def validate_iso8601_date(date_string: str, param_name: str) -> Optional[Dict[str, Any]]:
        """Validate that a string is in ISO 8601 format"""
        import re

        iso8601_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$"

        if not isinstance(date_string, str):
            return {
                "success": False,
                "error": {
                    "code": "INVALID_PARAMETER",
                    "message": f"{param_name} must be a string in ISO 8601 format (e.g., 2023-01-01T00:00:00Z)",
                },
            }

        if not re.match(iso8601_pattern, date_string):
            return {
                "success": False,
                "error": {
                    "code": "INVALID_DATE_FORMAT",
                    "message": f"{param_name} must be in ISO 8601 format (e.g., 2023-01-01T00:00:00Z)",
                },
            }

        return None

    @staticmethod
    def requires_one_of(params: Dict[str, Any], param_names: List[str]) -> Optional[Dict[str, Any]]:
        """Check that at least one of the given parameters is provided (treat empty string as missing)"""
        if not any(params.get(name) not in (None, "") for name in param_names):
            return {
                "success": False,
                "error": {
                    "code": "MISSING_PARAMETER",
                    "message": f"At least one of {', '.join(param_names)} must be provided",
                },
            }
        return None


class SchemaValidator:
    """Schema-based validator for MCP tool parameters"""

    @staticmethod
    def validate_schema(
        params: Dict[str, Any], schema: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Validate multiple parameters against a schema

        Args:
            params: Dictionary of parameter names and values
            schema: Dictionary mapping parameter names to validation rules

        Returns:
            None if validation passes, or an error dictionary if validation fails
        """
        # Special requirement validation
        if "requires_one_of" in schema:
            param_groups = schema.pop("requires_one_of")
            for group in param_groups:
                error = ParameterValidator.requires_one_of(params, group)
                if error:
                    return error

        # Validate each parameter against its schema
        for param_name, rules in schema.items():
            param_value = params.get(param_name)

            # Skip reserved keys that aren't parameters
            if param_name.startswith("_"):
                continue

            # Extract validation rules
            required = rules.get("required", False)
            valid_values = rules.get("valid_values")
            min_value = rules.get("min_value")
            max_value = rules.get("max_value")
            expected_type = rules.get("type")
            is_iso8601 = rules.get("is_iso8601", False)

            # Handle ISO8601 date validation
            if is_iso8601 and param_value is not None:
                error = ParameterValidator.validate_iso8601_date(param_value, param_name)
                if error:
                    return error
            else:
                # Use existing validator to check each parameter
                error = ParameterValidator.validate(
                    param_value,
                    param_name,
                    required,
                    valid_values,
                    min_value,
                    max_value,
                    expected_type,
                )

                if error:
                    return error

        return None


def validate_with_schema(schema: Dict[str, Dict[str, Any]]):
    """
    Decorator to validate function parameters against a schema.

    Args:
        schema: Dictionary mapping parameter names to validation rules

    Example:
        @validate_with_schema({
            "post_id": {"required": True, "type": str},
            "include_comments": {"type": bool}
        })
        def get_post(post_id, include_comments=False):
            # Function code without validation
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            # Combine positional and keyword arguments
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            all_args = bound_args.arguments

            # Validate against schema
            error = SchemaValidator.validate_schema(all_args, schema)
            if error:
                return error

            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
