"""
Main application file for CRIMESHIELD.
Demonstrates: Flask application setup, blueprints, and application factory pattern.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from pathlib import Path
import logging

from crimeshield.config import Config
from crimeshield.database import init_database
from crimeshield.routes.case_routes import case_bp, init_case_service
from crimeshield.routes.evidence_routes import evidence_bp, init_evidence_service
from crimeshield.routes.analysis_routes import analysis_bp, init_analysis_services
from crimeshield.routes.report_routes import report_bp, init_report_service
from crimeshield.services.audit_service import AuditLogger
from crimeshield.utils.logger import setup_logger


def create_app(config_class=Config) -> Flask:
    """
    Application factory function.
    Demonstrates: Factory pattern for creating Flask applications.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application
    """
    # Create Flask application
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)

    # Enable CORS for local development (Vite dev server)
    CORS(
        app,
        resources={r"/api/*": {"origins": [
            "http://127.0.0.1:5173", "http://localhost:5173",
            "http://127.0.0.1:3000", "http://localhost:3000",
            "http://127.0.0.1:4173", "http://localhost:4173"
        ]}},
        supports_credentials=True
    )
    
    # Setup logging
    logger = setup_logger('crimeshield', logging.INFO)
    logger.info("Starting CRIMESHIELD application")
    
    # Initialize database
    db_path = Path(app.config['DATABASE_PATH'])
    init_database(db_path)
    logger.info(f"Database initialized at: {db_path}")
    
    # Initialize audit logger
    audit_logger = AuditLogger(db_path)
    logger.info("Audit logger initialized")
    
    # Initialize services
    init_case_service(db_path)
    logger.info("Case service initialized")
    
    init_evidence_service(db_path, audit_logger)
    logger.info("Evidence service initialized with audit logging")
    
    init_analysis_services(db_path, audit_logger)
    logger.info("Analysis services initialized with audit logging")
    
    init_report_service(db_path)
    logger.info("Report service initialized")
    
    # Register blueprints
    app.register_blueprint(case_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(report_bp)
    logger.info("Blueprints registered")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'error': 'Resource not found',
            'message': 'The requested URL was not found on the server'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.route('/')
    def index():
        """Root endpoint with API information."""
        return jsonify({
            'service': 'CRIMESHIELD - Criminal Network Analysis System',
            'version': '3.0.0',
            'description': 'API for managing criminal investigation cases, evidence, and connection analysis',
            'status': 'operational',
            'endpoints': {
                'health': '/api/health',
                'cases': '/api/cases',
                'case_by_id': '/api/cases/<id>',
                'case_by_code': '/api/cases/code/<case_code>',
                'case_statistics': '/api/cases/statistics',
                'evidence': '/api/evidence',
                'evidence_by_id': '/api/evidence/<id>',
                'case_evidence': '/api/cases/<case_id>/evidence',
                'evidence_statistics': '/api/evidence/statistics',
                'analysis_run': '/api/analysis/run',
                'connections': '/api/connections',
                'connection_by_id': '/api/connections/<id>',
                'case_connections': '/api/cases/<case_id>/connections',
                'connection_review': '/api/connections/<id>/review',
                'connection_statistics': '/api/connections/statistics',
                'connection_graph': '/api/connections/graph/<case_id>',
                'reports_summary': '/api/reports/summary',
                'case_report': '/api/reports/cases/<case_id>',
                'case_export': '/api/reports/cases/<case_id>/export?format=csv|txt'
            }
        }), 200
    
    logger.info("Application setup complete")
    return app


def main():
    """
    Main entry point for running the application.
    Demonstrates: Main function pattern.
    """
    app = create_app()
    
    # Get configuration
    debug_mode = app.config.get('DEBUG', False)
    
    print("\n" + "="*60)
    print("CRIMESHIELD - Criminal Network Analysis System v3.0")
    print("="*60)
    print(f"Database: {app.config['DATABASE_PATH']}")
    print(f"Debug Mode: {debug_mode}")
    print("\nCase Management API Endpoints:")
    print("  - GET    /api/health")
    print("  - POST   /api/cases")
    print("  - GET    /api/cases")
    print("  - GET    /api/cases/<id>")
    print("  - GET    /api/cases/code/<case_code>")
    print("  - PUT    /api/cases/<id>")
    print("  - DELETE /api/cases/<id>")
    print("  - GET    /api/cases/statistics")
    print("\nEvidence Management API Endpoints:")
    print("  - POST   /api/evidence")
    print("  - GET    /api/evidence")
    print("  - GET    /api/evidence/<id>")
    print("  - PUT    /api/evidence/<id>")
    print("  - DELETE /api/evidence/<id>")
    print("  - GET    /api/cases/<case_id>/evidence")
    print("  - GET    /api/evidence/statistics")
    print("\nConnection Analysis API Endpoints:")
    print("  - POST   /api/analysis/run")
    print("  - GET    /api/connections")
    print("  - GET    /api/connections/<id>")
    print("  - GET    /api/cases/<case_id>/connections")
    print("  - PATCH  /api/connections/<id>/review")
    print("  - GET    /api/connections/statistics")
    print("  - GET    /api/connections/graph/<case_id>")
    print("\nReport Generation API Endpoints:")
    print("  - GET    /api/reports/summary")
    print("  - GET    /api/reports/cases/<case_id>")
    print("  - GET    /api/reports/cases/<case_id>/export?format=csv")
    print("  - GET    /api/reports/cases/<case_id>/export?format=txt")
    print("="*60)
    print("Server starting on http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server")
    print("="*60 + "\n")
    
    # Run the application
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=debug_mode
    )


if __name__ == '__main__':
    main()
