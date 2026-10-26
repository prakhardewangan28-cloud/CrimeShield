"""
Evidence model for CRIMESHIELD.
Demonstrates: Inheritance, super(), method overriding, and advanced OOP concepts.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import json
from abc import ABC, abstractmethod


# ============================================================================
# Base Entity Class - For Inheritance Demonstration
# ============================================================================

class BaseEntity(ABC):
    """
    Abstract base class for all entities in CRIMESHIELD.
    Demonstrates: Abstract base class, inheritance foundation.
    
    This provides common functionality for all entities (Case, Evidence).
    """
    
    def __init__(self, entity_id: Optional[int] = None, created_at: Optional[datetime] = None) -> None:
        """
        Initialize base entity.
        
        Args:
            entity_id: Database ID
            created_at: Creation timestamp
        """
        self.id: Optional[int] = entity_id
        self.created_at: Optional[datetime] = created_at
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entity to dictionary.
        Demonstrates: Abstract method that must be implemented by subclasses.
        """
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate entity data.
        Demonstrates: Abstract method for validation.
        """
        pass
    
    def to_json(self) -> str:
        """
        Convert entity to JSON string.
        Demonstrates: Concrete method inherited by all subclasses.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)
    
    def __repr__(self) -> str:
        """Base representation for debugging."""
        return f"{self.__class__.__name__}(id={self.id})"


# ============================================================================
# Evidence Class - Inherits from BaseEntity
# ============================================================================

