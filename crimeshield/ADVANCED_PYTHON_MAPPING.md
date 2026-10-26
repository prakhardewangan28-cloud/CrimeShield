# Advanced Python Concepts Mapping

This document maps each Advanced Python concept demonstrated in CRIMESHIELD to the exact file and function where it appears.

## 1. *args and **kwargs (Variable Arguments)

**Location:** `utils/advanced_python.py`
- **Function:** `format_entity_info(*args, **kwargs)` - Lines 20-45
- **Function:** `create_audit_entry(entity_type, entity_id, *actions, **metadata)` - Lines 48-68
- **Usage:** Flexible function arguments for audit logging and entity formatting

**Location:** `models/evidence_model.py`
- **Class:** `DigitalEvidence.__init__(*args, file_hash, file_size, **kwargs)` - Lines 335-345
- **Usage:** Extending parent class initialization with additional parameters

## 2. Higher-Order Functions

**Location:** `utils/advanced_python.py`
- **Function:** `apply_transformation(data, transformer)` - Lines 73-89
- **Function:** `create_validator(field_name, max_length)` - Lines 92-112
- **Usage:** Functions that take or return other functions

**Location:** `services/analysis_service.py`
- **Method:** `MatchingRule.find_matches()` - Lines 56-93
- **Usage:** Using strategy pattern with interchangeable algorithms

## 3. Closures

**Location:** `utils/advanced_python.py`
- **Function:** `create_evidence_filter(evidence_type, status)` - Lines 117-136
- **Function:** `counter(start)` - Lines 139-155
- **Usage:** Inner functions capturing outer function variables

**Location:** `utils/logger.py`
- **Decorator:** `log_request(func)` - Lines 31-72
- **Usage:** Decorator closure accessing outer function parameters

## 4. map() Function

**Location:** `utils/advanced_python.py`
- **Function:** `extract_field_values(items, field)` - Lines 160-175
- **Function:** `normalize_evidence_codes(codes)` - Lines 178-191
- **Usage:** Applying functions to iterables

## 5. filter() Function

**Location:** `utils/advanced_python.py`
- **Function:** `filter_by_status(items, status)` - Lines 196-213
- **Function:** `filter_active_items(items)` - Lines 216-234
- **Usage:** Filtering collections based on conditions

## 6. functools.reduce()

**Location:** `utils/advanced_python.py`
- **Function:** `count_by_type(items, type_field)` - Lines 239-263
- **Function:** `calculate_total_count(items)` - Lines 266-277
- **Usage:** Reducing collections to single values

## 7. Iterators

**Location:** `utils/advanced_python.py`
- **Class:** `EvidenceIterator` - Lines 282-314
- **Methods:** `__iter__()`, `__next__()`
- **Usage:** Custom iteration protocol implementation

## 8. Generators (yield)

**Location:** `utils/advanced_python.py`
- **Function:** `batch_processor(items, batch_size)` - Lines 319-335
- **Function:** `evidence_code_generator(prefix, start)` - Lines 338-354
- **Function:** `filtered_items_generator(items, condition)` - Lines 357-373
- **Usage:** Lazy evaluation and memory-efficient processing

## 9. Decorators

**Location:** `utils/logger.py`
- **Function:** `log_request(func)` - Lines 31-72
- **Function:** `log_execution_time(func)` - Lines 75-94
- **Usage:** Function wrapping with @functools.wraps

**Location:** `services/audit_service.py`
- **Function:** `audit_operation(action, entity_type)` - Lines 112-160
- **Usage:** Decorator for automatic audit logging

## 10. Inheritance and Method Overriding

**Location:** `models/evidence_model.py`
- **Class:** `BaseEntity(ABC)` - Lines 17-58
- **Class:** `Evidence(BaseEntity)` - Lines 65-310
- **Class:** `DigitalEvidence(Evidence)` - Lines 317-360
- **Usage:** Three-level inheritance hierarchy with abstract base class

**Methods Overridden:**
- `to_dict()` - Evidence overrides BaseEntity abstract method
- `validate()` - Evidence implements abstract method
- `__str__()` - Evidence overrides base representation
- `__repr__()` - Evidence overrides base representation

## 11. super()

**Location:** `models/evidence_model.py`
- **Method:** `Evidence.__init__()` - Line 85
- **Method:** `DigitalEvidence.__init__()` - Line 343
- **Method:** `DigitalEvidence.to_dict()` - Line 351
- **Usage:** Calling parent class methods

## 12. List Comprehensions

**Location:** `services/case_service.py`
- **Method:** `get_all_cases()` - Line 102
- **Usage:** `[self._row_to_case(row) for row in rows]`

**Location:** `services/evidence_service.py`
- **Method:** `get_all_evidence()` - Line 127
- **Usage:** Converting database rows to objects

**Location:** `routes/case_routes.py`
- **Method:** `get_cases()` - Line 145
- **Usage:** `[case.to_dict() for case in cases]`

## 13. Dictionary Comprehensions

**Location:** `models/case_model.py`
- **Method:** `to_dict()` - Lines 50-59
- **Usage:** Creating dictionaries with conditional expressions

**Location:** `services/case_service.py`
- **Method:** `update_case()` - Line 133
- **Usage:** `{k: v for k, v in updates.items() if v is not None}`

## 14. Context Managers

