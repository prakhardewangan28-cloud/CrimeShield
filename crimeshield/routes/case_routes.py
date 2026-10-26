"""
Case routes for CRIMESHIELD REST API.
Demonstrates: Flask blueprints, REST API design, error handling, and decorators.
"""

import sqlite3
from flask import Blueprint, request, jsonify
from typing import Dict, Any

from crimeshield.services.case_service import CaseService
from crimeshield.utils.validators import (
    validate_case_data,
    sanitize_search_params,
    validate_case_id
)
from crimeshield.utils.logger import log_request
from crimeshield.config import Config

# Create a Blueprint for case-related routes
# Demonstrates: Flask Blueprint for modular route organization
case_bp = Blueprint('cases', __name__, url_prefix='/api')

# Initialize service (will be properly initialized in app.py)
case_service: CaseService = None


def init_case_service(db_path) -> None:
    """
    Initialize the case service with database path.
    Called from app.py during application setup.
    """
    global case_service
    case_service = CaseService(db_path)


@case_bp.route('/health', methods=['GET'])
@log_request  # Demonstrates: Using the decorator we created
def health_check() -> tuple[Dict[str, Any], int]:
    """
    Health check endpoint.
    Demonstrates: Simple API endpoint with JSON response.
    
    Returns:
        JSON response with health status
    """
    return jsonify({
        'status': 'healthy',
        'service': 'CRIMESHIELD API',
        'version': '1.0.0'
    }), 200


@case_bp.route('/cases', methods=['POST'])
@log_request
def create_case() -> tuple[Dict[str, Any], int]:
    """
    Create a new case.
    Demonstrates: POST endpoint with validation and error handling.
    
    Request body:
        {
            "case_code": "CASE-2024-001",
            "title": "Investigation Title",
            "description": "Details...",
            "location": "City",
            "status": "open"
        }
    
    Returns:
        JSON response with created case or error message
    """
    try:
        # Get JSON data from request - silent=True prevents 400 BadRequest exception
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
        
        # Validate input data
        is_valid, error_message = validate_case_data(data, is_update=False)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Create the case using service
        case = case_service.create_case(
            case_code=data['case_code'],
            title=data['title'],
            description=data.get('description'),
            location=data.get('location'),
            status=data.get('status', 'open')
        )
        
        return jsonify({
            'message': 'Case created successfully',
            'case': case.to_dict()
        }), 201
    
    except sqlite3.IntegrityError:
        # Handle duplicate case_code
        return jsonify({
            'error': f"Case with code '{data.get('case_code')}' already exists"
        }), 409
    
    except sqlite3.Error as e:
        # Handle other database errors
        return jsonify({
            'error': 'Database error occurred',
            'details': str(e)
        }), 500
    
    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@case_bp.route('/cases', methods=['GET'])
@log_request
def get_cases() -> tuple[Dict[str, Any], int]:
    """
    Get all cases or search cases.
    Demonstrates: GET endpoint with optional query parameters.
    
    Query parameters:
        - title: Filter by title (partial match)
        - location: Filter by location (partial match)
        - status: Filter by exact status
    
    Returns:
        JSON response with list of cases
    """
    try:
        # Get query parameters and sanitize them
        search_params = sanitize_search_params(request.args.to_dict())
        
        if search_params:
            # Search with filters
            cases = case_service.search_cases(
                title=search_params.get('title'),
                location=search_params.get('location'),
                status=search_params.get('status')
            )
        else:
            # Get all cases
            cases = case_service.get_all_cases()
        
        # Convert cases to dictionaries using list comprehension
        cases_dict = [case.to_dict() for case in cases]
        
        return jsonify({
            'count': len(cases_dict),
            'cases': cases_dict
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


@case_bp.route('/cases/<case_id>', methods=['GET'])
@log_request
def get_case(case_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get a specific case by ID.
    Demonstrates: GET endpoint with URL parameter.
    
    Args:
        case_id: Case ID from URL
    
    Returns:
        JSON response with case details or error
    """
    try:
        # Validate case_id
        is_valid, id_int, error_message = validate_case_id(case_id)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Fetch the case
        case = case_service.get_case_by_id(id_int)
        
        if not case:
            return jsonify({
                'error': f'Case with ID {case_id} not found'
            }), 404
        
        return jsonify({
            'case': case.to_dict()
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


@case_bp.route('/cases/code/<case_code>', methods=['GET'])
@log_request
def get_case_by_code(case_code: str) -> tuple[Dict[str, Any], int]:
    """
    Get a specific case by case code.
    Demonstrates: GET endpoint with URL parameter.
    
    Args:
        case_code: Case code from URL
    
    Returns:
        JSON response with case details or error
    """
    try:
        # Fetch the case
        case = case_service.get_case_by_code(case_code)
        
        if not case:
            return jsonify({
                'error': f'Case with code {case_code} not found'
            }), 404
        
        return jsonify({
            'case': case.to_dict()
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


@case_bp.route('/cases/<case_id>', methods=['PUT'])
@log_request
def update_case(case_id: str) -> tuple[Dict[str, Any], int]:
    """
    Update an existing case.
    Demonstrates: PUT endpoint for updates.
    
    Args:
        case_id: Case ID from URL
    
    Request body (all fields optional):
        {
            "case_code": "CASE-2024-001",
            "title": "Updated Title",
            "description": "Updated details...",
            "location": "Updated City",
            "status": "under_review"
        }
    
    Returns:
        JSON response with updated case or error
    """
    try:
        # Validate case_id
        is_valid, id_int, error_message = validate_case_id(case_id)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Get JSON data with silent=True to handle invalid JSON gracefully
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
        
        # Validate update data
        is_valid, error_message = validate_case_data(data, is_update=True)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Update the case
        case = case_service.update_case(
            case_id=id_int,
            case_code=data.get('case_code'),
            title=data.get('title'),
            description=data.get('description'),
            location=data.get('location'),
            status=data.get('status')
        )
        
        if not case:
            return jsonify({
                'error': f'Case with ID {case_id} not found'
            }), 404
        
        return jsonify({
            'message': 'Case updated successfully',
            'case': case.to_dict()
        }), 200
    
    except sqlite3.IntegrityError:
        # Handle duplicate case_code
        return jsonify({
            'error': f"Case with code '{data.get('case_code')}' already exists"
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


@case_bp.route('/cases/<case_id>', methods=['DELETE'])
@log_request
def delete_case(case_id: str) -> tuple[Dict[str, Any], int]:
    """
    Delete a case.
    Demonstrates: DELETE endpoint.
    
    Args:
        case_id: Case ID from URL
    
    Returns:
        JSON response confirming deletion or error
    """
    try:
        # Validate case_id
        is_valid, id_int, error_message = validate_case_id(case_id)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Delete the case
        deleted = case_service.delete_case(id_int)
        
        if not deleted:
            return jsonify({
                'error': f'Case with ID {case_id} not found'
            }), 404
        
        return jsonify({
            'message': f'Case {case_id} deleted successfully'
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


@case_bp.route('/cases/statistics', methods=['GET'])
@log_request
def get_statistics() -> tuple[Dict[str, Any], int]:
    """
    Get case statistics.
    Demonstrates: Additional utility endpoint.
    
    Returns:
        JSON response with statistics
    """
    try:
        stats = case_service.get_statistics()
        
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
