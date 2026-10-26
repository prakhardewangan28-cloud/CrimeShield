"""
Report routes for CRIMESHIELD REST API.
Demonstrates: File download endpoints, content-type handling.
"""

from flask import Blueprint, jsonify, send_file
from typing import Dict, Any
import logging

from crimeshield.services.report_service import ReportService
from crimeshield.utils.logger import log_request

logger = logging.getLogger(__name__)

# Create a Blueprint for report-related routes
report_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

# Initialize service (will be properly initialized in app.py)
report_service: ReportService = None


def init_report_service(db_path) -> None:
    """
    Initialize the report service.
    Called from app.py during application setup.
    """
    global report_service
    report_service = ReportService(db_path)


@report_bp.route('/summary', methods=['GET'])
@log_request
def get_system_summary() -> tuple[Dict[str, Any], int]:
    """
    Get overall system summary.
    Demonstrates: Summary statistics endpoint.
    
    Returns:
        JSON response with system statistics
    """
    try:
        summary = report_service.generate_system_summary()
        
        return jsonify({
            'summary': summary
        }), 200
    
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@report_bp.route('/cases/<case_id>', methods=['GET'])
@log_request
def get_case_report(case_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get case report information (metadata, not file).
    Demonstrates: Report metadata endpoint.
    
    Args:
        case_id: Case ID from URL
    
    Returns:
        JSON response with report information
    """
    try:
        # Validate case_id
        try:
            id_int = int(case_id)
            if id_int <= 0:
                return jsonify({'error': 'case_id must be a positive integer'}), 400
        except ValueError:
            return jsonify({'error': 'case_id must be a valid integer'}), 400
        
        # Check if case exists
        case = report_service.case_service.get_case_by_id(id_int)
        if not case:
            return jsonify({
                'error': f'Case with ID {case_id} not found'
            }), 404
        
        # Get counts
        evidence_count = len(report_service.evidence_service.get_evidence_by_case(id_int))
        connection_count = len(report_service.connection_service.get_connections_for_case(id_int))
        
        return jsonify({
            'case_id': id_int,
            'case_code': case.case_code,
            'title': case.title,
            'evidence_count': evidence_count,
            'connection_count': connection_count,
            'available_formats': ['csv', 'txt']
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting case report info: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@report_bp.route('/cases/<case_id>/export', methods=['GET'])
@log_request
def export_case_report(case_id: str):
    """
    Export case report in specified format.
    Demonstrates: File download with proper content-type.
    
    Args:
        case_id: Case ID from URL
    
    Query parameters:
        - format: Export format (csv or txt)
    
    Returns:
        File download or error response
    """
    try:
        # Validate case_id
        try:
            id_int = int(case_id)
            if id_int <= 0:
                return jsonify({'error': 'case_id must be a positive integer'}), 400
        except ValueError:
            return jsonify({'error': 'case_id must be a valid integer'}), 400
        
        # Get format parameter
        from flask import request
        export_format = request.args.get('format', 'txt').lower()
        
        # Validate format
        if export_format not in ['csv', 'txt']:
            return jsonify({
                'error': 'Invalid format. Must be csv or txt'
            }), 400
        
        # Check if case exists
        case = report_service.case_service.get_case_by_id(id_int)
        if not case:
            return jsonify({
                'error': f'Case with ID {case_id} not found'
            }), 404
        
        # Generate report
        if export_format == 'csv':
            file_path = report_service.generate_case_report_csv(id_int)
            mimetype = 'text/csv'
            download_name = f"case_{case_id}_report.csv"
        else:  # txt
            file_path = report_service.generate_case_report_txt(id_int)
            mimetype = 'text/plain'
            download_name = f"case_{case_id}_report.txt"
        
        # Send file
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=download_name
        )
    
    except ValueError as e:
        return jsonify({
            'error': 'Validation error',
            'details': str(e)
        }), 404
    
    except Exception as e:
        logger.error(f"Error exporting case report: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500
