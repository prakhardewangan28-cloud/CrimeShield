"""
Test cases for CRIMESHIELD connection analysis.
Demonstrates: Testing of analysis, matching rules, and connection management.
"""

import pytest
import json
from crimeshield.utils.connection_graph import ConnectionGraph, build_graph_from_connections


class TestConnectionAnalysis:
    """Test suite for connection analysis."""
    
    def test_run_analysis_empty(self, client):
        """Test analysis with no evidence."""
        response = client.post('/api/analysis/run')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['results']['status'] == 'completed'
        assert data['results']['evidence_count'] == 0
        assert data['results']['connections_found'] == 0
    
    def test_location_match(self, client, sample_case_data):
        """Test location-based matching."""
        # Create two cases
        case1 = client.post('/api/cases', data=json.dumps(sample_case_data), content_type='application/json')
        case1_id = json.loads(case1.data)['case']['id']
        
        case2_data = sample_case_data.copy()
        case2_data['case_code'] = 'TEST-2024-002'
        case2 = client.post('/api/cases', data=json.dumps(case2_data), content_type='application/json')
        case2_id = json.loads(case2.data)['case']['id']
        
        # Create evidence with matching location
        evidence1 = {
            'evidence_code': 'EVD-001',
            'case_id': case1_id,
            'evidence_type': 'physical',
            'location_reference': '123 Main Street',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence1), content_type='application/json')
        
        evidence2 = {
            'evidence_code': 'EVD-002',
            'case_id': case2_id,
            'evidence_type': 'physical',
            'location_reference': '123 Main Street',  # Same location
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence2), content_type='application/json')
        
        # Run analysis
        response = client.post('/api/analysis/run')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['results']['connections_found'] >= 1
        
        # Verify connection was created
        connections = client.get('/api/connections')
        conn_data = json.loads(connections.data)
        assert conn_data['count'] >= 1
        
        # Check connection type
        location_matches = [c for c in conn_data['connections'] if c['connection_type'] == 'location_match']
        assert len(location_matches) >= 1
    
    def test_person_match(self, client, sample_case_data):
        """Test person-based matching."""
        # Create two cases
        case1 = client.post('/api/cases', data=json.dumps(sample_case_data), content_type='application/json')
        case1_id = json.loads(case1.data)['case']['id']
        
        case2_data = sample_case_data.copy()
        case2_data['case_code'] = 'TEST-2024-003'
        case2 = client.post('/api/cases', data=json.dumps(case2_data), content_type='application/json')
        case2_id = json.loads(case2.data)['case']['id']
        
        # Create evidence with matching person
        evidence1 = {
            'evidence_code': 'EVD-003',
            'case_id': case1_id,
            'evidence_type': 'document',
            'person_reference': 'John Doe',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence1), content_type='application/json')
        
        evidence2 = {
            'evidence_code': 'EVD-004',
            'case_id': case2_id,
            'evidence_type': 'document',
            'person_reference': 'john doe',  # Different case
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence2), content_type='application/json')
        
        # Run analysis
        response = client.post('/api/analysis/run')
        assert response.status_code == 200
        
        # Verify person match found
        connections = client.get('/api/connections')
        conn_data = json.loads(connections.data)
        person_matches = [c for c in conn_data['connections'] if c['connection_type'] == 'person_match']
        assert len(person_matches) >= 1
    
    def test_phone_match(self, client, sample_case_data):
        """Test phone number matching with normalization."""
        # Create two cases
        case1 = client.post('/api/cases', data=json.dumps(sample_case_data), content_type='application/json')
        case1_id = json.loads(case1.data)['case']['id']
        
        case2_data = sample_case_data.copy()
        case2_data['case_code'] = 'TEST-2024-004'
        case2 = client.post('/api/cases', data=json.dumps(case2_data), content_type='application/json')
        case2_id = json.loads(case2.data)['case']['id']
        
        # Create evidence with matching phone (different formats)
        evidence1 = {
            'evidence_code': 'EVD-005',
            'case_id': case1_id,
            'evidence_type': 'digital',
            'phone_reference': '+1 (555) 123-4567',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence1), content_type='application/json')
        
        evidence2 = {
            'evidence_code': 'EVD-006',
            'case_id': case2_id,
            'evidence_type': 'digital',
            'phone_reference': '555-123-4567',  # Different format, same number
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence2), content_type='application/json')
        
        # Run analysis
        response = client.post('/api/analysis/run')
        assert response.status_code == 200
        
        # Verify phone match found
        connections = client.get('/api/connections')
        conn_data = json.loads(connections.data)
        phone_matches = [c for c in conn_data['connections'] if c['connection_type'] == 'phone_match']
        assert len(phone_matches) >= 1
    
    def test_empty_values_not_matched(self, client, sample_case_data):
        """Test that empty values don't create false matches."""
        # Create two cases
        case1 = client.post('/api/cases', data=json.dumps(sample_case_data), content_type='application/json')
        case1_id = json.loads(case1.data)['case']['id']
        
        case2_data = sample_case_data.copy()
        case2_data['case_code'] = 'TEST-2024-005'
        case2 = client.post('/api/cases', data=json.dumps(case2_data), content_type='application/json')
        case2_id = json.loads(case2.data)['case']['id']
        
        # Create evidence with empty/null references
        evidence1 = {
            'evidence_code': 'EVD-007',
            'case_id': case1_id,
            'evidence_type': 'physical',
            'location_reference': '',  # Empty
            'person_reference': None,  # Null
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence1), content_type='application/json')
        
        evidence2 = {
            'evidence_code': 'EVD-008',
            'case_id': case2_id,
            'evidence_type': 'physical',
            'location_reference': '',  # Empty
            'person_reference': None,  # Null
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence2), content_type='application/json')
        
        # Run analysis
        response = client.post('/api/analysis/run')
        assert response.status_code == 200
        
        # Verify no connections created for empty values
        connections = client.get('/api/connections')
        conn_data = json.loads(connections.data)
        # Should have no new connections from empty values
        assert conn_data['count'] == 0
    
    def test_duplicate_prevention(self, client, sample_case_data):
        """Test that running analysis multiple times doesn't create duplicates."""
        # Create cases and evidence with matches
        case1 = client.post('/api/cases', data=json.dumps(sample_case_data), content_type='application/json')
        case1_id = json.loads(case1.data)['case']['id']
        
        case2_data = sample_case_data.copy()
        case2_data['case_code'] = 'TEST-2024-006'
        case2 = client.post('/api/cases', data=json.dumps(case2_data), content_type='application/json')
        case2_id = json.loads(case2.data)['case']['id']
        
        evidence1 = {
            'evidence_code': 'EVD-009',
            'case_id': case1_id,
            'evidence_type': 'physical',
            'location_reference': 'Test Location',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence1), content_type='application/json')
        
        evidence2 = {
            'evidence_code': 'EVD-010',
            'case_id': case2_id,
            'evidence_type': 'physical',
            'location_reference': 'Test Location',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence2), content_type='application/json')
        
        # Run analysis first time
        response1 = client.post('/api/analysis/run')
        data1 = json.loads(response1.data)
        connections_created_first = data1['results']['connections_created']
        
        # Run analysis second time
        response2 = client.post('/api/analysis/run')
        data2 = json.loads(response2.data)
        connections_created_second = data2['results']['connections_created']
        
        # Second run should create 0 new connections (duplicates prevented)
        assert connections_created_second == 0


