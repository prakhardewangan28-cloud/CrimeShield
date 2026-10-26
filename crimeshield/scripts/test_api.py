"""
Live API Testing Script for CRIMESHIELD
Tests the running Flask server with real HTTP requests.

Usage:
    python scripts/test_api.py
    python scripts/test_api.py --base-url http://127.0.0.1:5000
"""

import requests
import json
import sys
import argparse
from typing import Dict, Any, Tuple
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class APITester:
    """Test CRIMESHIELD API endpoints."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        """Initialize the API tester with base URL."""
        self.base_url = base_url.rstrip('/')
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.created_resources = {
            'cases': [],
            'evidence': [],
            'connections': []
        }
    
    def print_header(self, text: str):
        """Print a section header."""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    def print_test(self, test_name: str, passed: bool, details: str = ""):
        """Print test result."""
        if passed:
            status = f"{Colors.GREEN}✓ PASS{Colors.RESET}"
            self.passed += 1
        else:
            status = f"{Colors.RED}✗ FAIL{Colors.RESET}"
            self.failed += 1
        
        print(f"{status} | {test_name}")
        if details:
            print(f"       {Colors.YELLOW}{details}{Colors.RESET}")
    
    def print_skip(self, test_name: str, reason: str):
        """Print skipped test."""
        self.skipped += 1
        print(f"{Colors.YELLOW}⊘ SKIP{Colors.RESET} | {test_name} ({reason})")
    
    def test_server_running(self) -> bool:
        """Test if server is running."""
        self.print_header("SERVER CONNECTION TEST")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.print_test("Server is running", response.status_code == 200)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            self.print_test("Server is running", False, 
                          f"Could not connect to {self.base_url}")
            print(f"\n{Colors.RED}ERROR: Server is not running!{Colors.RESET}")
            print(f"Please start the server with: python app.py")
            return False
        except Exception as e:
            self.print_test("Server is running", False, str(e))
            return False
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        self.print_header("HEALTH CHECK ENDPOINT")
        
        try:
            response = requests.get(f"{self.base_url}/api/health")
            passed = response.status_code == 200
            self.print_test("GET /api/health", passed, 
                          f"Status: {response.status_code}")
            
            if passed:
                data = response.json()
                has_status = 'status' in data
                self.print_test("Response contains 'status'", has_status,
                              f"Status value: {data.get('status')}")
        except Exception as e:
            self.print_test("GET /api/health", False, str(e))
    
    def test_case_management(self):
        """Test case management endpoints."""
        self.print_header("CASE MANAGEMENT ENDPOINTS")
        
        # Test 1: Create a valid case
        try:
            case_data = {
                "case_code": f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}-001",
                "title": "API Test Case 1",
                "description": "Fictional test case for API testing",
                "location": "40.7128,-74.0060",  # NYC coordinates
                "status": "open"
            }
            response = requests.post(f"{self.base_url}/api/cases", json=case_data)
            passed = response.status_code == 201
            self.print_test("POST /api/cases (valid data)", passed,
                          f"Status: {response.status_code}")
            
            if passed:
                result = response.json()
                if 'case' in result and 'id' in result['case']:
                    case_id = result['case']['id']
                    self.created_resources['cases'].append(case_id)
                    self.print_test("Response contains case with ID", True,
                                  f"Case ID: {case_id}")
                else:
                    self.print_test("Response contains case with ID", False,
                                  "Missing case or id in response")
        except Exception as e:
            self.print_test("POST /api/cases (valid data)", False, str(e))
        
        # Test 2: Create case with missing required field
        try:
            invalid_data = {
                "case_code": f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}-002",
                "description": "Missing title field"
            }
            response = requests.post(f"{self.base_url}/api/cases", json=invalid_data)
            passed = response.status_code == 400
            self.print_test("POST /api/cases (missing required field)", passed,
                          f"Status: {response.status_code}, Expected: 400")
        except Exception as e:
            self.print_test("POST /api/cases (missing required field)", False, str(e))
        
        # Test 3: Create case with invalid JSON
        try:
            response = requests.post(f"{self.base_url}/api/cases",
                                   data="not valid json",
                                   headers={'Content-Type': 'application/json'})
            passed = response.status_code == 400
            self.print_test("POST /api/cases (invalid JSON)", passed,
                          f"Status: {response.status_code}, Expected: 400")
        except Exception as e:
            self.print_test("POST /api/cases (invalid JSON)", False, str(e))
        
        # Test 4: Get all cases
        try:
            response = requests.get(f"{self.base_url}/api/cases")
            passed = response.status_code == 200
            self.print_test("GET /api/cases", passed,
                          f"Status: {response.status_code}")
            
            if passed:
                data = response.json()
                has_cases = 'cases' in data and isinstance(data['cases'], list)
                self.print_test("Response contains cases array", has_cases,
                              f"Count: {data.get('count', 0)}")
        except Exception as e:
            self.print_test("GET /api/cases", False, str(e))
        
        # Test 5: Get case by ID
        if self.created_resources['cases']:
            try:
                case_id = self.created_resources['cases'][0]
                response = requests.get(f"{self.base_url}/api/cases/{case_id}")
                passed = response.status_code == 200
                self.print_test(f"GET /api/cases/{case_id}", passed,
                              f"Status: {response.status_code}")
                
                if passed:
                    data = response.json()
                    has_case = 'case' in data and data['case']['id'] == case_id
                    self.print_test("Response contains correct case", has_case)
            except Exception as e:
                self.print_test(f"GET /api/cases/{case_id}", False, str(e))
        else:
            self.print_skip("GET /api/cases/<id>", "No case created")
        
        # Test 6: Get non-existent case
        try:
            response = requests.get(f"{self.base_url}/api/cases/999999")
            passed = response.status_code == 404
            self.print_test("GET /api/cases/999999 (non-existent)", passed,
                          f"Status: {response.status_code}, Expected: 404")
        except Exception as e:
            self.print_test("GET /api/cases/999999 (non-existent)", False, str(e))
        
        # Test 7: Update case
        if self.created_resources['cases']:
            try:
                case_id = self.created_resources['cases'][0]
                update_data = {
                    "title": "Updated API Test Case",
                    "status": "under_review"
                }
                response = requests.put(f"{self.base_url}/api/cases/{case_id}",
                                      json=update_data)
                passed = response.status_code == 200
                self.print_test(f"PUT /api/cases/{case_id}", passed,
                              f"Status: {response.status_code}")
            except Exception as e:
                self.print_test(f"PUT /api/cases/{case_id}", False, str(e))
        else:
            self.print_skip("PUT /api/cases/<id>", "No case created")
        
        # Test 8: Search cases
        try:
            response = requests.get(f"{self.base_url}/api/cases?status=open")
            passed = response.status_code == 200
            self.print_test("GET /api/cases?status=open", passed,
                          f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("GET /api/cases?status=open", False, str(e))
        
        # Test 9: Get case statistics
        try:
            response = requests.get(f"{self.base_url}/api/cases/statistics")
            passed = response.status_code == 200
            self.print_test("GET /api/cases/statistics", passed,
                          f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("GET /api/cases/statistics", False, str(e))
    
    def test_evidence_management(self):
        """Test evidence management endpoints."""
        self.print_header("EVIDENCE MANAGEMENT ENDPOINTS")
        
        if not self.created_resources['cases']:
            self.print_skip("All evidence tests", "No case created")
            return
        
        case_id = self.created_resources['cases'][0]
        
        # Test 1: Create valid evidence
        try:
            evidence_data = {
                "evidence_code": f"EVD-{datetime.now().strftime('%Y%m%d%H%M%S')}-001",
                "case_id": case_id,
                "evidence_type": "physical",
                "description": "Test evidence item",
                "location_reference": "40.7589,-73.9851",  # NYC area
                "person_reference": "John Doe",
                "phone_reference": "+1-555-0123",
                "processing_status": "pending"
            }
            response = requests.post(f"{self.base_url}/api/evidence", json=evidence_data)
            passed = response.status_code == 201
            self.print_test("POST /api/evidence (valid data)", passed,
                          f"Status: {response.status_code}")
            
            if passed:
                result = response.json()
                if 'evidence' in result and 'id' in result['evidence']:
                    evidence_id = result['evidence']['id']
                    self.created_resources['evidence'].append(evidence_id)
                    self.print_test("Response contains evidence with ID", True,
                                  f"Evidence ID: {evidence_id}")
        except Exception as e:
            self.print_test("POST /api/evidence (valid data)", False, str(e))
        
        # Test 2: Create evidence with non-existent case
        try:
            invalid_evidence = {
                "evidence_code": f"EVD-{datetime.now().strftime('%Y%m%d%H%M%S')}-002",
                "case_id": 999999,
                "evidence_type": "digital",
                "description": "Should fail"
            }
            response = requests.post(f"{self.base_url}/api/evidence",
                                   json=invalid_evidence)
            passed = response.status_code == 404
            self.print_test("POST /api/evidence (non-existent case)", passed,
                          f"Status: {response.status_code}, Expected: 404")
        except Exception as e:
            self.print_test("POST /api/evidence (non-existent case)", False, str(e))
        
        # Test 3: Get all evidence
        try:
            response = requests.get(f"{self.base_url}/api/evidence")
            passed = response.status_code == 200
            self.print_test("GET /api/evidence", passed,
                          f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("GET /api/evidence", False, str(e))
        
        # Test 4: Get evidence by ID
        if self.created_resources['evidence']:
            try:
                evidence_id = self.created_resources['evidence'][0]
                response = requests.get(f"{self.base_url}/api/evidence/{evidence_id}")
                passed = response.status_code == 200
                self.print_test(f"GET /api/evidence/{evidence_id}", passed,
                              f"Status: {response.status_code}")
            except Exception as e:
                self.print_test(f"GET /api/evidence/{evidence_id}", False, str(e))
        
        # Test 5: Get evidence for case
        try:
            response = requests.get(f"{self.base_url}/api/cases/{case_id}/evidence")
            passed = response.status_code == 200
            self.print_test(f"GET /api/cases/{case_id}/evidence", passed,
                          f"Status: {response.status_code}")
        except Exception as e:
            self.print_test(f"GET /api/cases/{case_id}/evidence", False, str(e))
        
        # Test 6: Update evidence
        if self.created_resources['evidence']:
            try:
                evidence_id = self.created_resources['evidence'][0]
                update_data = {
                    "processing_status": "processed",
                    "description": "Updated evidence description"
                }
                response = requests.put(f"{self.base_url}/api/evidence/{evidence_id}",
                                      json=update_data)
                passed = response.status_code == 200
                self.print_test(f"PUT /api/evidence/{evidence_id}", passed,
                              f"Status: {response.status_code}")
            except Exception as e:
                self.print_test(f"PUT /api/evidence/{evidence_id}", False, str(e))
        
        # Test 7: Get evidence statistics
        try:
            response = requests.get(f"{self.base_url}/api/evidence/statistics")
            passed = response.status_code == 200
            self.print_test("GET /api/evidence/statistics", passed,
                          f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("GET /api/evidence/statistics", False, str(e))
    
    def test_connection_analysis(self):
        """Test connection analysis endpoints."""
        self.print_header("CONNECTION ANALYSIS ENDPOINTS")
        
        if len(self.created_resources['cases']) < 1:
            self.print_skip("All connection tests", "Not enough cases created")
            return
        
        # Create additional test cases and evidence for connection testing
        try:
            # Case 2 with overlapping location
            case2_data = {
                "case_code": f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}-002",
                "title": "API Test Case 2",
                "description": "Second test case",
                "location": "40.7589,-73.9851",  # Near first case
                "status": "open"
            }
            response = requests.post(f"{self.base_url}/api/cases", json=case2_data)
            if response.status_code == 201:
                case2_id = response.json()['case']['id']
                self.created_resources['cases'].append(case2_id)
                
                # Add evidence with same person
                evidence2_data = {
                    "evidence_code": f"EVD-{datetime.now().strftime('%Y%m%d%H%M%S')}-003",
                    "case_id": case2_id,
                    "evidence_type": "testimonial",
                    "description": "Witness statement",
                    "person_reference": "John Doe",  # Same person as case 1
                    "processing_status": "pending"
                }
                requests.post(f"{self.base_url}/api/evidence", json=evidence2_data)
        except Exception as e:
            print(f"       {Colors.YELLOW}Warning: Could not create additional test data: {e}{Colors.RESET}")
        
        # Test 1: Run analysis
        try:
            response = requests.post(f"{self.base_url}/api/analysis/run")
            passed = response.status_code == 200
            self.print_test("POST /api/analysis/run", passed,
                          f"Status: {response.status_code}")
            
            if passed:
                data = response.json()
                has_results = 'results' in data
                self.print_test("Response contains results", has_results)
                if has_results:
                    results = data['results']
                    print(f"       Found {results.get('total_connections', 0)} connection(s)")
        except Exception as e:
            self.print_test("POST /api/analysis/run", False, str(e))
        
        # Test 2: Get all connections
        try:
            response = requests.get(f"{self.base_url}/api/connections")
            passed = response.status_code == 200
            self.print_test("GET /api/connections", passed,
                          f"Status: {response.status_code}")
            
            if passed:
                data = response.json()
                if 'connections' in data and len(data['connections']) > 0:
                    conn_id = data['connections'][0]['id']
                    self.created_resources['connections'].append(conn_id)
        except Exception as e:
            self.print_test("GET /api/connections", False, str(e))
        
        # Test 3: Get connections with filter
        try:
            response = requests.get(f"{self.base_url}/api/connections?review_status=pending")
            passed = response.status_code == 200
            self.print_test("GET /api/connections?review_status=pending", passed,
                          f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("GET /api/connections?review_status=pending", False, str(e))
        
        # Test 4: Get connection by ID
        if self.created_resources['connections']:
            try:
                conn_id = self.created_resources['connections'][0]
                response = requests.get(f"{self.base_url}/api/connections/{conn_id}")
                passed = response.status_code == 200
                self.print_test(f"GET /api/connections/{conn_id}", passed,
                              f"Status: {response.status_code}")
            except Exception as e:
                self.print_test(f"GET /api/connections/{conn_id}", False, str(e))
        
        # Test 5: Get connections for case
        if self.created_resources['cases']:
            try:
                case_id = self.created_resources['cases'][0]
                response = requests.get(f"{self.base_url}/api/cases/{case_id}/connections")
                passed = response.status_code == 200
                self.print_test(f"GET /api/cases/{case_id}/connections", passed,
                              f"Status: {response.status_code}")
            except Exception as e:
                self.print_test(f"GET /api/cases/{case_id}/connections", False, str(e))
        
        # Test 6: Review connection
        if self.created_resources['connections']:
            try:
                conn_id = self.created_resources['connections'][0]
                review_data = {
                    "review_status": "confirmed_for_review",
                    "review_notes": "Verified by API test"
                }
                response = requests.patch(f"{self.base_url}/api/connections/{conn_id}/review",
                                        json=review_data)
                passed = response.status_code == 200
                self.print_test(f"PATCH /api/connections/{conn_id}/review", passed,
                              f"Status: {response.status_code}")
            except Exception as e:
                self.print_test(f"PATCH /api/connections/{conn_id}/review", False, str(e))
        
        # Test 7: Get connection statistics
        try:
            response = requests.get(f"{self.base_url}/api/connections/statistics")
            passed = response.status_code == 200
            self.print_test("GET /api/connections/statistics", passed,
                          f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("GET /api/connections/statistics", False, str(e))
        
        # Test 8: Get connection graph
        if self.created_resources['cases']:
            try:
                case_id = self.created_resources['cases'][0]
                response = requests.get(f"{self.base_url}/api/connections/graph/{case_id}")
                passed = response.status_code == 200
                self.print_test(f"GET /api/connections/graph/{case_id}", passed,
                              f"Status: {response.status_code}")
            except Exception as e:
                self.print_test(f"GET /api/connections/graph/{case_id}", False, str(e))
    
    def test_report_generation(self):
        """Test report generation endpoints."""
        self.print_header("REPORT GENERATION ENDPOINTS")
        
        # Test 1: Get system summary
        try:
            response = requests.get(f"{self.base_url}/api/reports/summary")
            passed = response.status_code == 200
            self.print_test("GET /api/reports/summary", passed,
                          f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("GET /api/reports/summary", False, str(e))
        
        if not self.created_resources['cases']:
            self.print_skip("Case report tests", "No case created")
            return
        
        case_id = self.created_resources['cases'][0]
        
        # Test 2: Get case report info
        try:
            response = requests.get(f"{self.base_url}/api/reports/cases/{case_id}")
            passed = response.status_code == 200
            self.print_test(f"GET /api/reports/cases/{case_id}", passed,
                          f"Status: {response.status_code}")
        except Exception as e:
            self.print_test(f"GET /api/reports/cases/{case_id}", False, str(e))
        
        # Test 3: Export case report (CSV)
        try:
            response = requests.get(f"{self.base_url}/api/reports/cases/{case_id}/export?format=csv")
            passed = response.status_code == 200
            self.print_test(f"GET /api/reports/cases/{case_id}/export?format=csv", passed,
                          f"Status: {response.status_code}")
            if passed:
                is_csv = 'text/csv' in response.headers.get('Content-Type', '')
                self.print_test("CSV file has correct content-type", is_csv)
        except Exception as e:
            self.print_test(f"GET /api/reports/cases/{case_id}/export?format=csv", False, str(e))
        
        # Test 4: Export case report (TXT)
        try:
            response = requests.get(f"{self.base_url}/api/reports/cases/{case_id}/export?format=txt")
            passed = response.status_code == 200
            self.print_test(f"GET /api/reports/cases/{case_id}/export?format=txt", passed,
                          f"Status: {response.status_code}")
            if passed:
                is_txt = 'text/plain' in response.headers.get('Content-Type', '')
                self.print_test("TXT file has correct content-type", is_txt)
        except Exception as e:
            self.print_test(f"GET /api/reports/cases/{case_id}/export?format=txt", False, str(e))
        
        # Test 5: Invalid format
        try:
            response = requests.get(f"{self.base_url}/api/reports/cases/{case_id}/export?format=pdf")
            passed = response.status_code == 400
            self.print_test("Export with invalid format (should fail)", passed,
                          f"Status: {response.status_code}, Expected: 400")
        except Exception as e:
            self.print_test("Export with invalid format", False, str(e))
    
    def cleanup(self):
        """Clean up test data."""
        self.print_header("CLEANUP")
        
        print(f"{Colors.YELLOW}Note: Test data cleanup is optional.{Colors.RESET}")
        print(f"{Colors.YELLOW}Created cases will be visible in the system.{Colors.RESET}")
        print(f"{Colors.YELLOW}You can delete them manually via the API if needed.{Colors.RESET}")
    
    def print_summary(self):
        """Print final test summary."""
        self.print_header("TEST SUMMARY")
        
        total = self.passed + self.failed + self.skipped
        print(f"\nTotal Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        print(f"{Colors.YELLOW}Skipped: {self.skipped}{Colors.RESET}")
        
        if self.failed == 0 and self.passed > 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.RESET}")
        elif self.failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}")
        
        print()
    
    def run_all_tests(self):
        """Run all API tests."""
        print(f"\n{Colors.BOLD}CRIMESHIELD API Testing Script{Colors.RESET}")
        print(f"Testing server at: {self.base_url}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check if server is running
        if not self.test_server_running():
            return False
        
        # Run all test suites
        self.test_health_endpoint()
        self.test_case_management()
        self.test_evidence_management()
        self.test_connection_analysis()
        self.test_report_generation()
        
        # Cleanup
        self.cleanup()
        
        # Print summary
        self.print_summary()
        
        return self.failed == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Test CRIMESHIELD API endpoints')
    parser.add_argument('--base-url', default='http://127.0.0.1:5000',
                       help='Base URL of the API server (default: http://127.0.0.1:5000)')
    
    args = parser.parse_args()
    
    tester = APITester(args.base_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
