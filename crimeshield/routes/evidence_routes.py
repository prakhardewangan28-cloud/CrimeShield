"""
Evidence routes for CRIMESHIELD REST API.
Demonstrates: Flask blueprints, REST API design, and error handling with custom exceptions.
"""

import sqlite3
from flask import Blueprint, request, jsonify
from typing import Dict, Any

from crimeshield.services.evidence_service import EvidenceService
from crimeshield.utils.logger import log_request
from crimeshield.utils.advanced_python import (
    ValidationError,
    NotFoundError,
    DuplicateError,
    InvalidReferenceError
)

# Create a Blueprint for evidence-related routes
evidence_bp = Blueprint('evidence', __name__, url_prefix='/api')

# Initialize service (will be properly initialized in app.py)
evidence_service: EvidenceService = None


def init_evidence_service(db_path, audit_logger=None) -> None:
    """
    Initialize the evidence service with database path and audit logger.
    Called from app.py during application setup.
    """
    global evidence_service
    evidence_service = EvidenceService(db_path, audit_logger)


def validate_evidence_data(data: Dict[str, Any], is_update: bool = False) -> tuple[bool, str]:
    """
    Validate evidence data from API requests.
    
    Args:
        data: Dictionary containing evidence data
        is_update: Whether this is an update operation
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # For create operations, required fields
    if not is_update:
        if not data.get('evidence_code'):
            return False, "evidence_code is required"
        
        if not data.get('case_id'):
            return False, "case_id is required"
        
        if not data.get('evidence_type'):
            return False, "evidence_type is required"
    
    # Validate evidence_code format if provided
    if 'evidence_code' in data:
        evidence_code = data['evidence_code']
        if not isinstance(evidence_code, str) or not evidence_code.strip():
            return False, "evidence_code must be a non-empty string"
        
        if len(evidence_code) > 50:
            return False, "evidence_code must be 50 characters or less"
    
    # Validate case_id if provided
    if 'case_id' in data:
        try:
            case_id = int(data['case_id'])
            if case_id <= 0:
                return False, "case_id must be a positive integer"
        except (ValueError, TypeError):
            return False, "case_id must be a valid integer"
    
    # Validate evidence_type if provided
    if 'evidence_type' in data:
        evidence_type = data['evidence_type']
        if not isinstance(evidence_type, str) or not evidence_type.strip():
            return False, "evidence_type must be a non-empty string"
        
        if len(evidence_type) > 100:
            return False, "evidence_type must be 100 characters or less"
    
    # Validate processing_status if provided
    if 'processing_status' in data:
        status = data['processing_status']
        valid_statuses = ('pending', 'processed', 'flagged')
        if status not in valid_statuses:
            return False, f"processing_status must be one of: {', '.join(valid_statuses)}"
    
    return True, ""


@evidence_bp.route('/evidence', methods=['POST'])
@log_request
def create_evidence() -> tuple[Dict[str, Any], int]:
    """
    Create a new evidence entry.
    Demonstrates: POST endpoint with custom exception handling.
    
    Request body:
        {
            "evidence_code": "EVD-2024-001",
            "case_id": 1,
            "evidence_type": "physical",
            "description": "Description...",
            "location_reference": "Location",
            "person_reference": "Person name",
            "phone_reference": "+1234567890",
            "processing_status": "pending"
        }
    
    Returns:
        JSON response with created evidence or error message
    """
    try:
        # Get JSON data with silent=True to handle invalid JSON gracefully
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
        
        # Validate input data
        is_valid, error_message = validate_evidence_data(data, is_update=False)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Create the evidence using service
        evidence = evidence_service.create_evidence(
            evidence_code=data['evidence_code'],
            case_id=int(data['case_id']),
            evidence_type=data['evidence_type'],
            description=data.get('description'),
            location_reference=data.get('location_reference'),
            person_reference=data.get('person_reference'),
            phone_reference=data.get('phone_reference'),
            processing_status=data.get('processing_status', 'pending')
        )
        
        return jsonify({
            'message': 'Evidence created successfully',
            'evidence': evidence.to_dict()
        }), 201
    
    except InvalidReferenceError as e:
        # Custom exception for invalid case reference
        return jsonify({
            'error': str(e),
            'details': f'Case ID {e.reference_id} does not exist'
        }), 404
    
    except DuplicateError as e:
        # Custom exception for duplicate evidence code
        return jsonify({
            'error': str(e),
            'details': f"Evidence with code '{e.value}' already exists"
        }), 409
    
    except sqlite3.Error as e:
        return jsonify({
            'error': 'Database error occurred',
            'details': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@evidence_bp.route('/evidence', methods=['GET'])
@log_request
def get_evidence() -> tuple[Dict[str, Any], int]:
    """
    Get all evidence or search evidence.
    Demonstrates: GET endpoint with optional query parameters.
    
    Query parameters:
        - evidence_type: Filter by evidence type
        - processing_status: Filter by processing status
        - case_id: Filter by case ID
    
    Returns:
        JSON response with list of evidence
    """
    try:
        # Get query parameters
        evidence_type = request.args.get('evidence_type')
        processing_status = request.args.get('processing_status')
        case_id_str = request.args.get('case_id')
        
        case_id = None
        if case_id_str:
            try:
                case_id = int(case_id_str)
            except ValueError:
                return jsonify({'error': 'case_id must be a valid integer'}), 400
        
        # Search or get all
        if evidence_type or processing_status or case_id:
            evidence_list = evidence_service.search_evidence(
                evidence_type=evidence_type,
                processing_status=processing_status,
                case_id=case_id
            )
        else:
            evidence_list = evidence_service.get_all_evidence()
        
        # Convert to dictionaries using list comprehension
        evidence_dicts = [evidence.to_dict() for evidence in evidence_list]
        
        return jsonify({
            'count': len(evidence_dicts),
            'evidence': evidence_dicts
        }), 200
    
    except sqlite3.Error as e:
        return jsonify({
            'error': 'Database error occurred',
            'details': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@evidence_bp.route('/evidence/<evidence_id>', methods=['GET'])
@log_request
def get_evidence_by_id(evidence_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get a specific evidence entry by ID.
    Demonstrates: GET endpoint with URL parameter.
    
    Args:
        evidence_id: Evidence ID from URL
    
    Returns:
        JSON response with evidence details or error
    """
    try:
        # Validate evidence_id
        try:
            id_int = int(evidence_id)
            if id_int <= 0:
                return jsonify({'error': 'evidence_id must be a positive integer'}), 400
        except ValueError:
            return jsonify({'error': 'evidence_id must be a valid integer'}), 400
        
        # Fetch the evidence
        evidence = evidence_service.get_evidence_by_id(id_int)
        
        if not evidence:
            return jsonify({
                'error': f'Evidence with ID {evidence_id} not found'
            }), 404
        
        return jsonify({
            'evidence': evidence.to_dict()
        }), 200
    
    except sqlite3.Error as e:
        return jsonify({
            'error': 'Database error occurred',
            'details': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@evidence_bp.route('/evidence/<evidence_id>', methods=['PUT'])
@log_request
def update_evidence(evidence_id: str) -> tuple[Dict[str, Any], int]:
    """
    Update an existing evidence entry.
    Demonstrates: PUT endpoint for updates.
    
    Args:
        evidence_id: Evidence ID from URL
    
    Request body (all fields optional):
        {
            "evidence_code": "EVD-2024-001",
            "evidence_type": "digital",
            "description": "Updated description...",
            "location_reference": "New location",
            "person_reference": "Updated person",
            "phone_reference": "+9876543210",
            "processing_status": "processed"
        }
    
    Returns:
        JSON response with updated evidence or error
    """
    try:
        # Validate evidence_id
        try:
            id_int = int(evidence_id)
            if id_int <= 0:
                return jsonify({'error': 'evidence_id must be a positive integer'}), 400
        except ValueError:
            return jsonify({'error': 'evidence_id must be a valid integer'}), 400
        
        # Get JSON data
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
        
        # Validate update data
        is_valid, error_message = validate_evidence_data(data, is_update=True)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Update the evidence
        evidence = evidence_service.update_evidence(
            evidence_id=id_int,
            evidence_code=data.get('evidence_code'),
            evidence_type=data.get('evidence_type'),
            description=data.get('description'),
            location_reference=data.get('location_reference'),
            person_reference=data.get('person_reference'),
            phone_reference=data.get('phone_reference'),
            processing_status=data.get('processing_status')
        )
        
        if not evidence:
            return jsonify({
                'error': f'Evidence with ID {evidence_id} not found'
            }), 404
        
        return jsonify({
            'message': 'Evidence updated successfully',
            'evidence': evidence.to_dict()
        }), 200
    
    except DuplicateError as e:
        return jsonify({
            'error': str(e),
            'details': f"Evidence with code '{e.value}' already exists"
        }), 409
    
    except sqlite3.Error as e:
        return jsonify({
            'error': 'Database error occurred',
            'details': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@evidence_bp.route('/evidence/<evidence_id>', methods=['DELETE'])
@log_request
def delete_evidence(evidence_id: str) -> tuple[Dict[str, Any], int]:
    """
    Delete an evidence entry.
    Demonstrates: DELETE endpoint.
    
    Args:
        evidence_id: Evidence ID from URL
    
    Returns:
        JSON response confirming deletion or error
    """
    try:
        # Validate evidence_id
        try:
            id_int = int(evidence_id)
            if id_int <= 0:
                return jsonify({'error': 'evidence_id must be a positive integer'}), 400
        except ValueError:
            return jsonify({'error': 'evidence_id must be a valid integer'}), 400
        
        # Delete the evidence
        deleted = evidence_service.delete_evidence(id_int)
        
        if not deleted:
            return jsonify({
                'error': f'Evidence with ID {evidence_id} not found'
            }), 404
        
        return jsonify({
            'message': f'Evidence {evidence_id} deleted successfully'
        }), 200
    
    except sqlite3.Error as e:
        return jsonify({
            'error': 'Database error occurred',
            'details': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@evidence_bp.route('/cases/<case_id>/evidence', methods=['GET'])
@log_request
def get_case_evidence(case_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get all evidence belonging to a specific case.
    Demonstrates: Nested resource endpoint.
    
    Args:
        case_id: Case ID from URL
    
    Returns:
        JSON response with list of evidence for the case
    """
    try:
        # Validate case_id
        try:
            id_int = int(case_id)
            if id_int <= 0:
                return jsonify({'error': 'case_id must be a positive integer'}), 400
        except ValueError:
            return jsonify({'error': 'case_id must be a valid integer'}), 400
        
        # Get evidence for the case
        evidence_list = evidence_service.get_evidence_by_case(id_int)
        
        # Convert to dictionaries
        evidence_dicts = [evidence.to_dict() for evidence in evidence_list]
        
        return jsonify({
            'case_id': id_int,
            'count': len(evidence_dicts),
            'evidence': evidence_dicts
        }), 200
    
    except sqlite3.Error as e:
        return jsonify({
            'error': 'Database error occurred',
            'details': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@evidence_bp.route('/evidence/statistics', methods=['GET'])
@log_request
def get_evidence_statistics() -> tuple[Dict[str, Any], int]:
    """
    Get evidence statistics.
    Demonstrates: Statistics endpoint using advanced Python utilities.
    
    Returns:
        JSON response with statistics
    """
    try:
        stats = evidence_service.get_statistics()
        
        return jsonify({
            'statistics': stats
        }), 200
    
    except sqlite3.Error as e:
        return jsonify({
            'error': 'Database error occurred',
            'details': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500
