"""
Evidence service module for CRIMESHIELD business logic.
Demonstrates: Service layer pattern with audit logging integration.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from crimeshield.models.evidence_model import Evidence
from crimeshield.database import get_db_connection
from crimeshield.services.audit_service import AuditLogger, audit_operation
from crimeshield.utils.advanced_python import (
    NotFoundError, 
    DuplicateError, 
    InvalidReferenceError,
    filter_by_status,
    count_by_type
)

logger = logging.getLogger(__name__)


class EvidenceService:
    """
    Service class for evidence management operations.
    Demonstrates: Service layer with audit logging and advanced error handling.
    """
    
    def __init__(self, db_path: Path, audit_logger: Optional[AuditLogger] = None) -> None:
        """
        Initialize the evidence service.
        
        Args:
            db_path: Path to the SQLite database
            audit_logger: Optional audit logger instance
        """
        self.db_path: Path = db_path
        self.audit_logger: Optional[AuditLogger] = audit_logger
    
    def _case_exists(self, case_id: int) -> bool:
        """
        Check if a case exists.
        
        Args:
            case_id: ID of the case
            
        Returns:
            True if case exists
        """
        query = "SELECT id FROM cases WHERE id = ?"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (case_id,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(f"Error checking case existence: {e}")
            raise
    
    @audit_operation('created', 'evidence')
    def create_evidence(
        self,
        evidence_code: str,
        case_id: int,
        evidence_type: str,
        description: Optional[str] = None,
        location_reference: Optional[str] = None,
        person_reference: Optional[str] = None,
        phone_reference: Optional[str] = None,
        processing_status: str = "pending"
    ) -> Evidence:
        """
        Create a new evidence entry in the database.
        Demonstrates: Foreign key validation and custom exceptions.
        
        Args:
            evidence_code: Unique evidence identifier
            case_id: ID of related case
            evidence_type: Type of evidence
            description: Evidence description
            location_reference: Location reference
            person_reference: Person reference
            phone_reference: Phone reference
            processing_status: Initial processing status
            
        Returns:
            Created Evidence object
            
        Raises:
            InvalidReferenceError: If case_id doesn't exist
            DuplicateError: If evidence_code already exists
        """
        # Validate that the case exists
        if not self._case_exists(case_id):
            raise InvalidReferenceError('case', case_id)
        
        query = """
        INSERT INTO evidence (
            evidence_code, case_id, evidence_type, description,
            location_reference, person_reference, phone_reference, processing_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (
                    evidence_code, case_id, evidence_type, description,
                    location_reference, person_reference, phone_reference, processing_status
                ))
                conn.commit()
                
                evidence_id = cursor.lastrowid
                logger.info(f"Created evidence {evidence_code} with ID {evidence_id}")
                
                return self.get_evidence_by_id(evidence_id)
        except sqlite3.IntegrityError as e:
            if 'evidence_code' in str(e) or 'UNIQUE' in str(e):
                raise DuplicateError('evidence', 'evidence_code', evidence_code)
            logger.error(f"Integrity error creating evidence: {e}")
            raise
        except sqlite3.Error as e:
            logger.error(f"Database error creating evidence: {e}")
            raise
    
    def get_evidence_by_id(self, evidence_id: int) -> Optional[Evidence]:
        """
        Retrieve evidence by its ID.
        
        Args:
            evidence_id: Database ID of the evidence
            
        Returns:
            Evidence object or None if not found
        """
        query = "SELECT * FROM evidence WHERE id = ?"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (evidence_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_evidence(row)
                return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching evidence by ID {evidence_id}: {e}")
            raise
    
    def get_evidence_by_code(self, evidence_code: str) -> Optional[Evidence]:
        """
        Retrieve evidence by its code.
        
        Args:
            evidence_code: Unique evidence code
            
        Returns:
            Evidence object or None if not found
        """
        query = "SELECT * FROM evidence WHERE evidence_code = ?"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (evidence_code,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_evidence(row)
                return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching evidence by code {evidence_code}: {e}")
            raise
    
    def get_all_evidence(self) -> List[Evidence]:
        """
        Retrieve all evidence from the database.
        Demonstrates: List comprehension for data transformation.
        
        Returns:
            List of Evidence objects
        """
        query = "SELECT * FROM evidence ORDER BY created_at DESC"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                return [self._row_to_evidence(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error fetching all evidence: {e}")
            raise
    
    def get_evidence_by_case(self, case_id: int) -> List[Evidence]:
        """
        Get all evidence belonging to a specific case.
        
        Args:
            case_id: ID of the case
            
        Returns:
            List of Evidence objects
        """
        query = "SELECT * FROM evidence WHERE case_id = ? ORDER BY created_at DESC"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (case_id,))
                rows = cursor.fetchall()
                
                return [self._row_to_evidence(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error fetching evidence for case {case_id}: {e}")
            raise
    
    def search_evidence(
        self,
        evidence_type: Optional[str] = None,
        processing_status: Optional[str] = None,
        case_id: Optional[int] = None
    ) -> List[Evidence]:
        """
        Search evidence by various criteria.
        Demonstrates: Dynamic query building.
        
        Args:
            evidence_type: Filter by evidence type
            processing_status: Filter by processing status
            case_id: Filter by case ID
            
        Returns:
            List of matching Evidence objects
        """
        query = "SELECT * FROM evidence WHERE 1=1"
        params: List[Any] = []
        
        if evidence_type:
            query += " AND evidence_type = ?"
            params.append(evidence_type)
        
        if processing_status:
            query += " AND processing_status = ?"
            params.append(processing_status)
        
        if case_id is not None:
            query += " AND case_id = ?"
            params.append(case_id)
        
        query += " ORDER BY created_at DESC"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                evidence_list = [self._row_to_evidence(row) for row in rows]
                logger.info(f"Search found {len(evidence_list)} evidence items")
                return evidence_list
        except sqlite3.Error as e:
            logger.error(f"Error searching evidence: {e}")
            raise
    
    @audit_operation('updated', 'evidence')
    def update_evidence(
        self,
        evidence_id: int,
        evidence_code: Optional[str] = None,
        evidence_type: Optional[str] = None,
        description: Optional[str] = None,
        location_reference: Optional[str] = None,
        person_reference: Optional[str] = None,
        phone_reference: Optional[str] = None,
        processing_status: Optional[str] = None
    ) -> Optional[Evidence]:
        """
        Update an existing evidence entry.
        Demonstrates: Dynamic SQL building and dictionary comprehension.
        
        Args:
            evidence_id: ID of the evidence to update
            evidence_code: New evidence code (optional)
            evidence_type: New evidence type (optional)
            description: New description (optional)
            location_reference: New location reference (optional)
            person_reference: New person reference (optional)
            phone_reference: New phone reference (optional)
            processing_status: New processing status (optional)
            
        Returns:
            Updated Evidence object or None if not found
        """
        updates = {
            'evidence_code': evidence_code,
            'evidence_type': evidence_type,
            'description': description,
            'location_reference': location_reference,
            'person_reference': person_reference,
            'phone_reference': phone_reference,
            'processing_status': processing_status
        }
        
        # Filter out None values using dictionary comprehension
        updates = {k: v for k, v in updates.items() if v is not None}
        
        if not updates:
            return self.get_evidence_by_id(evidence_id)
        
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        query = f"UPDATE evidence SET {set_clause} WHERE id = ?"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                values = list(updates.values()) + [evidence_id]
                cursor.execute(query, values)
                conn.commit()
                
                if cursor.rowcount == 0:
                    logger.warning(f"No evidence found with ID {evidence_id} to update")
                    return None
                
                logger.info(f"Updated evidence ID {evidence_id}")
                return self.get_evidence_by_id(evidence_id)
        except sqlite3.IntegrityError as e:
            if 'evidence_code' in str(e):
                raise DuplicateError('evidence', 'evidence_code', evidence_code)
            logger.error(f"Integrity error updating evidence: {e}")
            raise
        except sqlite3.Error as e:
            logger.error(f"Error updating evidence {evidence_id}: {e}")
            raise
    
    @audit_operation('deleted', 'evidence')
    def delete_evidence(self, evidence_id: int) -> bool:
        """
        Delete an evidence entry from the database.
        
        Args:
            evidence_id: ID of the evidence to delete
            
        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM evidence WHERE id = ?"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (evidence_id,))
                conn.commit()
                
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Deleted evidence ID {evidence_id}")
                else:
                    logger.warning(f"No evidence found with ID {evidence_id} to delete")
                
                return deleted
        except sqlite3.Error as e:
            logger.error(f"Error deleting evidence {evidence_id}: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get evidence statistics.
        Demonstrates: Using advanced_python utilities.
        
        Returns:
            Dictionary with statistics
        """
        try:
            all_evidence = self.get_all_evidence()
            evidence_dicts = [e.to_dict() for e in all_evidence]
            
            # Use advanced_python functions
            by_type = count_by_type(evidence_dicts, 'evidence_type')
            by_status = count_by_type(evidence_dicts, 'processing_status')
            
            return {
                'total': len(all_evidence),
                'by_type': by_type,
                'by_status': by_status
            }
        except sqlite3.Error as e:
            logger.error(f"Error getting statistics: {e}")
            raise
    
    @staticmethod
    def _row_to_evidence(row: sqlite3.Row) -> Evidence:
        """
        Convert a database row to an Evidence object.
        Demonstrates: Static method for utility function.
        
        Args:
            row: SQLite row object
            
        Returns:
            Evidence object
        """
        return Evidence(
            evidence_id=row['id'],
            evidence_code=row['evidence_code'],
            case_id=row['case_id'],
            evidence_type=row['evidence_type'],
            description=row['description'],
            location_reference=row['location_reference'],
            person_reference=row['person_reference'],
            phone_reference=row['phone_reference'],
            processing_status=row['processing_status'],
            created_at=Evidence._parse_datetime(row['created_at'])
        )
