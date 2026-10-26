"""Utility modules for CRIMESHIELD."""

from .validators import validate_case_data, validate_status
from .logger import setup_logger, log_request
from .advanced_python import (
    format_entity_info,
    create_evidence_filter,
    extract_field_values,
    filter_by_status,
    count_by_type,
    EvidenceIterator,
    batch_processor,
    evidence_code_generator,
    ValidationError,
    NotFoundError,
    DuplicateError,
    InvalidReferenceError,
    CrimeshieldException
)

__all__ = [
    'validate_case_data', 'validate_status', 'setup_logger', 'log_request',
    'format_entity_info', 'create_evidence_filter', 'extract_field_values',
    'filter_by_status', 'count_by_type', 'EvidenceIterator', 'batch_processor',
    'evidence_code_generator', 'ValidationError', 'NotFoundError', 
    'DuplicateError', 'InvalidReferenceError', 'CrimeshieldException'
]
