# CRIMESHIELD - Criminal Network Analysis System

**A College-Level Advanced Python Mini-Project**

CRIMESHIELD is a criminal investigation case management system built with Flask, SQLite, and modern Python features. This project demonstrates advanced Python concepts including decorators, context managers, type hints, and comprehensive testing.

## 🎯 Project Purpose

CRIMESHIELD helps investigators organize fictional criminal investigation cases, manage evidence, and identify potential connections between records. **Important:** A detected connection is only a lead for human review, not proof of criminal activity.

## ✨ Features

### Core Features
- **Case Management**: Create, read, update, and delete investigation cases
- **Evidence Management**: Track evidence items linked to cases with metadata
- **Connection Analysis**: Automated detection of connections between cases using:
  - Location matching (with coordinate distance calculation)
  - Person name matching (normalized)
  - Phone number matching (normalized with country codes)
- **Connection Review Workflow**: Review and approve/reject detected connections
- **Network Graph Analysis**: Recursive graph traversal with cycle detection
- **Report Generation**: Export case data in CSV and TXT formats
- **Audit Logging**: Complete audit trail of all system operations

### Technical Features
- **REST API**: Full-featured REST API with proper HTTP status codes
- **Search & Filter**: Search cases by title, location, or status
- **Data Validation**: Input validation with detailed error messages
- **Statistics**: Track case and evidence statistics
- **Request Logging**: Comprehensive request/response logging
- **Database**: SQLite with foreign keys, indexing, and normalization
- **Testing**: 62 comprehensive tests with pytest (100% passing)
- **Security**: Parameterized queries, input validation, path sanitization

## 🐍 Advanced Python Concepts Demonstrated

This project demonstrates **25+ Advanced Python concepts**. See [ADVANCED_PYTHON_MAPPING.md](ADVANCED_PYTHON_MAPPING.md) for exact file locations and line numbers.

### Core Object-Oriented Programming
1. **Classes and Objects** - Case, Evidence, Connection models
2. **Inheritance** - Strategy pattern base classes
3. **Magic Methods** - `__init__`, `__repr__`, `__str__`, `__eq__`, `__hash__`
4. **Properties** - `@property` decorators for getters/setters
5. **Static & Class Methods** - Utility functions and alternative constructors

### Functional Programming
6. **Decorators** - Request logging, function wrapping with `@functools.wraps`
7. **Lambda Functions** - Sorting, filtering, key functions
8. **Closures** - Connection strategy factories
9. **Higher-Order Functions** - Functions returning/accepting functions

### Data Structures & Algorithms
10. **List Comprehensions** - Data transformation and filtering
11. **Dictionary Comprehensions** - Dynamic dict building
12. **Generator Expressions** - Memory-efficient iterations
13. **Sets & Set Operations** - Duplicate prevention, visited tracking
14. **Recursion** - Graph traversal with cycle detection
15. **Graph Algorithms** - Network analysis, DFS/BFS

### Advanced Features
16. **Context Managers** - Database connections with `with` statement
17. **Type Hints** - Function signatures with `typing` module
18. **Dataclasses** - Structured data with validation
19. **Enums** - Status and type constants
20. **Pattern Matching** - Strategy pattern for connection rules
21. **Abstract Base Classes** - `ABC` and `abstractmethod`

### Software Engineering
22. **Modules and Packages** - Organized multi-file structure
23. **Exception Handling** - Try-except with custom error types
24. **Logging** - Application logging with levels
25. **Testing with pytest** - Fixtures, parametrization, mocking
26. **Design Patterns** - Strategy, Factory, Repository patterns

## 📁 Project Structure

