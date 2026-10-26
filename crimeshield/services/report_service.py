"""
Report generation service for CRIMESHIELD.
Demonstrates: File I/O, CSV generation, safe path handling.
"""

import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from crimeshield.database import get_db_connection
from crimeshield.services.case_service import CaseService
from crimeshield.services.evidence_service import EvidenceService
from crimeshield.services.connection_service import ConnectionService

logger = logging.getLogger(__name__)


class ReportService:
    """
    Service for generating reports in various formats.
    Demonstrates: File operations, CSV handling, path sanitization.
    """
    
    def __init__(self, db_path: Path, reports_dir: Optional[Path] = None) -> None:
        """
        Initialize report service.
        
        Args:
            db_path: Path to database
            reports_dir: Directory for report files (default: ./reports)
        """
        self.db_path: Path = db_path
        
        # Set reports directory with safe default
        if reports_dir is None:
            self.reports_dir = db_path.parent / "reports"
        else:
            self.reports_dir = reports_dir
        
        # Create reports directory if it doesn't exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize services
        self.case_service = CaseService(db_path)
        self.evidence_service = EvidenceService(db_path)
        self.connection_service = ConnectionService(db_path)
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal.
        Demonstrates: Security - safe filename handling.
        
        Args:
            filename: Proposed filename
            
        Returns:
            Sanitized filename
        """
        # Remove path separators and dangerous characters
        safe_name = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.'))
        
        # Ensure filename isn't empty
        if not safe_name:
            safe_name = "report"
        
        return safe_name
    
    def _safe_report_path(self, filename: str) -> Path:
        """
        Create a safe path within reports directory.
        Demonstrates: Path validation to prevent directory traversal.
        
        Args:
            filename: Desired filename
            
        Returns:
            Safe path within reports directory
        """
        safe_filename = self._sanitize_filename(filename)
        report_path = self.reports_dir / safe_filename
        
        # Resolve paths and verify report_path is within reports_dir
        try:
            report_path = report_path.resolve()
            reports_dir_resolved = self.reports_dir.resolve()
            
            # Check if report_path is within reports_dir
            if not str(report_path).startswith(str(reports_dir_resolved)):
                raise ValueError("Invalid report path - outside reports directory")
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            # Fallback to safe default
            report_path = reports_dir_resolved / "report.txt"
        
        return report_path
    
    def generate_system_summary(self) -> Dict[str, Any]:
        """
        Generate overall system summary.
        
        Returns:
            Dictionary with system statistics
        """
        try:
            case_stats = self.case_service.get_statistics()
            evidence_stats = self.evidence_service.get_statistics()
            connection_stats = self.connection_service.get_statistics()
            
            return {
                'generated_at': datetime.now().isoformat(),
                'cases': case_stats,
                'evidence': evidence_stats,
                'connections': connection_stats
            }
        except Exception as e:
            logger.error(f"Error generating system summary: {e}")
            raise
    
    def generate_case_report_csv(self, case_id: int) -> Path:
        """
        Generate CSV report for a case.
        Demonstrates: CSV file generation.
        
        Args:
            case_id: Case ID
            
        Returns:
            Path to generated CSV file
        """
        try:
            # Get case data
            case = self.case_service.get_case_by_id(case_id)
            if not case:
                raise ValueError(f"Case {case_id} not found")
            
            # Get evidence for case
            evidence_list = self.evidence_service.get_evidence_by_case(case_id)
            
            # Get connections for case
            connections = self.connection_service.get_connections_for_case(case_id)
            
            # Create safe filename
            filename = f"case_{case_id}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path = self._safe_report_path(filename)
            
            # Write CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Case information section
                writer.writerow(['CASE REPORT'])
                writer.writerow(['Case ID', case.id])
                writer.writerow(['Case Code', case.case_code])
                writer.writerow(['Title', case.title])
                writer.writerow(['Description', case.description or ''])
                writer.writerow(['Location', case.location or ''])
                writer.writerow(['Status', case.status])
                writer.writerow(['Created At', case.created_at.isoformat() if case.created_at else ''])
                writer.writerow([])
                
                # Evidence section
                writer.writerow(['EVIDENCE'])
                writer.writerow(['ID', 'Evidence Code', 'Type', 'Description', 'Status'])
                for evidence in evidence_list:
                    writer.writerow([
                        evidence.id,
                        evidence.evidence_code,
                        evidence.evidence_type,
                        evidence.description or '',
                        evidence.processing_status
                    ])
                writer.writerow([])
                
                # Connections section
                writer.writerow(['CONNECTIONS'])
                writer.writerow(['ID', 'Connected Case', 'Type', 'Value', 'Review Status'])
                for conn in connections:
                    # Determine which case is the "other" case
                    other_case = conn.case_id_2 if conn.case_id_1 == case_id else conn.case_id_1
                    writer.writerow([
                        conn.id,
                        other_case,
                        conn.connection_type,
                        conn.connection_value,
                        conn.review_status
                    ])
            
            logger.info(f"Generated CSV report: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            raise
    
    def generate_case_report_txt(self, case_id: int) -> Path:
        """
        Generate plain text report for a case.
        Demonstrates: Text file generation with formatting.
        
        Args:
            case_id: Case ID
            
        Returns:
            Path to generated TXT file
        """
        try:
            # Get case data
            case = self.case_service.get_case_by_id(case_id)
            if not case:
                raise ValueError(f"Case {case_id} not found")
            
            # Get evidence and connections
            evidence_list = self.evidence_service.get_evidence_by_case(case_id)
            connections = self.connection_service.get_connections_for_case(case_id)
            
            # Create safe filename
            filename = f"case_{case_id}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            file_path = self._safe_report_path(filename)
            
            # Write text report
            with open(file_path, 'w', encoding='utf-8') as txtfile:
                txtfile.write("="*60 + "\n")
                txtfile.write("CRIMESHIELD CASE REPORT\n")
                txtfile.write("="*60 + "\n\n")
                
                # Case information
                txtfile.write("CASE INFORMATION\n")
                txtfile.write("-"*60 + "\n")
                txtfile.write(f"Case ID:          {case.id}\n")
                txtfile.write(f"Case Code:        {case.case_code}\n")
                txtfile.write(f"Title:            {case.title}\n")
                txtfile.write(f"Description:      {case.description or 'N/A'}\n")
                txtfile.write(f"Location:         {case.location or 'N/A'}\n")
                txtfile.write(f"Status:           {case.status}\n")
                txtfile.write(f"Created At:       {case.created_at.isoformat() if case.created_at else 'N/A'}\n")
                txtfile.write("\n")
                
                # Evidence section
                txtfile.write("EVIDENCE ITEMS\n")
                txtfile.write("-"*60 + "\n")
                if evidence_list:
                    for i, evidence in enumerate(evidence_list, 1):
                        txtfile.write(f"\n{i}. Evidence Code: {evidence.evidence_code}\n")
                        txtfile.write(f"   Type:           {evidence.evidence_type}\n")
                        txtfile.write(f"   Description:    {evidence.description or 'N/A'}\n")
                        txtfile.write(f"   Status:         {evidence.processing_status}\n")
                        if evidence.location_reference:
                            txtfile.write(f"   Location Ref:   {evidence.location_reference}\n")
                        if evidence.person_reference:
                            txtfile.write(f"   Person Ref:     {evidence.person_reference}\n")
                        if evidence.phone_reference:
                            txtfile.write(f"   Phone Ref:      {evidence.phone_reference}\n")
                else:
                    txtfile.write("No evidence items found.\n")
                txtfile.write("\n")
                
                # Connections section
                txtfile.write("POTENTIAL CONNECTIONS\n")
                txtfile.write("-"*60 + "\n")
                if connections:
                    for i, conn in enumerate(connections, 1):
                        other_case = conn.case_id_2 if conn.case_id_1 == case_id else conn.case_id_1
                        txtfile.write(f"\n{i}. Connection ID: {conn.id}\n")
                        txtfile.write(f"   Connected to:    Case {other_case}\n")
                        txtfile.write(f"   Type:            {conn.connection_type}\n")
                        txtfile.write(f"   Shared Value:    {conn.connection_value}\n")
                        txtfile.write(f"   Explanation:     {conn.explanation}\n")
                        txtfile.write(f"   Review Status:   {conn.review_status}\n")
                        if conn.review_notes:
                            txtfile.write(f"   Review Notes:    {conn.review_notes}\n")
                else:
                    txtfile.write("No connections found.\n")
                txtfile.write("\n")
                
                # Footer
                txtfile.write("="*60 + "\n")
                txtfile.write(f"Report generated: {datetime.now().isoformat()}\n")
                txtfile.write("IMPORTANT: Connections are investigative leads, not proof.\n")
                txtfile.write("="*60 + "\n")
            
            logger.info(f"Generated TXT report: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"Error generating TXT report: {e}")
            raise