**Location:** `database.py`
- **Class:** `DatabaseConnection` - Lines 15-66
- **Methods:** `__enter__()`, `__exit__()`
- **Usage:** Class-based context manager

**Location:** `database.py`
- **Function:** `get_db_connection(db_path)` - Lines 69-92
- **Decorator:** `@contextmanager`
- **Usage:** Generator-based context manager

## 15. Custom Exceptions

**Location:** `utils/advanced_python.py`
- **Class:** `CrimeshieldException(Exception)` - Lines 381-385
- **Class:** `ValidationError(CrimeshieldException)` - Lines 388-392
- **Class:** `NotFoundError(CrimeshieldException)` - Lines 395-402
- **Class:** `DuplicateError(CrimeshieldException)` - Lines 405-412
- **Class:** `InvalidReferenceError(CrimeshieldException)` - Lines 415-422
- **Usage:** Custom exception hierarchy

**Location:** `services/analysis_service.py`
- **Class:** `AnalysisException(CrimeshieldException)` - Lines 24-26
- **Usage:** Analysis-specific exception

## 16. Type Hints

**Used Throughout:** All files consistently use type hints
- Function parameters: `def function(param: str) -> int:`
- Class attributes: `self.id: Optional[int] = None`
- Complex types: `List[Dict[str, Any]]`, `Optional[str]`

**Examples:**
- `models/case_model.py` - Lines 25-40
- `services/case_service.py` - Lines 28-65
- `utils/advanced_python.py` - Throughout

## 17. Lambda Functions

**Location:** `services/case_service.py`
- **Method:** `get_cases_by_status()` - Lines 307-313
- **Usage:** `sorted(cases, key=lambda case: case.created_at, reverse=True)`

**Location:** `utils/advanced_python.py`
- **Function:** `extract_field_values()` - Line 174
- **Usage:** `map(lambda item: item.get(field), items)`

## 18. Abstract Base Classes (ABC)

**Location:** `models/evidence_model.py`
- **Class:** `BaseEntity(ABC)` - Lines 17-58
- **Decorator:** `@abstractmethod`
- **Methods:** `to_dict()`, `validate()`
- **Usage:** Enforcing interface contracts

**Location:** `services/analysis_service.py`
- **Class:** `MatchingRule(ABC)` - Lines 35-95
- **Methods:** Abstract methods for strategy pattern
- **Usage:** Defining matching rule interface

## 19. Static Methods

**Location:** `models/case_model.py`
- **Method:** `_parse_datetime()` - Lines 97-111
- **Decorator:** `@staticmethod`
- **Usage:** Utility method not requiring instance

**Location:** `services/case_service.py`
- **Method:** `_row_to_case()` - Lines 326-342
- **Usage:** Database row conversion

## 20. Class Methods

**Location:** `models/case_model.py`
- **Method:** `from_dict()` - Lines 76-94
- **Decorator:** `@classmethod`
- **Usage:** Alternative constructor

**Location:** `models/evidence_model.py`
- **Method:** `from_dict()` - Lines 145-162
- **Usage:** Creating instances from dictionaries

## 21. Magic Methods

**Location:** `models/case_model.py`
- **Methods:** `__repr__()`, `__str__()`, `__eq__()`, `__hash__()`
- **Lines:** 113-138
- **Usage:** Custom object behavior

**Location:** `models/evidence_model.py`
- **Methods:** `__enter__()`, `__exit__()` in BaseEntity
- **Usage:** Context manager protocol

## 22. Strategy Pattern

**Location:** `services/analysis_service.py`
- **Classes:** `LocationMatchingRule`, `PersonMatchingRule`, `PhoneMatchingRule`
- **Lines:** 98-180
- **Usage:** Interchangeable matching algorithms

## 23. Recursion

**Location:** `utils/connection_graph.py`
- **Method:** `find_path()` with `_dfs_recursive()` - Lines 66-115
- **Method:** `get_connected_cases()` with `_traverse_recursive()` - Lines 118-153
- **Method:** `detect_cycle()` with `_detect_cycle_recursive()` - Lines 175-214
- **Usage:** Graph traversal with cycle detection and depth limits

## 24. File I/O

**Location:** `services/report_service.py`
- **Method:** `generate_case_report_csv()` - Lines 96-157
- **Method:** `generate_case_report_txt()` - Lines 160-245
- **Usage:** CSV and text file generation with safe path handling

## 25. Regular Expressions

**Location:** `services/analysis_service.py`
- **Method:** `PhoneMatchingRule.normalize_value()` - Lines 172-177
- **Usage:** `re.sub(r'\\D', '', value)` for phone number normalization

## Summary

This project demonstrates **25+ Advanced Python concepts** integrated into a real-world application:

1. Variable arguments (*args, **kwargs)
2. Higher-order functions
3. Closures
4. map(), filter(), reduce()
5. Iterators and generators
6. Decorators with functools.wraps
7. Inheritance and polymorphism
8. super() for parent class calls
9. List and dictionary comprehensions
10. Context managers (both types)
11. Custom exception hierarchy
12. Type hints throughout
13. Lambda functions
14. Abstract base classes
15. Static and class methods
16. Magic methods
17. Strategy design pattern
18. Recursion with safeguards
19. File I/O operations
20. Regular expressions
21. Database operations with parameterized queries
22. RESTful API design
23. Service layer architecture
24. Modular package structure
25. Comprehensive testing with pytest