```
crimeshield/
├── app.py                          # Main Flask application entry point
├── config.py                       # Configuration settings
├── database.py                     # Database connection and schema
├── requirements.txt                # Python dependencies
├── README.md                       # Main documentation (this file)
├── ADVANCED_PYTHON_MAPPING.md      # Maps concepts to exact code locations
├── DEMO_GUIDE.md                   # Step-by-step demonstration guide
├── .gitignore                      # Git ignore rules
│
├── models/                         # Data models
│   ├── __init__.py
│   ├── case_model.py              # Case class with validation
│   ├── evidence_model.py          # Evidence class
│   └── connection_model.py        # Connection class
│
├── services/                       # Business logic layer
│   ├── __init__.py
│   ├── case_service.py            # Case CRUD operations
│   ├── evidence_service.py        # Evidence CRUD operations
│   ├── connection_service.py      # Connection management with review
│   ├── analysis_service.py        # Batch connection analysis
│   ├── audit_service.py           # Audit logging service
│   └── report_service.py          # Report generation (CSV/TXT)
│
├── routes/                         # API endpoints
│   ├── __init__.py
│   ├── case_routes.py             # Case endpoints
│   ├── evidence_routes.py         # Evidence endpoints
│   ├── connection_routes.py       # Connection endpoints
│   ├── analysis_routes.py         # Analysis endpoints
│   └── report_routes.py           # Report download endpoints
│
├── utils/                          # Utility modules
│   ├── __init__.py
│   ├── validators.py              # Input validation
│   ├── logger.py                  # Logging utilities
│   ├── connection_rules.py        # Strategy pattern for matching
│   └── connection_graph.py        # Graph traversal algorithms
│
├── tests/                          # Test suite (62 tests)
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_cases.py              # Case tests
│   ├── test_evidence.py           # Evidence tests
│   └── test_connections.py        # Connection analysis tests
│
└── reports/                        # Generated reports directory
    └── .gitkeep
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)

### Step 1: Navigate to the Project Directory
```powershell
cd crimeshield
```

### Step 2: Create a Virtual Environment (Recommended)
```powershell
python -m venv venv
```

### Step 3: Activate the Virtual Environment
```powershell
# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

## 🎮 Running the Application

### Start the Server
```powershell
python app.py
```

The server will start at `http://127.0.0.1:5000`

You should see output like:
```
============================================================
CRIMESHIELD - Criminal Network Analysis System
============================================================
Database: C:\path\to\crimeshield\crimeshield.db
Debug Mode: True
API Endpoints:
  - GET  /api/health
  - POST /api/cases
  - GET  /api/cases
  - GET  /api/cases/<id>
  - GET  /api/cases/code/<case_code>
  - PUT  /api/cases/<id>
  - DELETE /api/cases/<id>
  - GET  /api/cases/statistics
============================================================
Server starting on http://127.0.0.1:5000
Press CTRL+C to stop the server
============================================================
```

## 🧪 Running Tests

### Run All Tests
```powershell
pytest
```

### Run Tests with Verbose Output
```powershell
pytest -v
```

### Run Tests with Coverage Report
```powershell
pytest --cov=crimeshield --cov-report=html
```

### Run Specific Test Class
```powershell
pytest tests/test_cases.py::TestCreateCase -v
```

## 📡 API Endpoints

### Health Check
```http
GET /api/health
```
Returns system health status.

---

### Case Management

#### Create a Case
```http
POST /api/cases
Content-Type: application/json

{
  "case_code": "CASE-2024-001",
  "title": "Fictional Investigation",
  "description": "Sample case description",
  "location": "Sample City",
  "status": "open"
}
```

#### Get All Cases
```http
GET /api/cases
GET /api/cases?status=open
GET /api/cases?location=Sample%20City
GET /api/cases?title=Investigation
```

#### Get Case by ID
```http
GET /api/cases/1
```

#### Get Case by Code
```http
GET /api/cases/code/CASE-2024-001
```

#### Update a Case
```http
PUT /api/cases/1
Content-Type: application/json

{
  "status": "under_review",
  "title": "Updated Title"
}
```

#### Delete a Case
```http
DELETE /api/cases/1
```

#### Get Case Statistics
```http
GET /api/cases/statistics
```

---

### Evidence Management

#### Create Evidence
```http
POST /api/evidence
Content-Type: application/json

{
  "case_id": 1,
  "evidence_type": "physical",
  "description": "Sample evidence",
  "location_found": "Crime scene",
  "collected_by": "Officer Smith"
}
```

#### Get All Evidence
```http
GET /api/evidence
GET /api/evidence?case_id=1
GET /api/evidence?evidence_type=digital
```

#### Get Evidence by ID
```http
GET /api/evidence/1
```

#### Update Evidence
```http
PUT /api/evidence/1
Content-Type: application/json

{
  "description": "Updated description",
  "status": "analyzed"
}
```

#### Delete Evidence
```http
DELETE /api/evidence/1
```

#### Get Evidence Statistics
```http
GET /api/evidence/statistics
```

---

### Connection Analysis

#### Run Connection Analysis
```http
POST /api/analysis/run
```
Analyzes all cases and detects connections based on:
- Location proximity (within 50km)
- Person name matches
- Phone number matches

#### Get All Connections
```http
GET /api/connections
GET /api/connections?status=pending
GET /api/connections?connection_type=location
```

#### Get Connection by ID
```http
GET /api/connections/1
```

#### Get Connections for a Case
```http
GET /api/connections/case/1
```

#### Get Connection Network
```http
GET /api/connections/network/1
```
Returns all cases connected to case 1 (recursive graph traversal).

#### Review Connection
```http
PATCH /api/connections/1/review
Content-Type: application/json

{
  "status": "approved",
  "reviewer": "Detective Johnson",
  "review_notes": "Verified connection"
}
```

