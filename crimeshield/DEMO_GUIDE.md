# CRIMESHIELD Demonstration Guide

This guide provides step-by-step instructions for demonstrating CRIMESHIELD during a college viva or presentation.

## Table of Contents
1. [Setup and Launch](#setup-and-launch)
2. [Demonstration Workflow](#demonstration-workflow)
3. [API Testing Examples](#api-testing-examples)
4. [Test Data](#test-data)
5. [Expected Results](#expected-results)
6. [Common Issues and Solutions](#common-issues-and-solutions)
7. [Viva Questions and Answers](#viva-questions-and-answers)

---

## Setup and Launch

### Prerequisites
```powershell
# Verify Python version (must be 3.12+)
python --version

# Navigate to project directory
cd crimeshield

# Activate virtual environment (if created)
.\venv\Scripts\Activate.ps1

# Verify dependencies installed
pip list | Select-String -Pattern "Flask|pytest"
```

### Launch Application
```powershell
# Start the Flask server
python app.py
```

**Expected Output:**
```
============================================================
CRIMESHIELD - Criminal Network Analysis System v3.0
============================================================
Database: C:\...\crimeshield\crimeshield.db
Debug Mode: True
... [API endpoints listed] ...
Server starting on http://127.0.0.1:5000
============================================================
```

---

## Demonstration Workflow

### Step 1: Verify System Health

**Action:** Check application status
```powershell
curl http://127.0.0.1:5000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "CRIMESHIELD API",
  "version": "1.0.0"
}
```

### Step 2: Create Investigation Cases

**Action:** Create first case
```powershell
curl -X POST http://127.0.0.1:5000/api/cases `
  -H "Content-Type: application/json" `
  -d '{\"case_code\":\"CASE-2024-001\",\"title\":\"Downtown Incident\",\"description\":\"Investigation of downtown incident\",\"location\":\"Main Street Plaza\",\"status\":\"open\"}'
```

**Action:** Create second case
```powershell
curl -X POST http://127.0.0.1:5000/api/cases `
  -H "Content-Type: application/json" `
  -d '{\"case_code\":\"CASE-2024-002\",\"title\":\"Shopping District Event\",\"description\":\"Investigation of shopping district event\",\"location\":\"Market Square\",\"status\":\"open\"}'
```

**Expected:** HTTP 201 with case details

### Step 3: Add Evidence with References

**Action:** Add evidence to Case 1 with location reference
```powershell
curl -X POST http://127.0.0.1:5000/api/evidence `
  -H "Content-Type: application/json" `
  -d '{\"evidence_code\":\"EVD-2024-001\",\"case_id\":1,\"evidence_type\":\"physical\",\"description\":\"Security footage\",\"location_reference\":\"Main Street Plaza\",\"person_reference\":\"John Smith\",\"phone_reference\":\"+1-555-1234\",\"processing_status\":\"pending\"}'
```

**Action:** Add evidence to Case 2 with MATCHING references
```powershell
curl -X POST http://127.0.0.1:5000/api/evidence `
  -H "Content-Type: application/json" `
  -d '{\"evidence_code\":\"EVD-2024-002\",\"case_id\":2,\"evidence_type\":\"digital\",\"description\":\"Phone records\",\"location_reference\":\"Main Street Plaza\",\"person_reference\":\"john smith\",\"phone_reference\":\"555-1234\",\"processing_status\":\"pending\"}'
```

**Key Point:** Note the matching location, person (different case), and phone (different format)

### Step 4: Run Connection Analysis

**Action:** Trigger analysis
```powershell
curl -X POST http://127.0.0.1:5000/api/analysis/run
```

**Expected Response:**
```json
{
  "message": "Analysis completed successfully",
  "results": {
    "status": "completed",
    "evidence_count": 2,
    "connections_found": 3,
    "connections_created": 3
  }
}
```

**Explanation:** Three connections found:
1. Location match: "Main Street Plaza"
2. Person match: "john smith" (normalized)
3. Phone match: "5551234" (normalized)

### Step 5: Review Connections

**Action:** Get all connections
```powershell
curl http://127.0.0.1:5000/api/connections
```

**Expected:** List of connections with:
- `connection_type`: "location_match", "person_match", "phone_match"
- `connection_value`: The matching value
- `explanation`: Human-readable description
- `review_status`: "pending"

**Action:** Get connections for a specific case
```powershell
curl http://127.0.0.1:5000/api/cases/1/connections
```

### Step 6: Review a Connection

**Action:** Update review status (use actual connection ID from previous step)
```powershell
curl -X PATCH http://127.0.0.1:5000/api/connections/1/review `
  -H "Content-Type: application/json" `
  -d '{\"review_status\":\"confirmed_for_review\",\"review_notes\":\"Requires further investigation\"}'
```

**Expected:** Updated connection with:
- `review_status`: "confirmed_for_review"
- `reviewed_at`: timestamp
- `review_notes`: Your notes

### Step 7: Generate Reports

**Action:** Get report metadata
```powershell
curl http://127.0.0.1:5000/api/reports/cases/1
```

**Action:** Export CSV report
```powershell
curl "http://127.0.0.1:5000/api/reports/cases/1/export?format=csv" -o case_1_report.csv
```

**Action:** Export TXT report
```powershell
curl "http://127.0.0.1:5000/api/reports/cases/1/export?format=txt" -o case_1_report.txt
```

**Action:** Open generated files to show formatted reports

### Step 8: View Statistics

**Action:** System-wide statistics
```powershell
curl http://127.0.0.1:5000/api/reports/summary
```

**Action:** Case statistics
```powershell
curl http://127.0.0.1:5000/api/cases/statistics
```

**Action:** Connection statistics
```powershell
curl http://127.0.0.1:5000/api/connections/statistics
```

---

## Test Data

### Fictional Test Cases

```json
{
  "case_code": "CASE-2024-003",
  "title": "Warehouse Investigation",
  "description": "Investigation at warehouse facility",
  "location": "Industrial Park",
  "status": "open"
}
```

### Fictional Test Evidence

```json
{
  "evidence_code": "EVD-2024-003",
  "case_id": 1,
  "evidence_type": "document",
  "description": "Shipping manifest",
  "location_reference": "Warehouse District",
  "person_reference": "Jane Doe",
  "phone_reference": "+1 (555) 987-6543",
  "processing_status": "pending"
}
```

### Matching Scenarios

**Scenario 1: Location Match**
- Evidence 1: `location_reference`: "Main Street Plaza"
- Evidence 2: `location_reference`: "main street plaza" (different case)
- **Result:** Match found (normalized to lowercase)

**Scenario 2: Person Match**
- Evidence 1: `person_reference`: "John Smith"
- Evidence 2: `person_reference`: "  john   smith  " (extra spaces)
- **Result:** Match found (normalized whitespace)

**Scenario 3: Phone Match**
- Evidence 1: `phone_reference`: "+1 (555) 123-4567"
- Evidence 2: `phone_reference`: "555-123-4567"
- Evidence 3: `phone_reference`: "5551234567"
- **Result:** All match (normalized to digits only)

---

## Expected Results

### Connection Analysis
- **Empty values NOT matched**: `""`, `null`, `"   "` do not create false connections
- **Self-connections prevented**: Database constraint ensures `case_id_1 < case_id_2`
- **Duplicates prevented**: UNIQUE constraint on `(case_id_1, case_id_2, type, value)`
- **Normalization works**: Different formatting of same value matches

### Audit Logging
- Evidence creation logged
- Connection reviews logged
- Analysis runs logged

### Report Generation
- CSV files have proper headers and structure
- TXT files are human-readable
- Files saved in `reports/` directory only
- Filenames are sanitized

---

## Common Issues and Solutions

### Issue 1: Port Already in Use
**Error:** `Address already in use`
**Solution:**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000
# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### Issue 2: Database Locked
**Error:** `database is locked`
**Solution:** Close any other connections to the database, restart the application

### Issue 3: Module Not Found
**Error:** `ModuleNotFoundError: No module named 'flask'`
**Solution:**
```powershell
pip install -r requirements.txt
```

### Issue 4: Tests Fail
**Solution:**
```powershell
# Delete test databases
Remove-Item test_crimeshield.db -ErrorAction SilentlyContinue
# Run tests again
pytest -v
```

---

## Viva Questions and Answers

### Q1: What is the purpose of CRIMESHIELD?
**A:** CRIMESHIELD is a Criminal Network Analysis System designed to help investigators manage investigation cases and evidence. It uses rule-based analysis to identify potential connections between cases based on shared information like locations, persons, or phone numbers. These connections are investigative leads for human review, not proof of wrongdoing.

### Q2: What Advanced Python concepts does this project demonstrate?
**A:** The project demonstrates 25+ concepts including:
- Decorators (logging, audit)
- Context managers (database connections)
- Generators (batch processing)
- Inheritance (Evidence inherits from BaseEntity)
- Type hints (throughout)
- Strategy pattern (matching rules)
- Recursion (connection graph traversal)
- Custom exceptions
- List/dict comprehensions
- *args and **kwargs

See ADVANCED_PYTHON_MAPPING.md for complete mapping.

### Q3: How does the connection analysis work?
**A:** The analysis service:
1. Fetches all evidence from the database
2. Applies matching rules (location, person, phone) using the Strategy pattern
3. Normalizes values (lowercase, remove spaces/punctuation)
4. Identifies evidence pairs with matching normalized values
5. Creates connection records linking the related cases
6. Prevents duplicates using database constraints

### Q4: What is the Strategy pattern and where is it used?
**A:** The Strategy pattern allows interchangeable algorithms. In CRIMESHIELD, `MatchingRule` is an abstract base class with three implementations:
- `LocationMatchingRule`: Matches location references
- `PersonMatchingRule`: Matches person references  
- `PhoneMatchingRule`: Matches phone references

Each has its own normalization logic. New matching rules can be added without modifying existing code.

### Q5: How do you prevent SQL injection?
**A:** All SQL queries use parameterized queries (placeholders `?`) instead of string formatting:
```python
query = "SELECT * FROM cases WHERE id = ?"
cursor.execute(query, (case_id,))
```
Never: `query = f"SELECT * FROM cases WHERE id = {case_id}"` (vulnerable!)

### Q6: What is a decorator and give an example?
**A:** A decorator wraps a function to add behavior. Example - `@log_request`:
```python
@log_request
def get_cases():
    # This function's execution is logged automatically
```
The decorator logs the request, executes the function, logs the response, and handles errors - all transparently.

### Q7: Explain the difference between a class method and static method.
**A:**
- **Static method** (`@staticmethod`): No access to class or instance. Pure utility function.
  ```python
  @staticmethod
  def _parse_datetime(dt_string):
      # Doesn't need self or cls
  ```

- **Class method** (`@classmethod`): Receives the class as first parameter (`cls`).
  ```python
  @classmethod
  def from_dict(cls, data):
      return cls(...)  # Can create instances
  ```

### Q8: What is a context manager and why use it?
**A:** Context managers ensure resources are properly acquired and released using `with`:
```python
with get_db_connection(db_path) as conn:
    cursor = conn.cursor()
    # ... use connection ...
# Connection automatically closed, even if error occurs
```

Prevents resource leaks and handles cleanup in the `__exit__` method.

### Q9: How does the recursive graph traversal work?
**A:** `ConnectionGraph.find_path()` uses depth-first search with:
- **Base case 1**: Found target → return path
- **Base case 2**: Max depth reached → return None
- **Base case 3**: Already visited (cycle) → return None
- **Recursive case**: Explore each neighbor

Safeguards prevent infinite recursion and detect cycles.

### Q10: What security measures are implemented?
**A:**
1. **SQL Injection Prevention**: Parameterized queries
2. **Path Traversal Prevention**: Filename sanitization in reports
3. **Input Validation**: All API inputs validated
4. **Foreign Key Enforcement**: Database referential integrity
5. **No eval/exec**: Never execute user-provided code
6. **Safe Logging**: Sensitive data not logged
7. **Database Constraints**: Self-connection prevention, duplicate prevention

### Q11: Why use SQLite instead of MySQL/PostgreSQL?
**A:** For this educational project:
- **Zero configuration**: No server setup required
- **Portable**: Single file database
- **Fast for small datasets**: Perfect for demonstrations
- **Python built-in**: No external dependencies

Production systems would use PostgreSQL/MySQL for scalability and concurrent access.

### Q12: What is the purpose of the audit_logs table?
**A:** Audit logs track important operations:
- Who did what (action)
- On which entity (entity_type, entity_id)
- When (created_at)
- Additional context (details JSON)

Essential for:
- Accountability
- Debugging
- Compliance
- Security investigations

### Q13: How do you handle database transactions?
**A:** Context managers with commit/rollback:
```python
with get_db_connection(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()  # Explicit commit
    # Rollback happens automatically on exception
```

### Q14: What is the difference between inheritance and composition?
**A:** 
- **Inheritance** ("is-a"): `Evidence` IS A `BaseEntity`
  ```python
  class Evidence(BaseEntity):
      # Inherits methods and attributes
  ```

- **Composition** ("has-a"): `EvidenceService` HAS A `database connection`
  ```python
  class EvidenceService:
      def __init__(self, db_path):
          self.db_path = db_path  # Composition
  ```

### Q15: Why separate routes, services, and models?
**A:** **Separation of Concerns:**
- **Models**: Data structures (Case, Evidence, Connection)
- **Services**: Business logic (CRUD, validation, analysis)
- **Routes**: HTTP handling (request/response, status codes)

Benefits:
- Easier testing
- Code reusability
- Clear responsibilities
- Maintainability

---

## Testing Demonstration

```powershell
# Run all tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_connections.py -v

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run single test
pytest tests/test_cases.py::TestCreateCase::test_create_case_success -v
```

**Expected:** All tests pass with green checkmarks

---

## Cleanup After Demo

```powershell
# Stop the Flask server (Ctrl+C)

# Optional: Clean database
Remove-Item crimeshield.db

# Optional: Clean reports
Remove-Item reports/*.csv
Remove-Item reports/*.txt

# Deactivate virtual environment
deactivate
```

---

## Presentation Tips

1. **Start with overview**: Explain project purpose and features
2. **Show architecture**: Diagram showing models → services → routes
3. **Demonstrate live**: Run API calls showing each feature
4. **Explain code**: Open key files and explain Advanced Python concepts
5. **Run tests**: Show comprehensive test suite passing
6. **Discuss security**: Explain safety measures implemented
7. **Mention limitations**: Acknowledge what would be needed for production

**Remember:** This is a **demonstration** system using **fictional data**. Real deployment requires authentication, authorization, encryption, legal compliance, and security hardening.
