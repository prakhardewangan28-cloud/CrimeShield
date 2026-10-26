"""
Analysis service for CRIMESHIELD connection detection.
Demonstrates: Strategy pattern for interchangeable matching rules.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
from abc import ABC, abstractmethod
import re
import logging

from crimeshield.database import get_db_connection
from crimeshield.models.connection_model import Connection
from crimeshield.services.audit_service import AuditLogger
from crimeshield.utils.advanced_python import (
    CrimeshieldException,
    batch_processor
)

logger = logging.getLogger(__name__)


class AnalysisException(CrimeshieldException):
    """Exception raised for analysis-specific errors."""
    pass


# ============================================================================
# Strategy Pattern: Matching Rules
# ============================================================================

class MatchingRule(ABC):
    """
    Abstract base class for matching rules.
    Demonstrates: Strategy pattern - interchangeable algorithms.
    """
    
    @abstractmethod
    def get_match_type(self) -> str:
        """Return the type of match this rule detects."""
        pass
    
    @abstractmethod
    def extract_value(self, evidence: Dict[str, Any]) -> Optional[str]:
        """Extract the relevant value from evidence."""
        pass
    
    @abstractmethod
    def normalize_value(self, value: str) -> str:
        """Normalize the value for comparison."""
        pass
    
    def is_valid_value(self, value: Optional[str]) -> bool:
        """Check if value is valid for matching (not empty or None)."""
        return value is not None and value.strip() != ''
    
    def find_matches(
        self,
        evidence_list: List[Dict[str, Any]]
    ) -> List[tuple[int, int, str, str]]:
        """
        Find all matching pairs in evidence list.
        Demonstrates: Higher-order function using the strategy.
        
        Args:
            evidence_list: List of evidence dictionaries
            
        Returns:
            List of (case_id_1, case_id_2, normalized_value, explanation) tuples
        """
        matches = []
        value_to_cases: Dict[str, Set[int]] = {}
        
        # Group evidence by normalized values
        for evidence in evidence_list:
            raw_value = self.extract_value(evidence)
            if self.is_valid_value(raw_value):
                normalized = self.normalize_value(raw_value)
                case_id = evidence.get('case_id')
                
                if normalized not in value_to_cases:
                    value_to_cases[normalized] = set()
                value_to_cases[normalized].add(case_id)
        
        # Find matches (cases sharing the same normalized value)
        for normalized_value, case_ids in value_to_cases.items():
            if len(case_ids) > 1:
                # Create pairs from matching cases
                case_list = sorted(list(case_ids))
                for i in range(len(case_list)):
                    for j in range(i + 1, len(case_list)):
                        explanation = self._create_explanation(normalized_value)
                        matches.append((
                            case_list[i],
                            case_list[j],
                            normalized_value,
                            explanation
                        ))
        
        return matches
    
    @abstractmethod
    def _create_explanation(self, value: str) -> str:
        """Create human-readable explanation for the match."""
        pass


class LocationMatchingRule(MatchingRule):
    """Matching rule for location references."""
    
    def get_match_type(self) -> str:
        return "location_match"
    
    def extract_value(self, evidence: Dict[str, Any]) -> Optional[str]:
        return evidence.get('location_reference')
    
    def normalize_value(self, value: str) -> str:
        """Normalize location by converting to lowercase and removing extra spaces."""
        return ' '.join(value.lower().split())
    
    def _create_explanation(self, value: str) -> str:
        return f"Both cases have evidence referencing location: '{value}'"


class PersonMatchingRule(MatchingRule):
    """Matching rule for person references."""
    
    def get_match_type(self) -> str:
        return "person_match"
    
    def extract_value(self, evidence: Dict[str, Any]) -> Optional[str]:
        return evidence.get('person_reference')
    
    def normalize_value(self, value: str) -> str:
        """Normalize person name by converting to lowercase and removing extra spaces."""
        return ' '.join(value.lower().split())
    
    def _create_explanation(self, value: str) -> str:
        return f"Both cases have evidence referencing person: '{value}'"


class PhoneMatchingRule(MatchingRule):
    """Matching rule for phone number references."""
    
    def get_match_type(self) -> str:
        return "phone_match"
    
    def extract_value(self, evidence: Dict[str, Any]) -> Optional[str]:
        return evidence.get('phone_reference')
    
    def normalize_value(self, value: str) -> str:
        """Normalize phone by removing non-digit characters."""
        digits_only = re.sub(r'\D', '', value)
        # Keep last 10 digits for comparison (handles country codes)
        return digits_only[-10:] if len(digits_only) >= 10 else digits_only
    
    def _create_explanation(self, value: str) -> str:
        return f"Both cases have evidence referencing phone number: '{value}'"


# ============================================================================
# Analysis Service
# ============================================================================

class AnalysisService:
    """
    Service for analyzing evidence and detecting connections.
    Demonstrates: Service pattern with strategy pattern integration.
    """
    
    def __init__(
        self,
        db_path: Path,
        audit_logger: Optional[AuditLogger] = None
    ) -> None:
        """
        Initialize analysis service.
        
        Args:
            db_path: Path to database
            audit_logger: Optional audit logger
        """
        self.db_path: Path = db_path
        self.audit_logger: Optional[AuditLogger] = audit_logger
        
        # Initialize matching rules (Strategy pattern)
        self.matching_rules: List[MatchingRule] = [
            LocationMatchingRule(),
            PersonMatchingRule(),
            PhoneMatchingRule()
        ]
    
    def run_analysis(self, batch_size: int = 100) -> Dict[str, Any]:
        """
        Run connection analysis on all evidence.
        Demonstrates: Generator-based batch processing.
        
        Args:
            batch_size: Number of evidence items to process per batch
            
        Returns:
            Analysis results summary
        """
        try:
            # Fetch all evidence
            evidence_list = self._fetch_all_evidence()
            
            if not evidence_list:
                logger.info("No evidence found for analysis")
                return {
                    'status': 'completed',
                    'evidence_count': 0,
                    'connections_found': 0,
                    'connections_created': 0
                }
            
            connections_found = []
            
            # Process evidence in batches using generator
            for batch in batch_processor(evidence_list, batch_size):
                batch_connections = self._analyze_batch(batch)
                connections_found.extend(batch_connections)
            
            # Store new connections
            connections_created = self._store_connections(connections_found)
            
            # Audit log the analysis
            if self.audit_logger:
                self.audit_logger.log(
                    action='analysis_run',
                    entity_type='connection',
                    evidence_count=len(evidence_list),
                    connections_found=len(connections_found),
                    connections_created=connections_created
                )
            
            result = {
                'status': 'completed',
                'evidence_count': len(evidence_list),
                'connections_found': len(connections_found),
                'connections_created': connections_created
            }
            
            logger.info(f"Analysis complete: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise AnalysisException(f"Analysis failed: {str(e)}")
    
    def _fetch_all_evidence(self) -> List[Dict[str, Any]]:
        """Fetch all evidence from database."""
        query = "SELECT * FROM evidence"
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error fetching evidence: {e}")
            raise
    
    def _analyze_batch(
        self,
        evidence_batch: List[Dict[str, Any]]
    ) -> List[Connection]:
        """
        Analyze a batch of evidence for connections.
        Demonstrates: Strategy pattern in action.
        
        Args:
            evidence_batch: Batch of evidence to analyze
            
        Returns:
            List of detected connections
        """
        connections = []
        
        # Apply each matching rule (Strategy pattern)
        for rule in self.matching_rules:
            matches = rule.find_matches(evidence_batch)
            
            for case_id_1, case_id_2, value, explanation in matches:
                connection = Connection(
                    case_id_1=case_id_1,
                    case_id_2=case_id_2,
                    connection_type=rule.get_match_type(),
                    connection_value=value,
                    explanation=explanation,
                    review_status='pending'
                )
                connections.append(connection)
        
        return connections
    
    def _store_connections(self, connections: List[Connection]) -> int:
        """
        Store connections in database, avoiding duplicates.
        
        Args:
            connections: List of connections to store
            
        Returns:
            Number of connections actually created
        """
        if not connections:
            return 0
        
        query = """
        INSERT OR IGNORE INTO connections (
            case_id_1, case_id_2, connection_type, connection_value, explanation, review_status
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        created_count = 0
        
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                for connection in connections:
                    cursor.execute(query, (
                        connection.case_id_1,
                        connection.case_id_2,
                        connection.connection_type,
                        connection.connection_value,
                        connection.explanation,
                        connection.review_status
                    ))
                    
                    if cursor.rowcount > 0:
                        created_count += 1
                
                conn.commit()
                logger.info(f"Stored {created_count} new connections")
                return created_count
        
        except sqlite3.Error as e:
            logger.error(f"Error storing connections: {e}")
            raise