---

### Report Generation

#### Export Case Report (CSV)
```http
GET /api/reports/cases/1/export?format=csv
```
Downloads CSV file with case, evidence, and connection data.

#### Export Case Report (TXT)
```http
GET /api/reports/cases/1/export?format=txt
```
Downloads plain text formatted report.

---

### Audit Logs

#### Get Audit Logs
```http
GET /api/audit-logs
GET /api/audit-logs?action=CREATE_CASE
GET /api/audit-logs?user_id=admin
```

## 🧪 Testing with curl (Windows PowerShell)

### Health Check
```powershell
curl http://127.0.0.1:5000/api/health
```

### Create a Case
```powershell
curl -X POST http://127.0.0.1:5000/api/cases -H "Content-Type: application/json" -d '{\"case_code\":\"CASE-2024-001\",\"title\":\"Downtown Incident\",\"description\":\"Fictional case\",\"location\":\"Main Street, Downtown\",\"status\":\"open\"}'
```

### Create Evidence
```powershell
curl -X POST http://127.0.0.1:5000/api/evidence -H "Content-Type: application/json" -d '{\"case_id\":1,\"evidence_type\":\"physical\",\"description\":\"Sample evidence\",\"location_found\":\"Crime scene\",\"collected_by\":\"Officer Smith\"}'
```

### Run Connection Analysis
```powershell
curl -X POST http://127.0.0.1:5000/api/analysis/run
```

### Get All Connections
```powershell
curl http://127.0.0.1:5000/api/connections
```

### Get Connection Network for Case
```powershell
curl http://127.0.0.1:5000/api/connections/network/1
```

### Review a Connection
```powershell
curl -X PATCH http://127.0.0.1:5000/api/connections/1/review -H "Content-Type: application/json" -d '{\"status\":\"approved\",\"reviewer\":\"Detective Johnson\"}'
```

### Export Case Report (CSV)
```powershell
curl -o report.csv http://127.0.0.1:5000/api/reports/cases/1/export?format=csv
```

### Export Case Report (TXT)
```powershell
curl -o report.txt http://127.0.0.1:5000/api/reports/cases/1/export?format=txt
```

## 📋 Quick Demo Workflow

For a complete step-by-step demonstration with test data, see [DEMO_GUIDE.md](DEMO_GUIDE.md).

### Quick Start
1. Start the server: `python app.py`
2. Create 2-3 cases with overlapping locations or person names
3. Run analysis: `curl -X POST http://127.0.0.1:5000/api/analysis/run`
4. View connections: `curl http://127.0.0.1:5000/api/connections`
5. Export report: `curl -o report.csv "http://127.0.0.1:5000/api/reports/cases/1/export?format=csv"`

## 📊 Database Schema

### Cases Table
| Column      | Type      | Constraints                           |
|-------------|-----------|---------------------------------------|
| id          | INTEGER   | PRIMARY KEY AUTOINCREMENT             |
| case_code   | TEXT      | NOT NULL, UNIQUE                      |
| title       | TEXT      | NOT NULL                              |
| description | TEXT      |                                       |
| location    | TEXT      |                                       |
| status      | TEXT      | NOT NULL, CHECK (open/under_review/closed) |
| created_at  | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP             |
| updated_at  | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP             |

**Indexes**: `idx_cases_status`, `idx_cases_location`, `idx_cases_code`

---

### Evidence Table
| Column         | Type      | Constraints                           |
|----------------|-----------|---------------------------------------|
| id             | INTEGER   | PRIMARY KEY AUTOINCREMENT             |
| case_id        | INTEGER   | NOT NULL, FOREIGN KEY → cases(id)     |
| evidence_type  | TEXT      | NOT NULL, CHECK (physical/digital/document/testimonial) |
| description    | TEXT      | NOT NULL                              |
| location_found | TEXT      |                                       |
| collected_by   | TEXT      |                                       |
| collected_at   | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP             |
| status         | TEXT      | NOT NULL, CHECK (collected/analyzed/stored) |
| chain_of_custody | TEXT    |                                       |
| created_at     | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP             |
| updated_at     | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP             |

**Indexes**: `idx_evidence_case_id`, `idx_evidence_type`, `idx_evidence_status`

---

