"""
Connection service for CRIMESHIELD.
Demonstrates: CRUD operations for connections with audit logging.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from crimeshield.models.connection_model import Connection
from crimeshield.database import get_db_connection
from crimeshield.services.audit_service import AuditLogger
from crimeshield.utils.advanced_python import NotFoundError

logger = logging.getLogger(__name__)


class ConnectionService:
    """Service class for connection management operations."""
    
    def __init__(
        self,
        db_path: Path,
        audit_logger: Optional[AuditLogger] = None
    ) -> None:
        """
        Initialize connection service.
        
        Args:
            db_path: Path to SQLite database
            audit_logger: Optional audit logger
        """
        self.db_path: Path = db_path
        self.audit_logger: Optional[AuditLogger] = audit_logger
    
    def get_connection_by_id(self, connection_id: int) -> Optional[Connection]:
        """
        Retrieve connection by ID.
        
        Args:
            connection_id: Connection ID
            
        Returns:
            Connection object or None
        """
        query = "SELECT * FROM connections WHERE id = ?"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (connection_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_connection(row)
                return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching connection {connection_id}: {e}")
            raise
    
    def get_all_connections(
        self,
        review_status: Optional[str] = None
    ) -> List[Connection]:
        """
        Get all connections, optionally filtered by review status.
        
        Args:
            review_status: Optional filter by review status
            
        Returns:
            List of Connection objects
        """
        query = "SELECT * FROM connections"
        params = []
        
        if review_status:
            query += " WHERE review_status = ?"
            params.append(review_status)
        
        query += " ORDER BY created_at DESC"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [self._row_to_connection(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error fetching connections: {e}")
            raise
    
    def get_connections_for_case(self, case_id: int) -> List[Connection]:
        """
        Get all connections involving a specific case.
        
        Args:
            case_id: Case ID
            
        Returns:
            List of Connection objects
        """
        query = """
        SELECT * FROM connections 
        WHERE case_id_1 = ? OR case_id_2 = ?
        ORDER BY created_at DESC
        """
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (case_id, case_id))
                rows = cursor.fetchall()
                
                return [self._row_to_connection(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error fetching connections for case {case_id}: {e}")
            raise
    
    def update_review_status(
        self,
        connection_id: int,
        new_status: str,
        review_notes: Optional[str] = None
    ) -> Optional[Connection]:
        """
        Update the review status of a connection.
        
        Args:
            connection_id: Connection ID
            new_status: New review status
            review_notes: Optional review notes
            
        Returns:
            Updated Connection object or None if not found
            
        Raises:
            ValueError: If status is invalid
        """
        # Validate status
        if new_status not in Connection.VALID_REVIEW_STATUSES:
            raise ValueError(
                f"Invalid review status. Must be one of: {', '.join(Connection.VALID_REVIEW_STATUSES)}"
            )
        
        query = """
        UPDATE connections 
        SET review_status = ?, reviewed_at = ?, review_notes = ?
        WHERE id = ?
        """
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (
                    new_status,
                    datetime.now().isoformat(),
                    review_notes,
                    connection_id
                ))
                conn.commit()
                
                if cursor.rowcount == 0:
                    return None
                
                # Audit log the review
                if self.audit_logger:
                    self.audit_logger.log(
                        action='connection_reviewed',
                        entity_type='connection',
                        entity_id=connection_id,
                        new_status=new_status
                    )
                
                return self.get_connection_by_id(connection_id)
        except sqlite3.Error as e:
            logger.error(f"Error updating connection {connection_id}: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get connection statistics.
        
        Returns:
            Dictionary with statistics
        """
        query = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN review_status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN review_status = 'confirmed_for_review' THEN 1 ELSE 0 END) as confirmed,
            SUM(CASE WHEN review_status = 'dismissed' THEN 1 ELSE 0 END) as dismissed
        FROM connections
        """
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                row = cursor.fetchone()
                
                return {
                    'total': row['total'] or 0,
                    'pending': row['pending'] or 0,
                    'confirmed_for_review': row['confirmed'] or 0,
                    'dismissed': row['dismissed'] or 0
                }
        except sqlite3.Error as e:
            logger.error(f"Error getting statistics: {e}")
            raise
    
    @staticmethod
    def _row_to_connection(row: sqlite3.Row) -> Connection:
        """Convert database row to Connection object."""
        return Connection(
            connection_id=row['id'],
            case_id_1=row['case_id_1'],
            case_id_2=row['case_id_2'],
            connection_type=row['connection_type'],
            connection_value=row['connection_value'],
            explanation=row['explanation'],
            review_status=row['review_status'],
            created_at=Connection._parse_datetime(row['created_at']),
            reviewed_at=Connection._parse_datetime(row['reviewed_at']),
            review_notes=row['review_notes']
        )
