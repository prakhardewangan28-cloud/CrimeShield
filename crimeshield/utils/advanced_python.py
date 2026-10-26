"""
Advanced Python concepts module for CRIMESHIELD.
Demonstrates practical usage of advanced Python features.
"""

from typing import Callable, Any, Iterable, TypeVar, Optional, List, Dict
from functools import reduce, wraps
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


# ============================================================================
# 1. *args and **kwargs - Variable Arguments
# ============================================================================

def format_entity_info(*args: Any, **kwargs: Any) -> str:
    """
    Format entity information with flexible arguments.
    Demonstrates: *args (positional) and **kwargs (keyword arguments).
    
    Used in: Audit logging for flexible log message formatting.
    
    Args:
        *args: Variable positional arguments
        **kwargs: Variable keyword arguments
        
    Returns:
        Formatted string with all arguments
        
    Example:
        >>> format_entity_info("Case", "Evidence", action="created", id=123)
        "Args: Case, Evidence | Keywords: action=created, id=123"
    """
    args_str = ", ".join(str(arg) for arg in args)
    kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    
    result_parts = []
    if args_str:
        result_parts.append(f"Args: {args_str}")
    if kwargs_str:
        result_parts.append(f"Keywords: {kwargs_str}")
    
    return " | ".join(result_parts) if result_parts else "No arguments"


