"""
Database module for CRIMESHIELD.
Demonstrates: Context managers, exception handling, and database operations.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Manages SQLite database connections and schema.
    Demonstrates: Class-based design and context manager protocol.
    """
    
    def __init__(self, db_path: Path) -> None:
        """
        Initialize database connection manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path: Path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """
        Create a connection to the database.
        
        Returns:
            SQLite connection object
        """
        try:
            # Enable foreign key support (important for referential integrity)
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Return rows as dictionaries for easier handling
            conn.row_factory = sqlite3.Row
            
            self.connection = conn
            logger.info(f"Connected to database: {self.db_path}")
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
    
    def __enter__(self) -> sqlite3.Connection:
        """Context manager entry - demonstrates __enter__ magic method."""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - demonstrates __exit__ magic method."""
        self.close()


@contextmanager
def get_db_connection(db_path: Path):
    """
    Context manager for database connections.
    Demonstrates: Generator-based context manager using @contextmanager decorator.
    
    Usage:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cases")
    
    Args:
        db_path: Path to the database file
        
    Yields:
        Database connection object
    """
    conn = None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def init_database(db_path: Path) -> None:
    """
    Initialize the database schema.
    Creates the cases, evidence, and audit_logs tables if they don't exist.
    
    Args:
        db_path: Path to the database file
    """
    # SQL schema for cases table
    create_cases_table = """
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_code TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        description TEXT,
        location TEXT,
        status TEXT NOT NULL DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CHECK (status IN ('open', 'under_review', 'closed'))
    )
    """
    
    # SQL schema for evidence table with foreign key to cases
    create_evidence_table = """
    CREATE TABLE IF NOT EXISTS evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evidence_code TEXT NOT NULL UNIQUE,
        case_id INTEGER NOT NULL,
        evidence_type TEXT NOT NULL,
        description TEXT,
        location_reference TEXT,
        person_reference TEXT,
        phone_reference TEXT,
        processing_status TEXT NOT NULL DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
        CHECK (processing_status IN ('pending', 'processed', 'flagged'))
    )
    """
    
    # SQL schema for audit_logs table
    create_audit_logs_table = """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id INTEGER,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # SQL schema for connections table
    # Demonstrates: Normalized case pair storage and self-connection prevention
    create_connections_table = """
    CREATE TABLE IF NOT EXISTS connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id_1 INTEGER NOT NULL,
        case_id_2 INTEGER NOT NULL,
        connection_type TEXT NOT NULL,
        connection_value TEXT NOT NULL,
        explanation TEXT NOT NULL,
        review_status TEXT NOT NULL DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP,
        review_notes TEXT,
        FOREIGN KEY (case_id_1) REFERENCES cases(id) ON DELETE CASCADE,
        FOREIGN KEY (case_id_2) REFERENCES cases(id) ON DELETE CASCADE,
        CHECK (review_status IN ('pending', 'confirmed_for_review', 'dismissed')),
        CHECK (case_id_1 < case_id_2),
        UNIQUE (case_id_1, case_id_2, connection_type, connection_value)
    )
    """
    
    # Create indexes for faster searches
    create_indexes = """
    CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);
    CREATE INDEX IF NOT EXISTS idx_cases_location ON cases(location);
    CREATE INDEX IF NOT EXISTS idx_cases_code ON cases(case_code);
    CREATE INDEX IF NOT EXISTS idx_evidence_case_id ON evidence(case_id);
    CREATE INDEX IF NOT EXISTS idx_evidence_type ON evidence(evidence_type);
    CREATE INDEX IF NOT EXISTS idx_evidence_status ON evidence(processing_status);
    CREATE INDEX IF NOT EXISTS idx_evidence_code ON evidence(evidence_code);
    CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);
    CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
    CREATE INDEX IF NOT EXISTS idx_connections_case1 ON connections(case_id_1);
    CREATE INDEX IF NOT EXISTS idx_connections_case2 ON connections(case_id_2);
    CREATE INDEX IF NOT EXISTS idx_connections_review_status ON connections(review_status);
    CREATE INDEX IF NOT EXISTS idx_connections_type ON connections(connection_type);
    """
    
    try:
        # Using context manager for automatic connection handling
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute(create_cases_table)
            cursor.execute(create_evidence_table)
            cursor.execute(create_audit_logs_table)
            cursor.execute(create_connections_table)
            
            # Execute index creation statements
            for statement in create_indexes.strip().split(';'):
                if statement.strip():
                    cursor.execute(statement)
            
            conn.commit()
            logger.info(f"Database initialized successfully at {db_path}")
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def drop_database(db_path: Path) -> None:
    """
    Drop all tables in the database (useful for testing).
    
    Args:
        db_path: Path to the database file
    """
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            # Drop in reverse order of dependencies
            cursor.execute("DROP TABLE IF EXISTS connections")
            cursor.execute("DROP TABLE IF EXISTS audit_logs")
            cursor.execute("DROP TABLE IF EXISTS evidence")
            cursor.execute("DROP TABLE IF EXISTS cases")
            conn.commit()
            logger.info(f"Database tables dropped at {db_path}")
    except sqlite3.Error as e:
        logger.error(f"Failed to drop database: {e}")
        raise
