"""
Validation utilities for CRIMESHIELD.
Demonstrates: Function design, type hints, and validation logic.
"""

from typing import Dict, Any, Optional, List
from crimeshield.config import VALID_STATUSES


def validate_case_data(data: Dict[str, Any], is_update: bool = False) -> tuple[bool, Optional[str]]:
    """
    Validate case data from API requests.
    Demonstrates: Function with type hints and tuple return.
    
    Args:
        data: Dictionary containing case data
        is_update: Whether this is an update operation (allows partial data)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # For create operations, case_code and title are required
    if not is_update:
        if not data.get('case_code'):
            return False, "case_code is required"
        
        if not data.get('title'):
            return False, "title is required"
    
    # Validate case_code format if provided
    if 'case_code' in data:
        case_code = data['case_code']
        if not isinstance(case_code, str) or not case_code.strip():
            return False, "case_code must be a non-empty string"
        
        if len(case_code) > 50:
            return False, "case_code must be 50 characters or less"
    
    # Validate title if provided
    if 'title' in data:
        title = data['title']
        if not isinstance(title, str) or not title.strip():
            return False, "title must be a non-empty string"
        
        if len(title) > 200:
            return False, "title must be 200 characters or less"
    
    # Validate status if provided
    if 'status' in data:
        is_valid, error = validate_status(data['status'])
        if not is_valid:
            return False, error
    
    # Validate description length if provided
    if 'description' in data and data['description']:
        if not isinstance(data['description'], str):
            return False, "description must be a string"
        
        if len(data['description']) > 2000:
            return False, "description must be 2000 characters or less"
    
    # Validate location length if provided
    if 'location' in data and data['location']:
        if not isinstance(data['location'], str):
            return False, "location must be a string"
        
        if len(data['location']) > 200:
            return False, "location must be 200 characters or less"
    
    return True, None


def validate_status(status: str) -> tuple[bool, Optional[str]]:
    """
    Validate case status value.
    
    Args:
        status: Status string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(status, str):
        return False, "status must be a string"
    
    if status not in VALID_STATUSES:
        valid_statuses = ", ".join(VALID_STATUSES)
        return False, f"status must be one of: {valid_statuses}"
    
    return True, None


def sanitize_search_params(params: Dict[str, Any]) -> Dict[str, str]:
    """
    Sanitize search parameters from query strings.
    Demonstrates: Dictionary comprehension with filtering.
    
    Args:
        params: Raw query parameters
        
    Returns:
        Sanitized parameters dictionary
    """
    allowed_keys = {'title', 'location', 'status'}
    
    # Filter and sanitize using dictionary comprehension
    return {
        key: str(value).strip()
        for key, value in params.items()
        if key in allowed_keys and value
    }


def validate_case_id(case_id: Any) -> tuple[bool, Optional[int], Optional[str]]:
    """
    Validate and convert case ID.
    
    Args:
        case_id: Case ID to validate
        
    Returns:
        Tuple of (is_valid, converted_id, error_message)
    """
    try:
        id_int = int(case_id)
        if id_int <= 0:
            return False, None, "case_id must be a positive integer"
        return True, id_int, None
    except (ValueError, TypeError):
        return False, None, "case_id must be a valid integer"