### Connections Table
| Column           | Type      | Constraints                           |
|------------------|-----------|---------------------------------------|
| id               | INTEGER   | PRIMARY KEY AUTOINCREMENT             |
| case_id_1        | INTEGER   | NOT NULL, FOREIGN KEY → cases(id)     |
| case_id_2        | INTEGER   | NOT NULL, FOREIGN KEY → cases(id)     |
| connection_type  | TEXT      | NOT NULL (location/person/phone/other) |
| connection_value | TEXT      | NOT NULL                              |
| confidence_score | REAL      | CHECK (0.0 to 1.0)                    |
| status           | TEXT      | NOT NULL, CHECK (pending/approved/rejected) |
| reviewer         | TEXT      |                                       |
| review_notes     | TEXT      |                                       |
| reviewed_at      | TIMESTAMP |                                       |
| created_at       | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP             |

**Constraints**: 
- `CHECK (case_id_1 < case_id_2)` - Normalized pairs
- `UNIQUE (case_id_1, case_id_2, connection_type, connection_value)` - No duplicates

**Indexes**: `idx_connections_case1`, `idx_connections_case2`, `idx_connections_type`, `idx_connections_status`

---

### Audit Logs Table
| Column     | Type      | Constraints                           |
|------------|-----------|---------------------------------------|
| id         | INTEGER   | PRIMARY KEY AUTOINCREMENT             |
| action     | TEXT      | NOT NULL                              |
| entity_type| TEXT      | NOT NULL                              |
| entity_id  | INTEGER   |                                       |
| user_id    | TEXT      |                                       |
| details    | TEXT      |                                       |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP             |

**Indexes**: `idx_audit_action`, `idx_audit_entity`, `idx_audit_user`

## 🔒 Security Features

- **SQL Injection Prevention**: All queries use parameterization
- **Path Traversal Prevention**: Report filenames sanitized and validated
- **Input Validation**: All inputs validated before processing
- **Error Handling**: Errors logged without exposing sensitive information
- **No eval/exec**: No use of dangerous functions on user input
- **Foreign Key Constraints**: Database integrity enforced with `PRAGMA foreign_keys = ON`
- **Audit Trail**: All operations logged with timestamps and user IDs

## 🎓 Learning Objectives

This project demonstrates:
1. **REST API Development** - Full CRUD operations with Flask
2. **Database Design** - Normalized schema with foreign keys and indexes
3. **Advanced Python Concepts** - 25+ concepts including decorators, context managers, type hints, recursion
4. **Design Patterns** - Strategy pattern for connection rules, Repository pattern for data access
5. **Test-Driven Development** - 62 comprehensive tests with pytest
6. **Graph Algorithms** - Recursive network traversal with cycle detection
7. **Business Logic** - Connection analysis with confidence scoring and review workflow
8. **Report Generation** - CSV and TXT exports with path security
9. **Audit Logging** - Complete system operation tracking
10. **Project Organization** - Clean architecture with separation of concerns
11. **Error Handling** - Comprehensive validation and exception handling
12. **Documentation** - Professional README, concept mapping, demo guide

## 📚 Documentation

- **README.md** (this file) - Complete project documentation
- **[ADVANCED_PYTHON_MAPPING.md](ADVANCED_PYTHON_MAPPING.md)** - Maps 25 concepts to exact code locations
- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Step-by-step demonstration with viva questions

## 🤝 Contributing

This is an educational project demonstrating Advanced Python concepts. Potential enhancements:
- Web UI with HTML/CSS/JavaScript
- User authentication and authorization
- Real-time notifications for new connections
- Advanced graph visualization
- Machine learning for connection confidence scoring
- Export to additional formats (PDF, Excel)
- RESTful pagination for large datasets

## ⚠️ Disclaimer

This system is designed for **educational purposes using fictional data only**. 

**Important Notes:**
- All data must be fictional/simulated
- A detected connection is only a lead for human review, not proof of criminal activity
- Real-world deployment would require:
  - User authentication and role-based access control
  - Encryption for sensitive data (at rest and in transit)
  - Compliance with data protection regulations (GDPR, etc.)
  - Professional security audit
  - Legal authorization for criminal investigation data

## 📝 License

This is an educational project for college-level Advanced Python coursework.

## 👨‍💻 Author

Created as a college-level Advanced Python mini-project demonstrating professional software development practices.

---

**Project Name**: CRIMESHIELD - Criminal Network Analysis System  
**Version**: 1.0.0  
**Python Version**: 3.12+  
**Framework**: Flask 3.0.0  
**Database**: SQLite3  
**Tests**: 62 passing (pytest)  
**Lines of Code**: ~2000+  
**Advanced Python Concepts**: 25+

---

## 🚀 Quick Start Summary

```powershell
# 1. Navigate to project
cd crimeshield

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run tests
pytest

# 6. Start server
python app.py

# 7. Test API
curl http://127.0.0.1:5000/api/health
```

Server will run at **http://127.0.0.1:5000**

For detailed demonstration, see **[DEMO_GUIDE.md](DEMO_GUIDE.md)**
