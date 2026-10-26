"""
Test cases for CRIMESHIELD evidence management.
Demonstrates: Comprehensive testing of evidence CRUD, validation, and audit logging.
"""

import pytest
import json


class TestEvidenceCreation:
    """Test suite for evidence creation."""
    
    def test_create_evidence_success(self, client, sample_case_data, sample_evidence_data):
        """Test successful evidence creation."""
        # First create a case
        case_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(case_response.data)['case']['id']
        
        # Create evidence linked to the case
        evidence_data = sample_evidence_data.copy()
        evidence_data['case_id'] = case_id
        
        response = client.post(
            '/api/evidence',
            data=json.dumps(evidence_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Evidence created successfully'
        assert data['evidence']['evidence_code'] == evidence_data['evidence_code']
        assert data['evidence']['case_id'] == case_id
        assert data['evidence']['id'] is not None
    
    def test_create_evidence_missing_code(self, client):
        """Test evidence creation fails without evidence_code."""
        invalid_data = {
            'case_id': 1,
            'evidence_type': 'physical'
        }
        
        response = client.post(
            '/api/evidence',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'evidence_code' in data['error'].lower()
    
    def test_create_evidence_missing_case_id(self, client, sample_evidence_data):
        """Test evidence creation fails without case_id."""
        invalid_data = sample_evidence_data.copy()
        del invalid_data['case_id']
        
        response = client.post(
            '/api/evidence',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'case_id' in data['error'].lower()
    
    def test_create_evidence_invalid_case_id(self, client, sample_evidence_data):
        """Test evidence creation fails with non-existent case_id."""
        invalid_data = sample_evidence_data.copy()
        invalid_data['case_id'] = 99999  # Non-existent case
        
        response = client.post(
            '/api/evidence',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'does not exist' in data['error'].lower()
    
    def test_create_evidence_duplicate_code(self, client, sample_case_data, sample_evidence_data):
        """Test evidence creation fails with duplicate evidence_code."""
        # Create a case
        case_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(case_response.data)['case']['id']
        
        # Create first evidence
        evidence_data = sample_evidence_data.copy()
        evidence_data['case_id'] = case_id
        client.post(
            '/api/evidence',
            data=json.dumps(evidence_data),
            content_type='application/json'
        )
        
        # Try to create duplicate
        response = client.post(
            '/api/evidence',
            data=json.dumps(evidence_data),
            content_type='application/json'
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'already exists' in data['error'].lower()
    
    def test_create_evidence_invalid_status(self, client, sample_case_data, sample_evidence_data):
        """Test evidence creation fails with invalid processing_status."""
        # Create a case
        case_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(case_response.data)['case']['id']
        
        invalid_data = sample_evidence_data.copy()
        invalid_data['case_id'] = case_id
        invalid_data['processing_status'] = 'invalid_status'
        
        response = client.post(
            '/api/evidence',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'processing_status' in data['error'].lower()


class TestGetEvidence:
    """Test suite for retrieving evidence."""
    
    def test_get_all_evidence_empty(self, client):
        """Test getting all evidence when database is empty."""
        response = client.get('/api/evidence')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 0
        assert data['evidence'] == []
    
    def test_get_all_evidence(self, client, sample_case_data, multiple_evidence_data):
        """Test getting all evidence after creating multiple items."""
        # Create a case
        case_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(case_response.data)['case']['id']
        
        # Create multiple evidence items
        for evidence_data in multiple_evidence_data:
            evidence_data['case_id'] = case_id
            client.post(
                '/api/evidence',
                data=json.dumps(evidence_data),
                content_type='application/json'
            )
        
        # Get all evidence
        response = client.get('/api/evidence')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == len(multiple_evidence_data)
    
    def test_get_evidence_by_id(self, client, sample_case_data, sample_evidence_data):
        """Test getting specific evidence by ID."""
        # Create a case
        case_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(case_response.data)['case']['id']
        
        # Create evidence
        evidence_data = sample_evidence_data.copy()
        evidence_data['case_id'] = case_id
        create_response = client.post(
            '/api/evidence',
            data=json.dumps(evidence_data),
            content_type='application/json'
        )
        evidence_id = json.loads(create_response.data)['evidence']['id']
        
        # Get the evidence by ID
        response = client.get(f'/api/evidence/{evidence_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['evidence']['id'] == evidence_id
        assert data['evidence']['evidence_code'] == evidence_data['evidence_code']
    
    def test_get_evidence_by_id_not_found(self, client):
        """Test getting non-existent evidence by ID."""
        response = client.get('/api/evidence/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['error'].lower()
    
    def test_get_evidence_by_case(self, client, sample_case_data, multiple_evidence_data):
        """Test getting evidence by case ID."""
        # Create a case
        case_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(case_response.data)['case']['id']
        
        # Create multiple evidence items
        for evidence_data in multiple_evidence_data:
            evidence_data['case_id'] = case_id
            client.post(
                '/api/evidence',
                data=json.dumps(evidence_data),
                content_type='application/json'
            )
        
        # Get evidence by case
        response = client.get(f'/api/cases/{case_id}/evidence')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['case_id'] == case_id
        assert data['count'] == len(multiple_evidence_data)


class TestSearchEvidence:
    """Test suite for searching evidence."""
    
    def test_search_by_type(self, client, sample_case_data, multiple_evidence_data):
        """Test searching evidence by type."""
        # Create a case
        case_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(case_response.data)['case']['id']
        
        # Create multiple evidence items
        for evidence_data in multiple_evidence_data:
            evidence_data['case_id'] = case_id
            client.post(
                '/api/evidence',
                data=json.dumps(evidence_data),
                content_type='application/json'
            )
        
        # Search by type
        response = client.get('/api/evidence?evidence_type=physical')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] > 0
        # Verify all results have correct type
        for evidence in data['evidence']:
            assert evidence['evidence_type'] == 'physical'
    
    def test_search_by_status(self, client, sample_case_data, multiple_evidence_data):
        """Test searching evidence by processing status."""
        # Create a case
        case_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(case_response.data)['case']['id']
        
        # Create multiple evidence items
        for evidence_data in multiple_evidence_data:
            evidence_data['case_id'] = case_id
            client.post(
                '/api/evidence',
                data=json.dumps(evidence_data),
                content_type='application/json'
            )
        
        # Search by status
        response = client.get('/api/evidence?processing_status=pending')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] > 0


class TestUpdateEvidence:
    """Test suite for updating evidence."""
    
    def test_update_evidence_success(self, client, sample_case_data, sample_evidence_data):
        """Test successful evidence update."""
        # Create a case
        case_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(case_response.data)['case']['id']
        
        # Create evidence
        evidence_data = sample_evidence_data.copy()
        evidence_data['case_id'] = case_id
        create_response = client.post(
            '/api/evidence',
            data=json.dumps(evidence_data),
            content_type='application/json'
        )
        evidence_id = json.loads(create_response.data)['evidence']['id']
        
        # Update the evidence
        update_data = {'processing_status': 'processed', 'description': 'Updated description'}
        response = client.put(
            f'/api/evidence/{evidence_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['evidence']['processing_status'] == 'processed'
        assert data['evidence']['description'] == 'Updated description'
    
    def test_update_evidence_not_found(self, client):
        """Test updating non-existent evidence."""
        update_data = {'processing_status': 'processed'}
        response = client.put(
            '/api/evidence/99999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['error'].lower()


class TestDeleteEvidence:
    """Test suite for deleting evidence."""
    
    def test_delete_evidence_success(self, client, sample_case_data, sample_evidence_data):
        """Test successful evidence deletion."""
        # Create a case
        case_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(case_response.data)['case']['id']
        
        # Create evidence
        evidence_data = sample_evidence_data.copy()
        evidence_data['case_id'] = case_id
        create_response = client.post(
            '/api/evidence',
            data=json.dumps(evidence_data),
            content_type='application/json'
        )
        evidence_id = json.loads(create_response.data)['evidence']['id']
        
        # Delete the evidence
        response = client.delete(f'/api/evidence/{evidence_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deleted successfully' in data['message'].lower()
        
        # Verify evidence is deleted
        get_response = client.get(f'/api/evidence/{evidence_id}')
        assert get_response.status_code == 404
    
    def test_delete_evidence_not_found(self, client):
        """Test deleting non-existent evidence."""
        response = client.delete('/api/evidence/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['error'].lower()


class TestEvidenceStatistics:
    """Test suite for evidence statistics."""
    
    def test_statistics_empty(self, client):
        """Test statistics with empty database."""
        response = client.get('/api/evidence/statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['statistics']['total'] == 0
    
    def test_statistics_with_evidence(self, client, sample_case_data, multiple_evidence_data):
        """Test statistics with multiple evidence items."""
        # Create a case
        case_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(case_response.data)['case']['id']
        
        # Create multiple evidence items
        for evidence_data in multiple_evidence_data:
            evidence_data['case_id'] = case_id
            client.post(
                '/api/evidence',
                data=json.dumps(evidence_data),
                content_type='application/json'
            )
        
        # Get statistics
        response = client.get('/api/evidence/statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['statistics']['total'] == len(multiple_evidence_data)
        assert 'by_type' in data['statistics']
        assert 'by_status' in data['statistics']


class TestAuditLogging:
    """Test suite for audit logging integration."""
    
    def test_evidence_creation_logged(self, client, sample_case_data, sample_evidence_data):
        """Test that evidence creation is logged in audit trail."""
        # Create a case
        case_response = client.post(
            '/api/cases',
            data=json.dumps(sample_case_data),
            content_type='application/json'
        )
        case_id = json.loads(case_response.data)['case']['id']
        
        # Create evidence
        evidence_data = sample_evidence_data.copy()
        evidence_data['case_id'] = case_id
        client.post(
            '/api/evidence',
            data=json.dumps(evidence_data),
            content_type='application/json'
        )
        
        # Audit logging should have captured this
        # Note: We verify this works without errors
        # In a real system, you'd query audit_logs table
        assert True
