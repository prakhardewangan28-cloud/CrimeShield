# 📝 CRIMESHIELD Demo Cheat Sheet

**Quick reference for live demonstration**

---

## 🚀 START COMMANDS

```powershell
# Terminal 1 - Backend
python -m crimeshield.app

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

**URLs**:
- Frontend: `http://127.0.0.1:5173/`
- Backend: `http://127.0.0.1:5000/api/health`

---

## 📊 TEST DATA TO CREATE

### Case 1:
```
Case Code:        DEMO-2024-001
Title:            Downtown Bank Incident
Description:      Suspicious activity near bank
Location:         40.7128,-74.0060
Status:           Open
```

### Case 2:
```
Case Code:        DEMO-2024-002
Title:            Warehouse Investigation
Description:      Related suspicious activity
Location:         40.7589,-73.9851
Status:           Open
```

### Evidence 1 (for Case 1):
```
Evidence Code:       EVD-DEMO-001
Evidence Type:       Physical
Description:         Security camera footage
Location:            40.7128,-74.0060
Person:              John Smith
Phone:               +1-555-0123
Status:              Pending
```

### Evidence 2 (for Case 2):
```
Evidence Code:       EVD-DEMO-002
Evidence Type:       Testimonial
Description:         Witness statement
Location:            40.7589,-73.9851
Person:              John Smith
Phone:               +1-555-9999
Status:              Pending
```

**Expected Result**: 2 connections (location + person match)

---

## 🎯 DEMO FLOW

1. **Intro** (2 min) → What is CRIMESHIELD?
2. **Architecture** (2 min) → Show folder structure
3. **Create Data** (3 min) → Create 2 cases + 2 evidence
4. **Run Analysis** (4 min) → Click "Run Network Analysis"
5. **Show Concepts** (2 min) → Open VS Code, show code
6. **Testing** (1 min) → Run `pytest -v`
7. **Conclusion** (1 min) → Summarize achievements

---

## 💬 KEY POINTS TO MENTION

### What Makes This Project Special:
- ✅ **26+ Advanced Python concepts** demonstrated
- ✅ **101 tests** (62 unit + 39 live) - all passing
- ✅ **26 REST API endpoints** - all working
- ✅ **Real-world algorithms**: Graph traversal, pattern matching
- ✅ **Design patterns**: Strategy, Factory, Repository
- ✅ **Security**: No SQL injection, input validation, audit logging
- ✅ **Professional**: Full documentation, testing, error handling

### Advanced Python Concepts (mention 5-6):
1. **Decorators** (`@log_request`, `@contextmanager`)
2. **Context Managers** (database connections)
3. **Strategy Pattern** (matching rules)
4. **Recursion** (graph traversal with cycle detection)
5. **Type Hints** (throughout codebase)
6. **Abstract Base Classes** (MatchingRule)

### Architecture Highlights:
- **Backend**: Flask REST API + SQLite
- **Frontend**: React + TypeScript
- **Testing**: pytest with fixtures
- **4 Tables**: cases, evidence, connections, audit_logs

---

## 🎤 COMMON QUESTIONS & ANSWERS

### "Why this project?"
> "To solve a real problem while demonstrating advanced Python concepts in a professional full-stack application."

### "What's the Strategy Pattern?"
> "A design pattern that makes algorithms interchangeable. I have 3 matching strategies (location, person, phone) that all inherit from a base class."

### "How do you prevent SQL injection?"
> "All queries use parameterized statements with `?` placeholders. Example: `cursor.execute('SELECT * FROM cases WHERE id = ?', (case_id,))`"

### "Why SQLite?"
> "Perfect for development and demos. Zero config, single file. For production, I'd use PostgreSQL for concurrency and performance."

### "What would you add?"
> "Authentication, machine learning for confidence scoring, real-time collaboration, and deployment to cloud."

---

## 🔍 FILES TO SHOW IN VS CODE

### Context Manager:
**File**: `crimeshield/database.py` (line ~70)
```python
@contextmanager
def get_db_connection(db_path: Path):
    # Shows: decorator, context manager, error handling
```

### Strategy Pattern:
**File**: `crimeshield/utils/connection_rules.py` (line ~8)
```python
class MatchingRule(ABC):
    @abstractmethod
    def normalize_value(self, value: str) -> str:
        # Shows: ABC, abstract methods, inheritance
```

### Recursion:
**File**: `crimeshield/utils/connection_graph.py`
```python
def _dfs_traverse(self, case_id: int, visited: Set[int], ...):
    # Shows: recursion, cycle detection
```

---

## 📈 PROJECT STATISTICS

**To Impress**:
- 30+ Python files
- 2000+ lines of code
- 62 pytest tests (100% passing)
- 39 live API tests (100% passing)
- 26 REST API endpoints
- 4 database tables with foreign keys
- 13 database indexes
- 26+ Advanced Python concepts
- 0 bugs found in audit
- 0 security vulnerabilities

---

## ⏱️ TIMING

| Section | Time | What to Do |
|---------|------|------------|
| Intro | 2 min | Explain problem & solution |
| Architecture | 2 min | Show folder structure |
| Create Data | 3 min | Create 2 cases + evidence |
| Analysis | 4 min | Run analysis, explore graph |
| Code Review | 2 min | Show 3 code examples |
| Testing | 1 min | Run pytest |
| Conclusion | 1 min | Summarize achievements |
| **Total** | **15 min** | |

---

## 🎯 IF RUNNING SHORT ON TIME

**Skip**:
- Detailed code walkthrough (just mention concepts)
- Report generation demo
- Frontend code (focus on backend Python)

**Must Show**:
- Create cases and evidence
- Run network analysis
- Show connections in graph
- Mention testing (don't need to run)

---

## 🆘 EMERGENCY FIXES

### Backend won't start:
```powershell
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process if needed
taskkill /PID <process_id> /F
```

### Frontend won't start:
```powershell
# Clear cache and reinstall
cd frontend
rm -r node_modules
npm install
npm run dev
```

### No connections found after analysis:
- Make sure evidence has SAME person name in both cases
- Check locations are within 50km
- Verify evidence was created for both cases

---

## ✅ FINAL CHECKLIST

**Before Demo Starts**:
- [ ] Backend running (green terminal output)
- [ ] Frontend running (browser auto-opens)
- [ ] Browser has frontend open
- [ ] VS Code open in background
- [ ] This cheat sheet open
- [ ] Close all unnecessary apps
- [ ] Turn off notifications
- [ ] Phone on silent

**You're Ready!** 🚀

---

## 💪 CONFIDENCE BOOSTERS

1. You have **101 passing tests** - that's exceptional
2. You built **26 working API endpoints** - that's professional
3. You implemented **real algorithms** - graph traversal, pattern matching
4. Your code is **well-documented** - 4 complete guides
5. Your project **solves a real problem** - connection analysis

**You've got this!** 🌟
