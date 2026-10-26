"""
Case model for CRIMESHIELD.
Demonstrates: Classes, type hints, dataclass-like design, and object-oriented programming.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import json


class Case:
    """
    Represents a criminal investigation case.
    Demonstrates: Class design with properties, methods, and type hints.
    """
    
    def __init__(
        self,
        case_code: str,
        title: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        status: str = "open",
        case_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ) -> None:
        """
        Initialize a Case instance.
        
        Args:
            case_code: Unique case identifier (e.g., "CASE-2024-001")
            title: Brief case title
            description: Detailed case description
            location: Location related to the case
            status: Case status (open, under_review, closed)
            case_id: Database ID (None for new cases)
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.id: Optional[int] = case_id
        self.case_code: str = case_code
        self.title: str = title
        self.description: Optional[str] = description
        self.location: Optional[str] = location
        self.status: str = status
        self.created_at: Optional[datetime] = created_at
        self.updated_at: Optional[datetime] = updated_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert case object to dictionary.
        Demonstrates: Dictionary comprehension and conditional expressions.
        
        Returns:
            Dictionary representation of the case
        """
        return {
            "id": self.id,
            "case_code": self.case_code,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_json(self) -> str:
        """
        Convert case to JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Case':
        """
        Create a Case instance from a dictionary.
        Demonstrates: Class method decorator (@classmethod).
        
        Args:
            data: Dictionary containing case data
            
        Returns:
            New Case instance
        """
        return cls(
            case_code=data.get('case_code', ''),
            title=data.get('title', ''),
            description=data.get('description'),
            location=data.get('location'),
            status=data.get('status', 'open'),
            case_id=data.get('id'),
            created_at=cls._parse_datetime(data.get('created_at')),
            updated_at=cls._parse_datetime(data.get('updated_at'))
        )
    
    @staticmethod
    def _parse_datetime(dt_string: Optional[str]) -> Optional[datetime]:
        """
        Parse datetime string to datetime object.
        Demonstrates: Static method decorator (@staticmethod).
        
        Args:
            dt_string: ISO format datetime string
            
        Returns:
            datetime object or None
        """
        if not dt_string:
            return None
        
        try:
            # Handle ISO format datetime strings
            if 'T' in dt_string:
                return datetime.fromisoformat(dt_string)
            else:
                # Handle SQLite datetime format
                return datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            return None
    
    def __repr__(self) -> str:
        """
        String representation for debugging.
        Demonstrates: __repr__ magic method.
        """
        return (f"Case(id={self.id}, case_code='{self.case_code}', "
                f"title='{self.title}', status='{self.status}')")
    
    def __str__(self) -> str:
        """
        User-friendly string representation.
        Demonstrates: __str__ magic method.
        """
        return f"Case {self.case_code}: {self.title} [{self.status}]"
    
    def __eq__(self, other: object) -> bool:
        """
        Check equality based on case_code.
        Demonstrates: __eq__ magic method for custom equality.
        """
        if not isinstance(other, Case):
            return False
        return self.case_code == other.case_code
    
    def __hash__(self) -> int:
        """
        Hash based on case_code for use in sets/dicts.
        Demonstrates: __hash__ magic method.
        """
        return hash(self.case_code)
    
    def is_active(self) -> bool:
        """
        Check if the case is still active.
        
        Returns:
            True if case is open or under review
        """
        return self.status in ('open', 'under_review')
    
    def is_closed(self) -> bool:
        """
        Check if the case is closed.
        
        Returns:
            True if case status is closed
        """
        return self.status == 'closed'
    
    def update_status(self, new_status: str) -> None:
        """
        Update the case status.
        
        Args:
            new_status: New status value
        """
        self.status = new_status
        self.updated_at = datetime.now()
