# 🛡️ CRIMESHIELD - Criminal Network Analysis System

<div align="center">

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![Tests](https://img.shields.io/badge/tests-101%20passing-brightgreen.svg)
![License](https://img.shields.io/badge/license-Educational-orange.svg)

**An Advanced Python Mini-Project for Criminal Investigation Case Management**

[Features](#-features) • [Demo](#-live-demonstration) • [Installation](#-installation) • [Documentation](#-documentation) • [Technologies](#-technologies)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Technologies](#-technologies)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [Advanced Python Concepts](#-advanced-python-concepts)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Screenshots](#-screenshots)
- [Project Statistics](#-project-statistics)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**CRIMESHIELD** is a sophisticated criminal investigation case management system that demonstrates professional software engineering practices using Advanced Python concepts. The system helps investigators organize cases, manage evidence, and **automatically detect connections between cases** using intelligent pattern-matching algorithms.

### The Problem

Criminal investigators often deal with fragmented evidence across multiple cases. Manually identifying connections between cases (shared locations, persons, or phone numbers) is time-consuming and error-prone.

### The Solution

CRIMESHIELD uses automated analysis algorithms to detect potential connections between cases by analyzing:
- 📍 **Geographic proximity** (coordinate-based distance calculation)
- 👤 **Person name matches** (normalized comparison)
- 📱 **Phone number matches** (normalized with country codes)

### Key Highlight

**This is not just a CRUD application** - it includes intelligent features like automated connection detection, graph-based network visualization, and recursive case traversal algorithms.

---

## ✨ Features

### Core Features

- ✅ **Case Management**: Complete CRUD operations for criminal investigation cases
- ✅ **Evidence Management**: Track evidence items with metadata and chain of custody
- ✅ **Automated Connection Analysis**: AI-powered detection of case relationships
- ✅ **Network Visualization**: Interactive graph showing case connections
- ✅ **Review Workflow**: Investigators can confirm or dismiss detected connections
- ✅ **Report Generation**: Export case data in CSV and TXT formats
- ✅ **Audit Logging**: Complete trail of all system operations
- ✅ **Search & Filtering**: Advanced search across cases and evidence

### Technical Features

- 🔒 **Security**: SQL injection prevention, input validation, path sanitization
- 🧪 **Testing**: 101 comprehensive tests (62 unit + 39 integration)
- 📊 **Statistics**: Real-time metrics and dashboards
- 🔄 **RESTful API**: 26 well-documented endpoints
- 📝 **Type Safety**: Full type hints throughout codebase
- 🎨 **Clean Architecture**: Separation of concerns (models, services, routes)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Frontend (React)                    │
│            TypeScript + Vite + TailwindCSS          │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────┴────────────────────────────────┐
│              Backend (Python/Flask)                  │
│  ┌─────────────────────────────────────────────┐   │
│  │  Routes Layer (26 API Endpoints)            │   │
│  └──────────────────┬──────────────────────────┘   │
│  ┌──────────────────┴──────────────────────────┐   │
│  │  Services Layer (Business Logic)            │   │
│  │  • CaseService    • EvidenceService         │   │
│  │  • AnalysisService • ConnectionService      │   │
│  │  • ReportService   • AuditService           │   │
│  └──────────────────┬──────────────────────────┘   │
│  ┌──────────────────┴──────────────────────────┐   │
│  │  Models Layer (Data Entities)               │   │
│  │  • Case  • Evidence  • Connection           │   │
│  └──────────────────┬──────────────────────────┘   │
│  ┌──────────────────┴──────────────────────────┐   │
│  │  Utils Layer (Algorithms)                   │   │
│  │  • Connection Rules (Strategy Pattern)      │   │
│  │  • Graph Traversal (DFS with Recursion)    │   │
│  │  • Validators • Loggers                     │   │
│  └──────────────────┬──────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────┐
│           SQLite Database (4 Tables)                 │
│  • cases  • evidence  • connections  • audit_logs   │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ Technologies

### Backend

- **Python 3.12+** - Core programming language
- **Flask 3.0.0** - Web framework for REST API
- **SQLite3** - Database (with foreign key enforcement)
- **pytest 7.4.3** - Testing framework
- **Type Hints** - Full static typing throughout

### Frontend

- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Cytoscape.js** - Network graph visualization

### Tools & Practices

- **Git** - Version control
- **Virtual Environment** - Dependency isolation
- **REST API** - Standard communication protocol
- **Context Managers** - Resource management
- **Design Patterns** - Strategy, Factory, Repository

---

## 📥 Installation

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Git
- Node.js 18+ (for frontend, optional)

### Step 1: Clone the Repository

```powershell
git clone https://github.com/prakhardewangan28-cloud/CrimeShield.git
cd CrimeShield
```

### Step 2: Set Up Backend

```powershell
# Navigate to backend directory
cd crimeshield

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Set Up Frontend (Optional)

```powershell
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install
```

---

## 🚀 Quick Start

### Start Backend Server

```powershell
# From project root
python -m crimeshield.app
```

Server will start at: **http://127.0.0.1:5000**

### Start Frontend (Optional)

```powershell
# In a separate terminal
cd frontend
npm run dev
```

Frontend will start at: **http://127.0.0.1:5173**

### Verify Backend is Running

```powershell
curl http://127.0.0.1:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "CRIMESHIELD API",
  "version": "1.0.0"
}
```

---

## 📡 API Endpoints

### Case Management (8 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/cases` | Create new case |
| GET | `/api/cases` | List all cases (with filters) |
| GET | `/api/cases/<id>` | Get case by ID |
| GET | `/api/cases/code/<code>` | Get case by code |
| PUT | `/api/cases/<id>` | Update case |
| DELETE | `/api/cases/<id>` | Delete case |
| GET | `/api/cases/statistics` | Get case statistics |

### Evidence Management (7 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/evidence` | Create evidence |
| GET | `/api/evidence` | List all evidence |
| GET | `/api/evidence/<id>` | Get evidence by ID |
| PUT | `/api/evidence/<id>` | Update evidence |
| DELETE | `/api/evidence/<id>` | Delete evidence |
| GET | `/api/cases/<id>/evidence` | Get case evidence |
| GET | `/api/evidence/statistics` | Get statistics |

### Connection Analysis (7 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analysis/run` | Run connection analysis |
| GET | `/api/connections` | List connections |
| GET | `/api/connections/<id>` | Get connection by ID |
| GET | `/api/cases/<id>/connections` | Get case connections |
| PATCH | `/api/connections/<id>/review` | Review connection |
| GET | `/api/connections/statistics` | Get statistics |
| GET | `/api/connections/graph/<id>` | Get connection graph |

### Report Generation (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/summary` | System summary |
| GET | `/api/reports/cases/<id>` | Case report info |
| GET | `/api/reports/cases/<id>/export` | Export report (CSV/TXT) |

**Full API documentation**: See [crimeshield/README.md](crimeshield/README.md)

---

## 🐍 Advanced Python Concepts

This project demonstrates **26+ Advanced Python concepts**:

### Object-Oriented Programming
- ✅ Classes and Objects
- ✅ Inheritance and Polymorphism
- ✅ Abstract Base Classes (ABC)
- ✅ Magic Methods (`__init__`, `__repr__`, `__enter__`, `__exit__`)
- ✅ Properties (`@property` decorator)
- ✅ Static and Class Methods

### Functional Programming
- ✅ Decorators (`@log_request`, `@contextmanager`)
- ✅ Closures
- ✅ Lambda Functions
- ✅ Higher-Order Functions
- ✅ Generator Expressions

### Data Structures & Algorithms
- ✅ List Comprehensions
- ✅ Dictionary Comprehensions
- ✅ Sets and Set Operations
- ✅ Recursion (Graph Traversal with DFS)
- ✅ Graph Algorithms (Cycle Detection)

### Advanced Features
- ✅ Context Managers (Resource Management)
- ✅ Type Hints (Full Static Typing)
- ✅ Custom Exceptions
- ✅ Dataclasses
- ✅ Enums

### Design Patterns
- ✅ Strategy Pattern (Matching Rules)
- ✅ Factory Pattern (Rule Creation)
- ✅ Repository Pattern (Data Access)

### Software Engineering
- ✅ Modules and Packages
- ✅ Exception Handling
- ✅ Logging
- ✅ Testing with pytest

**Detailed mapping**: See [ADVANCED_PYTHON_MAPPING.md](crimeshield/ADVANCED_PYTHON_MAPPING.md)

---

## 🧪 Testing

### Test Coverage

```
Total Tests: 101
├── Unit Tests (pytest): 62
│   ├── Case Tests: 26
│   ├── Evidence Tests: 20
│   └── Connection Tests: 16
└── Live API Tests: 39
    ├── Integration tests
    └── End-to-end workflows
```

### Run Tests

```powershell
# Run all unit tests
cd crimeshield
pytest -v

# Run with coverage
pytest --cov=crimeshield --cov-report=html

# Run live API tests (server must be running)
python scripts/test_api.py
```

### Test Results

```
============================== 62 passed in 6.43s ==============================
```

All tests passing ✅

---

## 📚 Documentation

This project includes comprehensive documentation:

1. **[README.md](crimeshield/README.md)** - Complete project guide
2. **[ADVANCED_PYTHON_MAPPING.md](crimeshield/ADVANCED_PYTHON_MAPPING.md)** - Concept locations
3. **[DEMO_GUIDE.md](crimeshield/DEMO_GUIDE.md)** - Step-by-step demonstration
4. **[BACKEND_AUDIT_REPORT.md](crimeshield/BACKEND_AUDIT_REPORT.md)** - Complete audit results
5. **[LIVE_DEMONSTRATION_GUIDE.md](crimeshield/LIVE_DEMONSTRATION_GUIDE.md)** - Presentation guide
6. **[PROJECT_SUMMARY.md](crimeshield/PROJECT_SUMMARY.md)** - Project overview

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Python Files** | 30+ |
| **Lines of Code** | 2000+ |
| **API Endpoints** | 26 |
| **Database Tables** | 4 |
| **Database Indexes** | 13 |
| **Unit Tests** | 62 |
| **Integration Tests** | 39 |
| **Test Pass Rate** | 100% |
| **Advanced Concepts** | 26+ |
| **Dependencies** | 5 packages |
| **Documentation Files** | 6 |

---

## 🔒 Security

### Security Features Implemented

- ✅ **SQL Injection Prevention**: All queries use parameterized statements
- ✅ **Path Traversal Prevention**: Filename sanitization and validation
- ✅ **Input Validation**: Comprehensive validation on all inputs
- ✅ **Error Handling**: Secure error messages (no sensitive data leaked)
- ✅ **Audit Logging**: Complete operation trail
- ✅ **Foreign Key Constraints**: Database integrity enforced
- ✅ **No Dangerous Functions**: No use of `eval()` or `exec()`

### Security Audit Results

- ✅ 0 SQL injection vulnerabilities
- ✅ 0 path traversal vulnerabilities  
- ✅ 0 critical security issues

**Full audit**: See [BACKEND_AUDIT_REPORT.md](crimeshield/BACKEND_AUDIT_REPORT.md)

---

## 🎓 Educational Value

This project was created as an **Advanced Python college mini-project** to demonstrate:

### Skills Demonstrated

1. **Full-Stack Development** - Backend + Frontend integration
2. **API Design** - RESTful principles and best practices
3. **Database Design** - Normalization, constraints, indexes
4. **Algorithm Implementation** - Graph traversal, pattern matching
5. **Testing Methodology** - Unit tests, integration tests, fixtures
6. **Software Architecture** - Clean code, separation of concerns
7. **Security Awareness** - Defensive programming practices
8. **Documentation** - Professional-grade documentation

### Real-World Application

While this is an educational project using fictional data, the architecture and patterns used are suitable for real-world applications. For production deployment, additional features would be needed:

- User authentication and authorization
- Data encryption (at rest and in transit)
- Compliance with data protection regulations
- Horizontal scaling architecture
- Advanced caching strategies

---

## 🤝 Contributing

This is an educational project, but contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

See [Installation](#-installation) section for setup instructions.

---

## 📝 License

This project is created for educational purposes as part of college coursework. Feel free to use it for learning and reference.

**Important**: This system uses **fictional data only**. Do not use with real criminal investigation data without proper:
- Legal authorization
- Data protection compliance
- Security measures (authentication, encryption, etc.)
- Professional security audit

---

## 👨‍💻 Author

**Prakhar Dewangan**

- GitHub: [@prakhardewangan28-cloud](https://github.com/prakhardewangan28-cloud)
- Project: [CRIMESHIELD](https://github.com/prakhardewangan28-cloud/CrimeShield)

---

## 🌟 Acknowledgments

- Python Software Foundation
- Flask Framework
- SQLite Database
- React Community
- Open Source Community

---

## 📞 Support

For questions or issues:
1. Check the [documentation](crimeshield/)
2. Review [DEMO_GUIDE.md](crimeshield/DEMO_GUIDE.md)
3. Open an issue on GitHub

---

<div align="center">

**⭐ Star this repository if you found it helpful!**

Made with ❤️ and Python 🐍

</div>
