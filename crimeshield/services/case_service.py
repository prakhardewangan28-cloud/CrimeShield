"""
Case service module for CRIMESHIELD business logic.
Demonstrates: Separation of concerns, exception handling, and CRUD operations.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from crimeshield.models.case_model import Case
from crimeshield.database import get_db_connection

logger = logging.getLogger(__name__)


class CaseService:
    """
    Service class for case management operations.
    Demonstrates: Service layer pattern, separating business logic from routes.
    """
    
    def __init__(self, db_path: Path) -> None:
        """
        Initialize the case service.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path: Path = db_path
    
    def create_case(
        self,
        case_code: str,
        title: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        status: str = "open"
    ) -> Case:
        """
        Create a new case in the database.
        Demonstrates: Exception handling and parameterized queries.
        
        Args:
            case_code: Unique case identifier
            title: Case title
            description: Case description
            location: Case location
            status: Initial status
            
        Returns:
            Created Case object
            
        Raises:
            sqlite3.IntegrityError: If case_code already exists
            sqlite3.Error: For other database errors
        """
        query = """
        INSERT INTO cases (case_code, title, description, location, status)
        VALUES (?, ?, ?, ?, ?)
        """
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                # Using parameterized query to prevent SQL injection
                cursor.execute(query, (case_code, title, description, location, status))
                conn.commit()
                
                case_id = cursor.lastrowid
                logger.info(f"Created case {case_code} with ID {case_id}")
                
                # Return the created case
                return self.get_case_by_id(case_id)
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error creating case {case_code}: {e}")
            raise
        except sqlite3.Error as e:
            logger.error(f"Database error creating case: {e}")
            raise
    
    def get_case_by_id(self, case_id: int) -> Optional[Case]:
        """
        Retrieve a case by its ID.
        
        Args:
            case_id: Database ID of the case
            
        Returns:
            Case object or None if not found
        """
        query = "SELECT * FROM cases WHERE id = ?"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (case_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_case(row)
                return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching case by ID {case_id}: {e}")
            raise
    
    def get_case_by_code(self, case_code: str) -> Optional[Case]:
        """
        Retrieve a case by its case code.
        
        Args:
            case_code: Unique case code
            
        Returns:
            Case object or None if not found
        """
        query = "SELECT * FROM cases WHERE case_code = ?"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (case_code,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_case(row)
                return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching case by code {case_code}: {e}")
            raise
    
    def get_all_cases(self) -> List[Case]:
        """
        Retrieve all cases from the database.
        Demonstrates: List comprehension.
        
        Returns:
            List of Case objects
        """
        query = "SELECT * FROM cases ORDER BY created_at DESC"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                # List comprehension to convert rows to Case objects
                return [self._row_to_case(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error fetching all cases: {e}")
            raise
    
    def update_case(
        self,
        case_id: int,
        case_code: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[Case]:
        """
        Update an existing case.
        Demonstrates: Dynamic SQL building and exception handling.
        
        Args:
            case_id: ID of the case to update
            case_code: New case code (optional)
            title: New title (optional)
            description: New description (optional)
            location: New location (optional)
            status: New status (optional)
            
        Returns:
            Updated Case object or None if not found
            
        Raises:
            sqlite3.IntegrityError: If new case_code already exists
        """
        # Build update query dynamically based on provided fields
        # Demonstrates: Dictionary comprehension with conditional logic
        updates = {
            'case_code': case_code,
            'title': title,
            'description': description,
            'location': location,
            'status': status
        }
        
        # Filter out None values using dictionary comprehension
        updates = {k: v for k, v in updates.items() if v is not None}
        
        if not updates:
            # Nothing to update
            return self.get_case_by_id(case_id)
        
        # Build SQL SET clause
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        query = f"UPDATE cases SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                # Add case_id to the end of values
                values = list(updates.values()) + [case_id]
                cursor.execute(query, values)
                conn.commit()
                
                if cursor.rowcount == 0:
                    logger.warning(f"No case found with ID {case_id} to update")
                    return None
                
                logger.info(f"Updated case ID {case_id}")
                return self.get_case_by_id(case_id)
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error updating case {case_id}: {e}")
            raise
        except sqlite3.Error as e:
            logger.error(f"Error updating case {case_id}: {e}")
            raise
    
    def delete_case(self, case_id: int) -> bool:
        """
        Delete a case from the database.
        
        Args:
            case_id: ID of the case to delete
            
        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM cases WHERE id = ?"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (case_id,))
                conn.commit()
                
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Deleted case ID {case_id}")
                else:
                    logger.warning(f"No case found with ID {case_id} to delete")
                
                return deleted
        except sqlite3.Error as e:
            logger.error(f"Error deleting case {case_id}: {e}")
            raise
    
    def search_cases(
        self,
        title: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Case]:
        """
        Search cases by various criteria.
        Demonstrates: Dynamic query building and lambda functions.
        
        Args:
            title: Search by title (partial match)
            location: Search by location (partial match)
            status: Filter by exact status
            
        Returns:
            List of matching Case objects
        """
        # Start with base query
        query = "SELECT * FROM cases WHERE 1=1"
        params: List[Any] = []
        
        # Build WHERE clause dynamically
        if title:
            query += " AND title LIKE ?"
            params.append(f"%{title}%")
        
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert rows to Case objects
                cases = [self._row_to_case(row) for row in rows]
                
                logger.info(f"Search found {len(cases)} cases")
                return cases
        except sqlite3.Error as e:
            logger.error(f"Error searching cases: {e}")
            raise
    
    def get_cases_by_status(self, status: str) -> List[Case]:
        """
        Get all cases with a specific status.
        Demonstrates: Using lambda for sorting.
        
        Args:
            status: Case status to filter by
            
        Returns:
            List of Case objects sorted by creation date
        """
        cases = self.search_cases(status=status)
        
        # Lambda function to sort by created_at (newest first)
        return sorted(
            cases,
            key=lambda case: case.created_at if case.created_at else datetime.min,
            reverse=True
        )
    
    def get_active_cases(self) -> List[Case]:
        """
        Get all active cases (open or under_review).
        Demonstrates: List comprehension with filtering.
        
        Returns:
            List of active Case objects
        """
        all_cases = self.get_all_cases()
        
        # Filter active cases using list comprehension
        return [case for case in all_cases if case.is_active()]
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get case statistics.
        Demonstrates: Dictionary operations.
        
        Returns:
            Dictionary with statistics
        """
        query = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open,
            SUM(CASE WHEN status = 'under_review' THEN 1 ELSE 0 END) as under_review,
            SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed
        FROM cases
        """
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                row = cursor.fetchone()
                
                return {
                    'total': row['total'] or 0,
                    'open': row['open'] or 0,
                    'under_review': row['under_review'] or 0,
                    'closed': row['closed'] or 0
                }
        except sqlite3.Error as e:
            logger.error(f"Error getting statistics: {e}")
            raise
    
    @staticmethod
    def _row_to_case(row: sqlite3.Row) -> Case:
        """
        Convert a database row to a Case object.
        Demonstrates: Static method for utility function.
        
        Args:
            row: SQLite row object
            
        Returns:
            Case object
        """
        return Case(
            case_id=row['id'],
            case_code=row['case_code'],
            title=row['title'],
            description=row['description'],
            location=row['location'],
            status=row['status'],
            created_at=Case._parse_datetime(row['created_at']),
            updated_at=Case._parse_datetime(row['updated_at'])
        )
