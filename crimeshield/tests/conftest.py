"""
Pytest configuration and fixtures for CRIMESHIELD tests.
Demonstrates: Pytest fixtures, test database setup, and test client creation.
"""

import pytest
from pathlib import Path
import tempfile
import os

from crimeshield.app import create_app
from crimeshield.config import TestConfig
from crimeshield.database import init_database, drop_database


@pytest.fixture(scope='function')
def test_db_path():
    """
    Fixture to create a temporary test database.
    Demonstrates: Pytest fixture with setup and teardown.
    
    Yields:
        Path to temporary test database
    """
    # Create a temporary file for the test database
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as tmp_file:
        db_path = Path(tmp_file.name)
    
    # Initialize the database
    init_database(db_path)
    
    # Yield the path to the test
    yield db_path
    
    # Cleanup: remove the test database after test completes
    try:
        if db_path.exists():
            os.unlink(db_path)
    except Exception:
        pass


@pytest.fixture(scope='function')
def app(test_db_path):
    """
    Fixture to create a Flask test application.
    Demonstrates: Flask test app fixture with custom configuration.
    
    Args:
        test_db_path: Path to test database (from fixture)
    
    Yields:
        Flask application instance
    """
    # Create custom test configuration
    class TestConfigCustom(TestConfig):
        DATABASE_PATH = test_db_path
    
    # Create the application
    app = create_app(TestConfigCustom)
    
    # Set testing mode
    app.config['TESTING'] = True
    
    yield app


@pytest.fixture(scope='function')
def client(app):
    """
    Fixture to create a Flask test client.
    Demonstrates: Test client fixture for API testing.
    
    Args:
        app: Flask application (from fixture)
    
    Yields:
        Flask test client
    """
    return app.test_client()


@pytest.fixture(scope='function')
def sample_case_data():
    """
    Fixture providing sample case data.
    Demonstrates: Data fixture for test cases.
    
    Returns:
        Dictionary with sample case data
    """
    return {
        'case_code': 'TEST-2024-001',
        'title': 'Test Investigation Case',
        'description': 'This is a test case for investigation',
        'location': 'Test City',
        'status': 'open'
    }


@pytest.fixture(scope='function')
def multiple_cases_data():
    """
    Fixture providing multiple sample cases.
    Demonstrates: List comprehension in fixtures.
    
    Returns:
        List of case dictionaries
    """
    return [
        {
            'case_code': f'TEST-2024-{str(i).zfill(3)}',
            'title': f'Test Case {i}',
            'description': f'Description for test case {i}',
            'location': 'Test City' if i % 2 == 0 else 'Another City',
            'status': 'open' if i % 3 == 0 else 'under_review'
        }
        for i in range(1, 6)
    ]


@pytest.fixture(scope='function')
def sample_evidence_data():
    """
    Fixture providing sample evidence data.
    Demonstrates: Data fixture for evidence test cases.
    
    Returns:
        Dictionary with sample evidence data
    """
    return {
        'evidence_code': 'EVD-2024-001',
        'case_id': 1,  # Will be updated in tests
        'evidence_type': 'physical',
        'description': 'Test evidence description',
        'location_reference': 'Crime Scene A',
        'person_reference': 'John Doe',
        'phone_reference': '+1234567890',
        'processing_status': 'pending'
    }


@pytest.fixture(scope='function')
def multiple_evidence_data():
    """
    Fixture providing multiple sample evidence items.
    Demonstrates: List comprehension for test data generation.
    
    Returns:
        List of evidence dictionaries
    """
    evidence_types = ['physical', 'digital', 'document', 'physical', 'digital']
    statuses = ['pending', 'processed', 'flagged', 'pending', 'pending']
    
    return [
        {
            'evidence_code': f'EVD-2024-{str(i).zfill(3)}',
            'case_id': 1,  # Will be updated in tests
            'evidence_type': evidence_types[i-1],
            'description': f'Evidence item {i} description',
            'location_reference': f'Location {i}',
            'person_reference': f'Person {i}' if i % 2 == 0 else None,
            'phone_reference': f'+123456789{i}' if i % 3 == 0 else None,
            'processing_status': statuses[i-1]
        }
        for i in range(1, 6)
    ]