def create_audit_entry(entity_type: str, entity_id: int, *actions: str, **metadata: Any) -> Dict[str, Any]:
    """
    Create an audit entry with flexible action and metadata.
    Demonstrates: Practical use of *args and **kwargs.
    
    Used in: Audit logging system for flexible log entries.
    
    Args:
        entity_type: Type of entity (case, evidence)
        entity_id: ID of the entity
        *actions: Variable number of actions performed
        **metadata: Additional metadata fields
        
    Returns:
        Dictionary representing audit entry
    """
    return {
        'entity_type': entity_type,
        'entity_id': entity_id,
        'actions': list(actions),
        'metadata': metadata,
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# 2. Higher-Order Functions - Functions that take/return functions
# ============================================================================

def apply_transformation(data: List[T], transformer: Callable[[T], T]) -> List[T]:
    """
    Apply a transformation function to all items in a list.
    Demonstrates: Higher-order function (takes function as parameter).
    
    Used in: Data processing pipelines for evidence and case data.
    
    Args:
        data: List of items to transform
        transformer: Function to apply to each item
        
    Returns:
        List of transformed items
    """
    return [transformer(item) for item in data]


def create_validator(field_name: str, max_length: int) -> Callable[[str], bool]:
    """
    Create a validation function for a specific field.
    Demonstrates: Higher-order function (returns a function).
    
    Used in: Dynamic validator creation for different evidence types.
    
    Args:
        field_name: Name of field being validated
        max_length: Maximum allowed length
        
    Returns:
        Validation function
    """
    def validator(value: str) -> bool:
        """Validate that value meets length requirement."""
        is_valid = len(value) <= max_length
        if not is_valid:
            logger.warning(f"{field_name} exceeds max length of {max_length}")
        return is_valid
    
    return validator


# ============================================================================
# 3. Closures - Inner functions that capture outer function variables
# ============================================================================

def create_evidence_filter(evidence_type: str, status: str) -> Callable[[Dict[str, Any]], bool]:
    """
    Create a filter function that captures specific criteria.
    Demonstrates: Closure - inner function accessing outer function variables.
    
    Used in: Evidence filtering and search operations.
    
    Args:
        evidence_type: Type of evidence to filter
        status: Processing status to filter
        
    Returns:
        Filter function that checks if evidence matches criteria
    """
    def filter_func(evidence: Dict[str, Any]) -> bool:
        """Filter function with captured criteria (closure)."""
        # Access evidence_type and status from outer scope
        return (
            evidence.get('evidence_type') == evidence_type and
            evidence.get('processing_status') == status
        )
    
    return filter_func


def counter(start: int = 0) -> Callable[[], int]:
    """
    Create a counter function with encapsulated state.
    Demonstrates: Closure maintaining state across calls.
    
    Used in: Evidence code generation with incremental counters.
    
    Args:
        start: Starting value for counter
        
    Returns:
        Function that returns next count on each call
    """
    count = start
    
    def increment() -> int:
        """Return and increment counter (closure with mutable state)."""
        nonlocal count  # Allows modification of outer variable
        count += 1
        return count
    
    return increment


# ============================================================================
# 4. map() - Apply function to all items in iterable
# ============================================================================

def extract_field_values(items: List[Dict[str, Any]], field: str) -> List[Any]:
    """
    Extract a specific field from all items using map().
    Demonstrates: map() for applying function to iterable.
    
    Used in: Extracting case IDs, evidence codes, or other fields from collections.
    
    Args:
        items: List of dictionaries
        field: Field name to extract
        
    Returns:
        List of field values
    """
    return list(map(lambda item: item.get(field), items))


def normalize_evidence_codes(codes: List[str]) -> List[str]:
    """
    Normalize evidence codes to uppercase using map().
    Demonstrates: map() with built-in function.
    
    Used in: Evidence code standardization before database operations.
    
    Args:
        codes: List of evidence codes
        
    Returns:
        List of normalized codes
    """
    return list(map(str.upper, codes))


# ============================================================================
# 5. filter() - Filter items based on condition
# ============================================================================

def filter_by_status(items: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    """
    Filter items by status using filter().
    Demonstrates: filter() with lambda function.
    
    Used in: Filtering cases or evidence by processing status.
    
    Args:
        items: List of items with 'status' or 'processing_status' field
        field: Status value to filter by
        
    Returns:
        Filtered list of items
    """
    return list(filter(
        lambda item: item.get('status') == status or item.get('processing_status') == status,
        items
    ))


def filter_active_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter items that are not closed/processed.
    Demonstrates: filter() with custom condition.
    
    Used in: Finding active cases and pending evidence.
    
    Args:
        items: List of items
        
    Returns:
        List of active items
    """
    def is_active(item: Dict[str, Any]) -> bool:
        """Check if item is active."""
        status = item.get('status') or item.get('processing_status')
        return status not in ('closed', 'processed')
    
    return list(filter(is_active, items))


# ============================================================================
# 6. functools.reduce() - Reduce iterable to single value
# ============================================================================

def count_by_type(items: List[Dict[str, Any]], type_field: str = 'evidence_type') -> Dict[str, int]:
    """
    Count items by type using reduce().
    Demonstrates: functools.reduce() for aggregation.
    
    Used in: Statistics generation for evidence types, case statuses.
    
    Args:
        items: List of items with type field
        type_field: Name of the field containing type
        
    Returns:
        Dictionary with counts per type
    """
    def accumulator(counts: Dict[str, int], item: Dict[str, Any]) -> Dict[str, int]:
        """Accumulator function for reduce."""
        item_type = item.get(type_field, 'unknown')
        counts[item_type] = counts.get(item_type, 0) + 1
        return counts
    
    return reduce(accumulator, items, {})


def calculate_total_count(items: List[Dict[str, Any]]) -> int:
    """
    Calculate total count using reduce().
    Demonstrates: reduce() for simple aggregation.
    
    Args:
        items: List of items
        
    Returns:
        Total count
    """
    return reduce(lambda count, item: count + 1, items, 0)


# ============================================================================
# 7. Iterators - Objects that can be iterated over
# ============================================================================

class EvidenceIterator:
    """
    Custom iterator for evidence items.
    Demonstrates: Iterator protocol with __iter__ and __next__.
    
    Used in: Batch processing of evidence records.
    """
    
    def __init__(self, evidence_list: List[Dict[str, Any]]) -> None:
        """
        Initialize iterator.
        
        Args:
            evidence_list: List of evidence dictionaries
        """
        self._evidence = evidence_list
        self._index = 0
    
    def __iter__(self):
        """Return iterator object (self)."""
        return self
    
    def __next__(self) -> Dict[str, Any]:
        """
        Return next item or raise StopIteration.
        Demonstrates: __next__ method for iteration protocol.
        """
        if self._index >= len(self._evidence):
            raise StopIteration
        
        evidence = self._evidence[self._index]
        self._index += 1
        return evidence
    
    def reset(self) -> None:
        """Reset iterator to beginning."""
        self._index = 0


# ============================================================================
# 8. Generators - Functions that yield values (lazy iteration)
# ============================================================================

def batch_processor(items: List[T], batch_size: int = 10):
    """
    Generator that yields items in batches.
    Demonstrates: Generator with yield for memory-efficient batch processing.
    
    Used in: Processing large numbers of evidence items without loading all into memory.
    
    Args:
        items: List of items to process
        batch_size: Size of each batch
        
    Yields:
        Batches of items
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def evidence_code_generator(prefix: str, start: int = 1):
    """
    Generator for creating evidence codes.
    Demonstrates: Infinite generator with yield.
    
    Used in: Auto-generating unique evidence codes.
    
    Args:
        prefix: Prefix for evidence codes
        start: Starting number
        
    Yields:
        Evidence codes in sequence
    """
    counter = start
    while True:
        yield f"{prefix}-{counter:06d}"
        counter += 1


def filtered_items_generator(items: Iterable[Dict[str, Any]], condition: Callable[[Dict[str, Any]], bool]):
    """
    Generator that yields items matching condition.
    Demonstrates: Generator with filtering (lazy evaluation).
    
    Used in: Memory-efficient filtering of large datasets.
    
    Args:
        items: Iterable of items
        condition: Filter condition function
        
    Yields:
        Items that match the condition
    """
    for item in items:
        if condition(item):
            yield item


# ============================================================================
# 9. Custom Exceptions - Domain-specific error handling
# ============================================================================

class CrimeshieldException(Exception):
    """
    Base exception for CRIMESHIELD application.
    Demonstrates: Custom exception hierarchy.
    """
    pass


class ValidationError(CrimeshieldException):
    """
    Exception raised for validation errors.
    Used in: Input validation for evidence and cases.
    """
    pass


class NotFoundError(CrimeshieldException):
    """
    Exception raised when an entity is not found.
    Used in: Service layer when retrieving non-existent records.
    """
    def __init__(self, entity_type: str, entity_id: Any):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with ID {entity_id} not found")


class DuplicateError(CrimeshieldException):
    """
    Exception raised when attempting to create duplicate entity.
    Used in: Preventing duplicate case codes or evidence codes.
    """
    def __init__(self, entity_type: str, field: str, value: Any):
        self.entity_type = entity_type
        self.field = field
        self.value = value
        super().__init__(f"{entity_type} with {field}='{value}' already exists")


class InvalidReferenceError(CrimeshieldException):
    """
    Exception raised when referencing non-existent entity.
    Used in: Evidence creation with invalid case_id.
    """
    def __init__(self, referenced_entity: str, reference_id: Any):
        self.referenced_entity = referenced_entity
        self.reference_id = reference_id
        super().__init__(f"Referenced {referenced_entity} with ID {reference_id} does not exist")


# ============================================================================
# Utility Functions Using Multiple Concepts
# ============================================================================

def process_evidence_batch(evidence_list: List[Dict[str, Any]], 
                          *transformers: Callable[[Dict[str, Any]], Dict[str, Any]],
                          **options: Any) -> List[Dict[str, Any]]:
    """
    Process evidence batch with multiple transformers.
    Demonstrates: Combining *args, **kwargs, map, and higher-order functions.
    
    Args:
        evidence_list: List of evidence dictionaries
        *transformers: Functions to apply to each evidence item
        **options: Processing options
        
    Returns:
        Processed evidence list
    """
    result = evidence_list
    
    # Apply each transformer function
    for transformer in transformers:
        result = list(map(transformer, result))
    
    # Apply batch size limit if specified
    if 'limit' in options:
        result = result[:options['limit']]
    
    return result
