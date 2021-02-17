""" Schema Validators """
import re
from typing import Any, Dict, List, Optional, Union

from django.utils.dateparse import parse_date, parse_datetime

from openapi_tester import OpenAPISchemaError
from openapi_tester.constants import (
    INVALID_PATTERN_ERROR,
    OPENAPI_PYTHON_MAPPING,
    VALIDATE_ENUM_ERROR,
    VALIDATE_FORMAT_ERROR,
    VALIDATE_MAX_ARRAY_LENGTH_ERROR,
    VALIDATE_MAX_LENGTH_ERROR,
    VALIDATE_MAXIMUM_ERROR,
    VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR,
    VALIDATE_MIN_ARRAY_LENGTH_ERROR,
    VALIDATE_MIN_LENGTH_ERROR,
    VALIDATE_MINIMUM_ERROR,
    VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR,
    VALIDATE_MULTIPLE_OF_ERROR,
    VALIDATE_PATTERN_ERROR,
    VALIDATE_TYPE_ERROR,
    VALIDATE_UNIQUE_ITEMS_ERROR,
)


def validate_enum(schema_section: Dict[str, Any], data: Any) -> Optional[str]:
    enum = schema_section.get("enum")
    if enum and data not in enum:
        return VALIDATE_ENUM_ERROR.format(enum=schema_section["enum"], received=str(data))
    return None


def validate_pattern(schema_section: Dict[str, Any], data: str) -> Optional[str]:
    pattern = schema_section.get("pattern")
    if not pattern:
        return None
    try:
        compiled_pattern = re.compile(pattern)
    except re.error as e:
        raise OpenAPISchemaError(INVALID_PATTERN_ERROR.format(pattern=pattern)) from e
    return None if compiled_pattern.match(data) else VALIDATE_PATTERN_ERROR.format(data=data, pattern=pattern)


def validate_format(schema_section: Dict[str, Any], data: Union[str, bytes, int, float]) -> Optional[str]:
    valid = True
    schema_format = schema_section.get("format")
    if schema_format in ["double", "float"]:
        valid = isinstance(data, float) if data != 0 else isinstance(data, (int, float))
    elif schema_format == "byte":
        valid = isinstance(data, bytes)
    elif schema_format in ["date", "date-time"]:
        parser = parse_date if schema_format == "date" else parse_datetime
        valid = isinstance(data, str) and parser(data) is not None
    return None if valid else VALIDATE_FORMAT_ERROR.format(expected=schema_section["format"], received=str(data))


def validate_openapi_type(schema_section: Dict[str, Any], data: Any) -> Optional[str]:
    valid = True
    schema_type = schema_section.get("type")
    if not schema_type and ("properties" in schema_section or "additionalProperties" in schema_section):
        schema_type = "object"
    if not schema_type:
        return None
    if schema_type in ["file", "string"]:
        valid = isinstance(data, (str, bytes))
    elif schema_type == "boolean":
        valid = isinstance(data, bool)
    elif schema_type == "integer":
        valid = isinstance(data, int) and not isinstance(data, bool)
    elif schema_type == "number":
        valid = isinstance(data, (int, float)) and not isinstance(data, bool)
    elif schema_type == "object":
        valid = isinstance(data, dict)
    elif schema_type == "array":
        valid = isinstance(data, list)

    return (
        None
        if valid
        else VALIDATE_TYPE_ERROR.format(
            expected=OPENAPI_PYTHON_MAPPING[schema_type],
            received=type(data).__name__,
        )
    )


def validate_multiple_of(schema_section: Dict[str, Any], data: Union[int, float]) -> Optional[str]:
    multiple = schema_section.get("multipleOf")
    if multiple and data % multiple != 0:
        return VALIDATE_MULTIPLE_OF_ERROR.format(data=data, multiple=multiple)
    return None


def validate_min_and_max(schema_section: Dict[str, Any], data: Union[int, float]) -> Optional[str]:
    minimum = schema_section.get("minimum")
    maximum = schema_section.get("maximum")
    exclusive_minimum = schema_section.get("exclusiveMinimum")
    exclusive_maximum = schema_section.get("exclusiveMaximum")
    if minimum and exclusive_minimum and data <= minimum:
        return VALIDATE_MINIMUM_ERROR.format(data=data, minimum=minimum + 1)
    if minimum and not exclusive_minimum and data < minimum:
        return VALIDATE_MINIMUM_ERROR.format(data=data, minimum=minimum)
    if maximum and exclusive_maximum and data >= maximum:
        return VALIDATE_MAXIMUM_ERROR.format(data=data, maximum=maximum - 1)
    if maximum and not exclusive_maximum and data > maximum:
        return VALIDATE_MAXIMUM_ERROR.format(data=data, maximum=maximum)
    return None


def validate_unique_items(schema_section: Dict[str, Any], data: List[Any]) -> Optional[str]:
    unique_items = schema_section.get("uniqueItems")
    if unique_items and len(set(data)) != len(data):
        return VALIDATE_UNIQUE_ITEMS_ERROR
    # TODO: handle deep dictionary comparison - for lists of dicts
    return None


def validate_length(schema_section: Dict[str, Any], data: str) -> Optional[str]:
    min_length: Optional[int] = schema_section.get("minLength")
    max_length: Optional[int] = schema_section.get("maxLength")
    if min_length and len(data) < min_length:
        return VALIDATE_MIN_LENGTH_ERROR.format(data=data, min_length=min_length)
    if max_length and len(data) > max_length:
        return VALIDATE_MAX_LENGTH_ERROR.format(data=data, max_length=max_length)
    return None


def validate_array_length(schema_section: Dict[str, Any], data: list) -> Optional[str]:
    min_length: Optional[int] = schema_section.get("minItems")
    max_length: Optional[int] = schema_section.get("maxItems")
    if min_length and len(data) < min_length:
        return VALIDATE_MIN_ARRAY_LENGTH_ERROR.format(data=data, min_length=min_length)
    if max_length and len(data) > max_length:
        return VALIDATE_MAX_ARRAY_LENGTH_ERROR.format(data=data, max_length=max_length)
    return None


def validate_number_of_properties(schema_section: Dict[str, Any], data: dict) -> Optional[str]:
    min_properties: Optional[int] = schema_section.get("minProperties")
    max_properties: Optional[int] = schema_section.get("maxProperties")
    if min_properties and len(data) < min_properties:
        return VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR.format(data=data, min_length=min_properties)
    if max_properties and len(data) > max_properties:
        return VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR.format(data=data, max_length=max_properties)
    return None
