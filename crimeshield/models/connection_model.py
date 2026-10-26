"""
Connection model for CRIMESHIELD.
Demonstrates: Model for relationship data between cases.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import json


class Connection:
    """
    Represents a potential connection between two criminal investigation cases.
    
    IMPORTANT: A connection is an investigative lead based on shared information,
    not proof of guilt or wrongdoing. Every connection requires human review.
    """
    
    # Valid review statuses
    VALID_REVIEW_STATUSES = ('pending', 'confirmed_for_review', 'dismissed')
    
    def __init__(
        self,
        case_id_1: int,
        case_id_2: int,
        connection_type: str,
        connection_value: str,
        explanation: str,
        review_status: str = "pending",
        connection_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        reviewed_at: Optional[datetime] = None,
        review_notes: Optional[str] = None
    ) -> None:
        """
        Initialize a Connection instance.
        
        Args:
            case_id_1: First case ID (must be < case_id_2 for normalization)
            case_id_2: Second case ID
            connection_type: Type of connection (location, person, phone)
            connection_value: The matching value
            explanation: Human-readable explanation
            review_status: Review status
            connection_id: Database ID
            created_at: Creation timestamp
            reviewed_at: Review timestamp
            review_notes: Notes from review
        """
        # Normalize case IDs (ensure case_id_1 < case_id_2)
        if case_id_1 > case_id_2:
            case_id_1, case_id_2 = case_id_2, case_id_1
        
        self.id: Optional[int] = connection_id
        self.case_id_1: int = case_id_1
        self.case_id_2: int = case_id_2
        self.connection_type: str = connection_type
        self.connection_value: str = connection_value
        self.explanation: str = explanation
        self.review_status: str = review_status
        self.created_at: Optional[datetime] = created_at
        self.reviewed_at: Optional[datetime] = reviewed_at
        self.review_notes: Optional[str] = review_notes
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert connection object to dictionary.
        
        Returns:
            Dictionary representation of the connection
        """
        return {
            "id": self.id,
            "case_id_1": self.case_id_1,
            "case_id_2": self.case_id_2,
            "connection_type": self.connection_type,
            "connection_value": self.connection_value,
            "explanation": self.explanation,
            "review_status": self.review_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "review_notes": self.review_notes
        }
    
    def to_json(self) -> str:
        """Convert connection to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Connection':
        """Create a Connection instance from a dictionary."""
        return cls(
            case_id_1=data.get('case_id_1', 0),
            case_id_2=data.get('case_id_2', 0),
            connection_type=data.get('connection_type', ''),
            connection_value=data.get('connection_value', ''),
            explanation=data.get('explanation', ''),
            review_status=data.get('review_status', 'pending'),
            connection_id=data.get('id'),
            created_at=cls._parse_datetime(data.get('created_at')),
            reviewed_at=cls._parse_datetime(data.get('reviewed_at')),
            review_notes=data.get('review_notes')
        )
    
    @staticmethod
    def _parse_datetime(dt_string: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object."""
        if not dt_string:
            return None
        
        try:
            if 'T' in dt_string:
                return datetime.fromisoformat(dt_string)
            else:
                return datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            return None
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"Connection between cases {self.case_id_1} and {self.case_id_2}: {self.connection_type} [{self.review_status}]"
    
    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return (f"Connection(id={self.id}, case_id_1={self.case_id_1}, "
                f"case_id_2={self.case_id_2}, type='{self.connection_type}')")
    
    def is_pending(self) -> bool:
        """Check if connection is pending review."""
        return self.review_status == 'pending'
    
    def is_confirmed(self) -> bool:
        """Check if connection is confirmed for review."""
        return self.review_status == 'confirmed_for_review'
    
    def is_dismissed(self) -> bool:
        """Check if connection was dismissed."""
        return self.review_status == 'dismissed'
    
    def update_review_status(
        self,
        new_status: str,
        review_notes: Optional[str] = None
    ) -> None:
        """
        Update the review status.
        
        Args:
            new_status: New review status
            review_notes: Optional review notes
            
        Raises:
            ValueError: If status is invalid
        """
        if new_status not in self.VALID_REVIEW_STATUSES:
            raise ValueError(
                f"Invalid status. Must be one of: {', '.join(self.VALID_REVIEW_STATUSES)}"
            )
        
        self.review_status = new_status
        self.reviewed_at = datetime.now()
        if review_notes:
            self.review_notes = review_notes