class TestConnectionRetrieval:
    """Test suite for retrieving connections."""
    
    def test_get_all_connections_empty(self, client):
        """Test getting connections when none exist."""
        response = client.get('/api/connections')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 0
        assert data['connections'] == []
    
    def test_get_connection_by_id(self, client, sample_case_data):
        """Test getting specific connection by ID."""
        # Setup: Create cases, evidence, and run analysis
        case1 = client.post('/api/cases', data=json.dumps(sample_case_data), content_type='application/json')
        case1_id = json.loads(case1.data)['case']['id']
        
        case2_data = sample_case_data.copy()
        case2_data['case_code'] = 'TEST-2024-007'
        case2 = client.post('/api/cases', data=json.dumps(case2_data), content_type='application/json')
        case2_id = json.loads(case2.data)['case']['id']
        
        evidence1 = {
            'evidence_code': 'EVD-011',
            'case_id': case1_id,
            'evidence_type': 'physical',
            'location_reference': 'Specific Location',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence1), content_type='application/json')
        
        evidence2 = {
            'evidence_code': 'EVD-012',
            'case_id': case2_id,
            'evidence_type': 'physical',
            'location_reference': 'Specific Location',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence2), content_type='application/json')
        
        client.post('/api/analysis/run')
        
        # Get all connections and pick first one
        connections = client.get('/api/connections')
        conn_data = json.loads(connections.data)
        assert conn_data['count'] > 0
        
        connection_id = conn_data['connections'][0]['id']
        
        # Get specific connection
        response = client.get(f'/api/connections/{connection_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['connection']['id'] == connection_id
    
    def test_get_connections_for_case(self, client, sample_case_data):
        """Test getting connections for a specific case."""
        # Setup
        case1 = client.post('/api/cases', data=json.dumps(sample_case_data), content_type='application/json')
        case1_id = json.loads(case1.data)['case']['id']
        
        case2_data = sample_case_data.copy()
        case2_data['case_code'] = 'TEST-2024-008'
        case2 = client.post('/api/cases', data=json.dumps(case2_data), content_type='application/json')
        case2_id = json.loads(case2.data)['case']['id']
        
        evidence1 = {
            'evidence_code': 'EVD-013',
            'case_id': case1_id,
            'evidence_type': 'physical',
            'location_reference': 'Case Location',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence1), content_type='application/json')
        
        evidence2 = {
            'evidence_code': 'EVD-014',
            'case_id': case2_id,
            'evidence_type': 'physical',
            'location_reference': 'Case Location',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence2), content_type='application/json')
        
        client.post('/api/analysis/run')
        
        # Get connections for case 1
        response = client.get(f'/api/cases/{case1_id}/connections')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['case_id'] == case1_id
        assert data['count'] > 0