class Evidence(BaseEntity):
    """
    Represents physical or digital evidence in a criminal investigation.
    Demonstrates: Inheritance, method overriding, super(), and OOP principles.
    
    Inherits from BaseEntity and implements required abstract methods.
    """
    
    # Class variable - shared across all instances
    VALID_PROCESSING_STATUSES = ('pending', 'processed', 'flagged')
    
    def __init__(
        self,
        evidence_code: str,
        case_id: int,
        evidence_type: str,
        description: Optional[str] = None,
        location_reference: Optional[str] = None,
        person_reference: Optional[str] = None,
        phone_reference: Optional[str] = None,
        processing_status: str = "pending",
        evidence_id: Optional[int] = None,
        created_at: Optional[datetime] = None
    ) -> None:
        """
        Initialize an Evidence instance.
        Demonstrates: Calling parent constructor with super().
        
        Args:
            evidence_code: Unique evidence identifier
            case_id: Foreign key to case
            evidence_type: Type of evidence (physical, digital, document, etc.)
            description: Detailed description
            location_reference: Location where evidence was found
            person_reference: Person associated with evidence
            phone_reference: Phone number reference
            processing_status: Current processing status
            evidence_id: Database ID
            created_at: Creation timestamp
        """
        # Call parent class constructor using super()
        super().__init__(entity_id=evidence_id, created_at=created_at)
        
        self.evidence_code: str = evidence_code
        self.case_id: int = case_id
        self.evidence_type: str = evidence_type
        self.description: Optional[str] = description
        self.location_reference: Optional[str] = location_reference
        self.person_reference: Optional[str] = person_reference
        self.phone_reference: Optional[str] = phone_reference
        self.processing_status: str = processing_status
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert evidence object to dictionary.
        Demonstrates: Method overriding - implementing abstract method from parent.
        
        Returns:
            Dictionary representation of the evidence
        """
        return {
            "id": self.id,
            "evidence_code": self.evidence_code,
            "case_id": self.case_id,
            "evidence_type": self.evidence_type,
            "description": self.description,
            "location_reference": self.location_reference,
            "person_reference": self.person_reference,
            "phone_reference": self.phone_reference,
            "processing_status": self.processing_status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def validate(self) -> bool:
        """
        Validate evidence data.
        Demonstrates: Implementing abstract method from parent.
        
        Returns:
            True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if not self.evidence_code or not self.evidence_code.strip():
            raise ValueError("Evidence code is required")
        
        if not self.case_id or self.case_id <= 0:
            raise ValueError("Valid case_id is required")
        
        if not self.evidence_type or not self.evidence_type.strip():
            raise ValueError("Evidence type is required")
        
        if self.processing_status not in self.VALID_PROCESSING_STATUSES:
            raise ValueError(
                f"Processing status must be one of: {', '.join(self.VALID_PROCESSING_STATUSES)}"
            )
        
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Evidence':
        """
        Create an Evidence instance from a dictionary.
        Demonstrates: Class method for alternative constructor.
        
        Args:
            data: Dictionary containing evidence data
            
        Returns:
            New Evidence instance
        """
        return cls(
            evidence_code=data.get('evidence_code', ''),
            case_id=data.get('case_id', 0),
            evidence_type=data.get('evidence_type', ''),
            description=data.get('description'),
            location_reference=data.get('location_reference'),
            person_reference=data.get('person_reference'),
            phone_reference=data.get('phone_reference'),
            processing_status=data.get('processing_status', 'pending'),
            evidence_id=data.get('id'),
            created_at=cls._parse_datetime(data.get('created_at'))
        )
    
    @staticmethod
    def _parse_datetime(dt_string: Optional[str]) -> Optional[datetime]:
        """
        Parse datetime string to datetime object.
        Demonstrates: Static method for utility function.
        
        Args:
            dt_string: ISO format datetime string
            
        Returns:
            datetime object or None
        """
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
        """
        User-friendly string representation.
        Demonstrates: Method overriding (__str__ magic method).
        """
        return f"Evidence {self.evidence_code}: {self.evidence_type} [{self.processing_status}]"
    
    def __repr__(self) -> str:
        """
        Developer-friendly string representation.
        Demonstrates: Method overriding (__repr__ magic method) and super() usage.
        """
        # We could call parent's __repr__ if needed: super().__repr__()
        return (f"Evidence(id={self.id}, evidence_code='{self.evidence_code}', "
                f"case_id={self.case_id}, type='{self.evidence_type}')")
    
    def __eq__(self, other: object) -> bool:
        """
        Check equality based on evidence_code.
        Demonstrates: __eq__ magic method for custom equality.
        """
        if not isinstance(other, Evidence):
            return False
        return self.evidence_code == other.evidence_code
    
    def __hash__(self) -> int:
        """
        Hash based on evidence_code for use in sets/dicts.
        Demonstrates: __hash__ magic method.
        """
        return hash(self.evidence_code)
    
    def is_pending(self) -> bool:
        """
        Check if evidence is pending processing.
        
        Returns:
            True if status is pending
        """
        return self.processing_status == 'pending'
    
    def is_processed(self) -> bool:
        """
        Check if evidence has been processed.
        
        Returns:
            True if status is processed
        """
        return self.processing_status == 'processed'
    
    def is_flagged(self) -> bool:
        """
        Check if evidence has been flagged for review.
        
        Returns:
            True if status is flagged
        """
        return self.processing_status == 'flagged'
    
    def update_status(self, new_status: str) -> None:
        """
        Update the processing status.
        
        Args:
            new_status: New status value
            
        Raises:
            ValueError: If status is invalid
        """
        if new_status not in self.VALID_PROCESSING_STATUSES:
            raise ValueError(
                f"Invalid status. Must be one of: {', '.join(self.VALID_PROCESSING_STATUSES)}"
            )
        self.processing_status = new_status
    
    def has_references(self) -> bool:
        """
        Check if evidence has any references (location, person, or phone).
        
        Returns:
            True if any reference field is populated
        """
        return any([
            self.location_reference,
            self.person_reference,
            self.phone_reference
        ])
    
    def get_reference_summary(self) -> Dict[str, Optional[str]]:
        """
        Get a summary of all references.
        Demonstrates: Dictionary creation from object attributes.
        
        Returns:
            Dictionary with all reference fields
        """
        return {
            'location': self.location_reference,
            'person': self.person_reference,
            'phone': self.phone_reference
        }


# ============================================================================
# Specialized Evidence Types - Further Inheritance
# ============================================================================

class DigitalEvidence(Evidence):
    """
    Specialized evidence class for digital evidence.
    Demonstrates: Multi-level inheritance.
    """
    
    def __init__(self, *args, file_hash: Optional[str] = None, 
                 file_size: Optional[int] = None, **kwargs) -> None:
        """
        Initialize digital evidence with additional fields.
        Demonstrates: *args, **kwargs, and super() in multi-level inheritance.
        """
        super().__init__(*args, **kwargs)
        self.file_hash: Optional[str] = file_hash
        self.file_size: Optional[int] = file_size
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Override to_dict to include digital-specific fields.
        Demonstrates: Method overriding with super() to extend parent behavior.
        """
        # Call parent's to_dict and extend it
        data = super().to_dict()
        data['file_hash'] = self.file_hash
        data['file_size'] = self.file_size
        return data
    
    def __str__(self) -> str:
        """Override string representation for digital evidence."""
        base_str = super().__str__()
        if self.file_hash:
            return f"{base_str} (Hash: {self.file_hash[:8]}...)"
        return base_str
