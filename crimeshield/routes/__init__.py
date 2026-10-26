"""Routes package for CRIMESHIELD API endpoints."""

from .case_routes import case_bp
from .evidence_routes import evidence_bp
from .analysis_routes import analysis_bp
from .report_routes import report_bp

__all__ = ['case_bp', 'evidence_bp', 'analysis_bp', 'report_bp']
