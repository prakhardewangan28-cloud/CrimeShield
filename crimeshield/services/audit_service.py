"""
Audit logging service for CRIMESHIELD.
Demonstrates: Context managers, decorators, and audit trail implementation.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from functools import wraps
from datetime import datetime
import json
import logging

from crimeshield.database import get_db_connection
from crimeshield.utils.advanced_python import format_entity_info

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Service class for audit logging operations.
    Demonstrates: Context manager usage, service pattern, and audit trail.
    """
    
    def __init__(self, db_path: Path) -> None:
        """
        Initialize the audit logger.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path: Path = db_path
    
    def log(
        self,
        action: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        **details: Any
    ) -> int:
        """
        Create an audit log entry.
        Demonstrates: **kwargs for flexible detail capture.
        
        Args:
            action: Action performed (created, updated, deleted, etc.)
            entity_type: Type of entity (case, evidence)
            entity_id: ID of the entity
            **details: Additional details to log
            
        Returns:
            ID of created audit log entry
        """
        query = """
        INSERT INTO audit_logs (action, entity_type, entity_id, details)
        VALUES (?, ?, ?, ?)
        """
        
        # Format details as JSON, excluding sensitive information
        details_json = json.dumps(self._sanitize_details(details))
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (action, entity_type, entity_id, details_json))
                conn.commit()
                
                audit_id = cursor.lastrowid
                logger.debug(f"Audit log created: {action} on {entity_type} {entity_id}")
                return audit_id
        except sqlite3.Error as e:
            logger.error(f"Error creating audit log: {e}")
            raise
    
    def get_logs(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs with optional filtering.
        
        Args:
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            action: Filter by action
            limit: Maximum number of logs to return
            
        Returns:
            List of audit log dictionaries
        """
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params: List[Any] = []
        
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        
        if entity_id is not None:
            query += " AND entity_id = ?"
            params.append(entity_id)
        
        if action:
            query += " AND action = ?"
            params.append(action)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving audit logs: {e}")
            raise
    
    def get_entity_history(self, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        """
        Get complete history for a specific entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            
        Returns:
            List of audit logs for the entity
        """
        return self.get_logs(entity_type=entity_type, entity_id=entity_id, limit=1000)
    
    @staticmethod
    def _sanitize_details(details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive information from audit details.
        Demonstrates: Static method for utility function.
        
        Args:
            details: Details dictionary
            
        Returns:
            Sanitized details
        """
        # List of sensitive keys to exclude
        sensitive_keys = {'password', 'token', 'secret', 'api_key'}
        
        return {
            key: value for key, value in details.items()
            if key.lower() not in sensitive_keys
        }


def audit_operation(action: str, entity_type: str):
    """
    Decorator to automatically log operations.
    Demonstrates: Decorator pattern for cross-cutting concerns.
    
    Args:
        action: Action being performed
        entity_type: Type of entity
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            """
            Wrapper function that adds audit logging.
            Demonstrates: Closure accessing decorator parameters.
            """
            # Execute the function
            result = func(self, *args, **kwargs)
            
            # Try to extract entity_id from result
            entity_id = None
            if hasattr(result, 'id'):
                entity_id = result.id
            elif isinstance(result, dict) and 'id' in result:
                entity_id = result['id']
            
            # Log the operation if audit_logger is available
            if hasattr(self, 'audit_logger') and self.audit_logger:
                try:
                    # Format additional context using format_entity_info
                    context = format_entity_info(
                        func.__name__,
                        action=action,
                        entity_type=entity_type
                    )
                    
                    self.audit_logger.log(
                        action=action,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        operation=func.__name__,
                        context=context
                    )
                except Exception as e:
                    # Don't fail the operation if audit logging fails
                    logger.warning(f"Audit logging failed: {e}")
            
            return result
        
        return wrapper
    return decorator
