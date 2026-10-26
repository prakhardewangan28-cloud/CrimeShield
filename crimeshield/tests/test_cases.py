"""
Test cases for CRIMESHIELD case management.
Demonstrates: Pytest test organization, test classes, and comprehensive testing.
"""

import pytest
import json


class TestHealthEndpoint:
    """Test suite for health check endpoint."""
    
    def test_health_check(self, client):
        """Test the health check endpoint returns correct response."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'CRIMESHIELD' in data['service']


class TestCreateCase:
    """Test suite for case creation."""
    
    def test_create_case_success(self, client, sample_case_data):
        """Test successful case creation."""
        response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Case created successfully'
        assert data['case']['case_code'] == sample_case_data['case_code']
        assert data['case']['title'] == sample_case_data['title']
        assert data['case']['id'] is not None
    
    def test_create_case_missing_case_code(self, client):
        """Test case creation fails without case_code."""
        invalid_data = {
            'title': 'Test Case',
            'description': 'Test description'
        }
        
        response = client.post(
            '/api/cases',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'case_code' in data['error'].lower()
    
    def test_create_case_missing_title(self, client):
        """Test case creation fails without title."""
        invalid_data = {
            'case_code': 'TEST-2024-001',
            'description': 'Test description'
        }
        
        response = client.post(
            '/api/cases',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'title' in data['error'].lower()
    
    def test_create_case_duplicate_code(self, client, sample_case_data):
        """Test case creation fails with duplicate case_code."""
        # Create first case
        client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        
        # Try to create duplicate
        response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data
        assert 'already exists' in data['error'].lower()
    
    def test_create_case_invalid_status(self, client, sample_case_data):
        """Test case creation fails with invalid status."""
        invalid_data = sample_case_data.copy()
        invalid_data['status'] = 'invalid_status'
        
        response = client.post(
            '/api/cases',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'status' in data['error'].lower()
    
    def test_create_case_invalid_json(self, client):
        """Test case creation fails with invalid JSON."""
        response = client.post(
            '/api/cases',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestGetCases:
    """Test suite for retrieving cases."""
    
    def test_get_all_cases_empty(self, client):
        """Test getting all cases when database is empty."""
        response = client.get('/api/cases')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 0
        assert data['cases'] == []
    
    def test_get_all_cases(self, client, multiple_cases_data):
        """Test getting all cases after creating multiple cases."""
        # Create multiple cases
        for case_data in multiple_cases_data:
            client.post(
                '/api/cases',
                data=json.dumps(case_data),
                content_type='application/json'
            )
        
        # Get all cases
        response = client.get('/api/cases')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == len(multiple_cases_data)
        assert len(data['cases']) == len(multiple_cases_data)
    
    def test_get_case_by_id(self, client, sample_case_data):
        """Test getting a specific case by ID."""
        # Create a case
        create_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(create_response.data)['case']['id']
        
        # Get the case by ID
        response = client.get(f'/api/cases/{case_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['case']['id'] == case_id
        assert data['case']['case_code'] == sample_case_data['case_code']
    
    def test_get_case_by_id_not_found(self, client):
        """Test getting a non-existent case by ID."""
        response = client.get('/api/cases/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error'].lower()
    
    def test_get_case_by_id_invalid(self, client):
        """Test getting a case with invalid ID format."""
        response = client.get('/api/cases/invalid')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_case_by_code(self, client, sample_case_data):
        """Test getting a case by case code."""
        # Create a case
        client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        
        # Get by case code
        response = client.get(f'/api/cases/code/{sample_case_data["case_code"]}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['case']['case_code'] == sample_case_data['case_code']
    
    def test_get_case_by_code_not_found(self, client):
        """Test getting a non-existent case by code."""
        response = client.get('/api/cases/code/NONEXISTENT')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


class TestSearchCases:
    """Test suite for searching cases."""
    
    def test_search_by_status(self, client, multiple_cases_data):
        """Test searching cases by status."""
        # Create multiple cases
        for case_data in multiple_cases_data:
            client.post(
                '/api/cases',
                data=json.dumps(case_data),
                content_type='application/json'
            )
        
        # Search for open cases using lambda to count expected results
        expected_open = len(list(filter(lambda c: c['status'] == 'open', multiple_cases_data)))
        
        response = client.get('/api/cases?status=open')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == expected_open
    
    def test_search_by_location(self, client, multiple_cases_data):
        """Test searching cases by location."""
        # Create multiple cases
        for case_data in multiple_cases_data:
            client.post(
                '/api/cases',
                data=json.dumps(case_data),
                content_type='application/json'
            )
        
        # Search by location
        response = client.get('/api/cases?location=Test City')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] > 0
        # Verify all results contain the search term
        for case in data['cases']:
            assert 'Test City' in case['location']
    
    def test_search_by_title(self, client, multiple_cases_data):
        """Test searching cases by title (partial match)."""
        # Create multiple cases
        for case_data in multiple_cases_data:
            client.post(
                '/api/cases',
                data=json.dumps(case_data),
                content_type='application/json'
            )
        
        # Search by partial title
        response = client.get('/api/cases?title=Case 1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] > 0


class TestUpdateCase:
    """Test suite for updating cases."""
    
    def test_update_case_success(self, client, sample_case_data):
        """Test successful case update."""
        # Create a case
        create_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(create_response.data)['case']['id']
        
        # Update the case
        update_data = {'status': 'under_review', 'title': 'Updated Title'}
        response = client.put(
            f'/api/cases/{case_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['case']['status'] == 'under_review'
        assert data['case']['title'] == 'Updated Title'
        assert data['case']['case_code'] == sample_case_data['case_code']
    
    def test_update_case_not_found(self, client):
        """Test updating a non-existent case."""
        update_data = {'status': 'closed'}
        response = client.put(
            '/api/cases/99999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_case_invalid_status(self, client, sample_case_data):
        """Test updating with invalid status."""
        # Create a case
        create_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(create_response.data)['case']['id']
        
        # Try invalid update
        update_data = {'status': 'invalid_status'}
        response = client.put(
            f'/api/cases/{case_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestDeleteCase:
    """Test suite for deleting cases."""
    
    def test_delete_case_success(self, client, sample_case_data):
        """Test successful case deletion."""
        # Create a case
        create_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(create_response.data)['case']['id']
        
        # Delete the case
        response = client.delete(f'/api/cases/{case_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deleted successfully' in data['message'].lower()
        
        # Verify case is deleted
        get_response = client.get(f'/api/cases/{case_id}')
        assert get_response.status_code == 404
    
    def test_delete_case_not_found(self, client):
        """Test deleting a non-existent case."""
        response = client.delete('/api/cases/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_delete_case_invalid_id(self, client):
        """Test deleting with invalid ID."""
        response = client.delete('/api/cases/invalid')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestStatistics:
    """Test suite for statistics endpoint."""
    
    def test_statistics_empty(self, client):
        """Test statistics with empty database."""
        response = client.get('/api/cases/statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['statistics']['total'] == 0
        assert data['statistics']['open'] == 0
        assert data['statistics']['under_review'] == 0
        assert data['statistics']['closed'] == 0
    
    def test_statistics_with_cases(self, client, multiple_cases_data):
        """Test statistics with multiple cases."""
        # Create multiple cases
        for case_data in multiple_cases_data:
            client.post(
                '/api/cases',
                data=json.dumps(case_data),
                content_type='application/json'
            )
        
        # Get statistics
        response = client.get('/api/cases/statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['statistics']['total'] == len(multiple_cases_data)
        assert data['statistics']['open'] + data['statistics']['under_review'] + data['statistics']['closed'] == len(multiple_cases_data)


class TestRootEndpoint:
    """Test suite for root endpoint."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns API information."""
        response = client.get('/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'CRIMESHIELD' in data['service']
        assert 'endpoints' in data
        assert 'health' in data['endpoints']