class TestConnectionReview:
    """Test suite for connection review workflow."""
    
    def test_review_connection_success(self, client, sample_case_data):
        """Test successful connection review."""
        # Setup
        case1 = client.post('/api/cases', data=json.dumps(sample_case_data), content_type='application/json')
        case1_id = json.loads(case1.data)['case']['id']
        
        case2_data = sample_case_data.copy()
        case2_data['case_code'] = 'TEST-2024-009'
        case2 = client.post('/api/cases', data=json.dumps(case2_data), content_type='application/json')
        case2_id = json.loads(case2.data)['case']['id']
        
        evidence1 = {
            'evidence_code': 'EVD-015',
            'case_id': case1_id,
            'evidence_type': 'physical',
            'location_reference': 'Review Location',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence1), content_type='application/json')
        
        evidence2 = {
            'evidence_code': 'EVD-016',
            'case_id': case2_id,
            'evidence_type': 'physical',
            'location_reference': 'Review Location',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence2), content_type='application/json')
        
        client.post('/api/analysis/run')
        
        # Get connection
        connections = client.get('/api/connections')
        conn_data = json.loads(connections.data)
        connection_id = conn_data['connections'][0]['id']
        
        # Review connection
        review_data = {
            'review_status': 'confirmed_for_review',
            'review_notes': 'Requires further investigation'
        }
        response = client.patch(
            f'/api/connections/{connection_id}/review',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['connection']['review_status'] == 'confirmed_for_review'
        assert data['connection']['review_notes'] == 'Requires further investigation'
        assert data['connection']['reviewed_at'] is not None
    
    def test_review_invalid_status(self, client, sample_case_data):
        """Test review with invalid status."""
        # Setup
        case1 = client.post('/api/cases', data=json.dumps(sample_case_data), content_type='application/json')
        case1_id = json.loads(case1.data)['case']['id']
        
        case2_data = sample_case_data.copy()
        case2_data['case_code'] = 'TEST-2024-010'
        case2 = client.post('/api/cases', data=json.dumps(case2_data), content_type='application/json')
        case2_id = json.loads(case2.data)['case']['id']
        
        evidence1 = {
            'evidence_code': 'EVD-017',
            'case_id': case1_id,
            'evidence_type': 'physical',
            'location_reference': 'Invalid Location',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence1), content_type='application/json')
        
        evidence2 = {
            'evidence_code': 'EVD-018',
            'case_id': case2_id,
            'evidence_type': 'physical',
            'location_reference': 'Invalid Location',
            'processing_status': 'pending'
        }
        client.post('/api/evidence', data=json.dumps(evidence2), content_type='application/json')
        
        client.post('/api/analysis/run')
        
        # Get connection
        connections = client.get('/api/connections')
        conn_data = json.loads(connections.data)
        connection_id = conn_data['connections'][0]['id']
        
        # Try invalid review status
        review_data = {
            'review_status': 'invalid_status'
        }
        response = client.patch(
            f'/api/connections/{connection_id}/review',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestConnectionGraph:
    """Test suite for recursive graph traversal."""
    
    def test_find_path(self):
        """Test finding path between cases."""
        graph = ConnectionGraph()
        
        # Create a path: 1 -> 2 -> 3
        graph.add_connection(1, 2, {'type': 'location'})
        graph.add_connection(2, 3, {'type': 'person'})
        
        # Find path from 1 to 3
        path = graph.find_path(1, 3, max_depth=5)
        assert path is not None
        assert 1 in path
        assert 3 in path
        assert len(path) == 3  # [1, 2, 3]
    
    def test_cycle_detection(self):
        """Test cycle detection in graph."""
        graph = ConnectionGraph()
        
        # Create a cycle: 1 -> 2 -> 3 -> 1
        graph.add_connection(1, 2, {'type': 'location'})
        graph.add_connection(2, 3, {'type': 'person'})
        graph.add_connection(3, 1, {'type': 'phone'})
        
        # Detect cycle
        cycle = graph.detect_cycle(1, max_length=10)
        assert cycle is not None
        assert len(cycle) > 2
    
    def test_max_depth_limit(self):
        """Test that max depth prevents unbounded recursion."""
        graph = ConnectionGraph()
        
        # Create a long chain
        for i in range(1, 11):
            graph.add_connection(i, i + 1, {'type': 'location'})
        
        # Try to find path with depth limit
        path = graph.find_path(1, 11, max_depth=5)
        # Should not find path due to depth limit
        assert path is None
    
    def test_get_connected_cases(self):
        """Test getting all connected cases within depth."""
        graph = ConnectionGraph()
        
        # Create connections
        graph.add_connection(1, 2, {'type': 'location'})
        graph.add_connection(1, 3, {'type': 'person'})
        graph.add_connection(2, 4, {'type': 'phone'})
        
        # Get connected cases (depth 1)
        connected = graph.get_connected_cases(1, max_depth=1)
        assert 2 in connected
        assert 3 in connected
        assert 4 not in connected  # Too deep
        
        # Get connected cases (depth 2)
        connected2 = graph.get_connected_cases(1, max_depth=2)
        assert 2 in connected2
        assert 3 in connected2
        assert 4 in connected2  # Now reachable


class TestConnectionStatistics:
    """Test suite for connection statistics."""
    
    def test_statistics_empty(self, client):
        """Test statistics with no connections."""
        response = client.get('/api/connections/statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['statistics']['total'] == 0
        assert data['statistics']['pending'] == 0
