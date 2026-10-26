"""
Analysis and connection routes for CRIMESHIELD REST API.
Demonstrates: REST API for connection analysis and review workflows.
"""

import sqlite3
from flask import Blueprint, request, jsonify
from typing import Dict, Any

from crimeshield.services.analysis_service import AnalysisService, AnalysisException
from crimeshield.services.connection_service import ConnectionService
from crimeshield.utils.logger import log_request
from crimeshield.utils.connection_graph import build_graph_from_connections

# Create a Blueprint for analysis-related routes
analysis_bp = Blueprint('analysis', __name__, url_prefix='/api')

# Initialize services (will be properly initialized in app.py)
analysis_service: AnalysisService = None
connection_service: ConnectionService = None


def init_analysis_services(db_path, audit_logger=None) -> None:
    """
    Initialize analysis and connection services.
    Called from app.py during application setup.
    """
    global analysis_service, connection_service
    analysis_service = AnalysisService(db_path, audit_logger)
    connection_service = ConnectionService(db_path, audit_logger)


@analysis_bp.route('/analysis/run', methods=['POST'])
@log_request
def run_analysis() -> tuple[Dict[str, Any], int]:
    """
    Run connection analysis on all evidence.
    Demonstrates: POST endpoint for triggering analysis.
    
    IMPORTANT: In production, this endpoint must require authentication
    and authorization. This is a college mini-project demonstration.
    
    Request body (optional):
        {
            "batch_size": 100
        }
    
    Returns:
        JSON response with analysis results
    """
    try:
        # Get optional parameters
        data = request.get_json(silent=True) or {}
        batch_size = data.get('batch_size', 100)
        
        # Validate batch_size
        if not isinstance(batch_size, int) or batch_size < 1:
            return jsonify({'error': 'batch_size must be a positive integer'}), 400
        
        # Run analysis
        result = analysis_service.run_analysis(batch_size=batch_size)
        
        return jsonify({
            'message': 'Analysis completed successfully',
            'results': result
        }), 200
    
    except AnalysisException as e:
        return jsonify({
            'error': 'Analysis failed',
            'details': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@analysis_bp.route('/connections', methods=['GET'])
@log_request
def get_connections() -> tuple[Dict[str, Any], int]:
    """
    Get all connections, optionally filtered by review status.
    Demonstrates: GET endpoint with query parameters.
    
    Query parameters:
        - review_status: Filter by review status (pending, confirmed_for_review, dismissed)
    
    Returns:
        JSON response with list of connections
    """
    try:
        # Get query parameter
        review_status = request.args.get('review_status')
        
        # Validate if provided
        if review_status and review_status not in ['pending', 'confirmed_for_review', 'dismissed']:
            return jsonify({
                'error': 'Invalid review_status. Must be: pending, confirmed_for_review, or dismissed'
            }), 400
        
        # Fetch connections
        connections = connection_service.get_all_connections(review_status=review_status)
        
        # Convert to dictionaries
        connections_dict = [conn.to_dict() for conn in connections]
        
        return jsonify({
            'count': len(connections_dict),
            'connections': connections_dict
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


@analysis_bp.route('/connections/<connection_id>', methods=['GET'])
@log_request
def get_connection(connection_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get a specific connection by ID.
    Demonstrates: GET endpoint with URL parameter.
    
    Args:
        connection_id: Connection ID from URL
    
    Returns:
        JSON response with connection details
    """
    try:
        # Validate connection_id
        try:
            id_int = int(connection_id)
            if id_int <= 0:
                return jsonify({'error': 'connection_id must be a positive integer'}), 400
        except ValueError:
            return jsonify({'error': 'connection_id must be a valid integer'}), 400
        
        # Fetch connection
        connection = connection_service.get_connection_by_id(id_int)
        
        if not connection:
            return jsonify({
                'error': f'Connection with ID {connection_id} not found'
            }), 404
        
        return jsonify({
            'connection': connection.to_dict()
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


@analysis_bp.route('/cases/<case_id>/connections', methods=['GET'])
@log_request
def get_case_connections(case_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get all connections for a specific case.
    Demonstrates: Nested resource endpoint.
    
    Args:
        case_id: Case ID from URL
    
    Returns:
        JSON response with connections for the case
    """
    try:
        # Validate case_id
        try:
            id_int = int(case_id)
            if id_int <= 0:
                return jsonify({'error': 'case_id must be a positive integer'}), 400
        except ValueError:
            return jsonify({'error': 'case_id must be a valid integer'}), 400
        
        # Fetch connections
        connections = connection_service.get_connections_for_case(id_int)
        
        # Convert to dictionaries
        connections_dict = [conn.to_dict() for conn in connections]
        
        return jsonify({
            'case_id': id_int,
            'count': len(connections_dict),
            'connections': connections_dict
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


@analysis_bp.route('/connections/<connection_id>/review', methods=['PATCH'])
@log_request
def review_connection(connection_id: str) -> tuple[Dict[str, Any], int]:
    """
    Update the review status of a connection.
    Demonstrates: PATCH endpoint for partial updates.
    
    IMPORTANT: In production, this endpoint must require authentication
    and authorization. Only authorized personnel should review connections.
    
    Args:
        connection_id: Connection ID from URL
    
    Request body:
        {
            "review_status": "confirmed_for_review" or "dismissed",
            "review_notes": "Optional notes"
        }
    
    Returns:
        JSON response with updated connection
    """
    try:
        # Validate connection_id
        try:
            id_int = int(connection_id)
            if id_int <= 0:
                return jsonify({'error': 'connection_id must be a positive integer'}), 400
        except ValueError:
            return jsonify({'error': 'connection_id must be a valid integer'}), 400
        
        # Get JSON data
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
        
        # Validate required fields
        if 'review_status' not in data:
            return jsonify({'error': 'review_status is required'}), 400
        
        new_status = data['review_status']
        review_notes = data.get('review_notes')
        
        # Update review status
        connection = connection_service.update_review_status(
            connection_id=id_int,
            new_status=new_status,
            review_notes=review_notes
        )
        
        if not connection:
            return jsonify({
                'error': f'Connection with ID {connection_id} not found'
            }), 404
        
        return jsonify({
            'message': 'Connection review status updated successfully',
            'connection': connection.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({
            'error': 'Validation error',
            'details': str(e)
        }), 400
    
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


@analysis_bp.route('/connections/statistics', methods=['GET'])
@log_request
def get_connection_statistics() -> tuple[Dict[str, Any], int]:
    """
    Get connection statistics.
    Demonstrates: Statistics endpoint.
    
    Returns:
        JSON response with statistics
    """
    try:
        stats = connection_service.get_statistics()
        
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


@analysis_bp.route('/connections/graph/<case_id>', methods=['GET'])
@log_request
def get_connection_graph(case_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get connection graph for a case (recursive traversal with depth limit).
    Demonstrates: Recursive utility usage.
    
    Args:
        case_id: Starting case ID
    
    Query parameters:
        - max_depth: Maximum traversal depth (default: 2)
    
    Returns:
        JSON response with connected cases
    """
    try:
        # Validate case_id
        try:
            id_int = int(case_id)
            if id_int <= 0:
                return jsonify({'error': 'case_id must be a positive integer'}), 400
        except ValueError:
            return jsonify({'error': 'case_id must be a valid integer'}), 400
        
        # Get max_depth parameter
        max_depth = request.args.get('max_depth', 2, type=int)
        if max_depth < 1 or max_depth > 5:
            return jsonify({'error': 'max_depth must be between 1 and 5'}), 400
        
        # Fetch connections for building graph
        all_connections = connection_service.get_all_connections()
        
        # Build graph
        graph = build_graph_from_connections([conn.to_dict() for conn in all_connections])
        
        # Get connected cases
        connected_cases = graph.get_connected_cases(id_int, max_depth=max_depth)
        
        return jsonify({
            'case_id': id_int,
            'max_depth': max_depth,
            'connected_cases': list(connected_cases),
            'connection_count': len(connected_cases)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500
