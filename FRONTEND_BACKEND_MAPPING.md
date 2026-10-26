# CRIMESHIELD — Frontend-to-Backend API Integration Mapping

**College Advanced Python Mini-Project**  
**Project Name**: CRIMESHIELD — Criminal Network Analysis System  
**Tagline**: *From Fragmented Evidence to Connected Intelligence*  
**Architecture**: React 19 + TypeScript + Vite + Tailwind CSS Frontend integrated with Flask 3.0 + SQLite3 Backend

---

## 1. Complete API Integration Matrix

| Frontend Page / Component | User Action / Trigger | Backend Endpoint | HTTP Method | Request Body / Query Params | Expected Backend Response | Integration Status | Notes / Missing Support |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: | :--- |
| **System Shell / TopBar** | Auto-polling health check | `/api/health` | `GET` | *None* | `{"service": "...", "status": "healthy", "version": "1.0.0"}` | **Integrated & Verified** | Probes server alive state and latency |
| **Dashboard** | Operational stats cards & charts | `/api/reports/summary` | `GET` | *None* | `{"summary": {"cases": {...}, "evidence": {...}, "connections": {...}}}` | **Integrated & Verified** | Unified aggregate metrics feed |
| **Dashboard** | Recent cases list | `/api/cases` | `GET` | *None* | `{"cases": [...], "count": N}` | **Integrated & Verified** | Live SQLite table extraction |
| **Dashboard** | Recent connections list | `/api/connections` | `GET` | *None* | `{"connections": [...], "count": N}` | **Integrated & Verified** | Live SQLite table extraction |
| **Case Management** | Search & filter case list | `/api/cases` | `GET` | `?title=...&location=...&status=...` | `{"cases": [...], "count": N}` | **Integrated & Verified** | Full search & status filtering |
| **Case Management** | Case Details Modal | `/api/cases/<id>` | `GET` | Path param: `case_id` | `{"case": {...}}` | **Integrated & Verified** | Specific case record retrieval |
| **Case Management** | Case Code Lookup | `/api/cases/code/<case_code>` | `GET` | Path param: `case_code` | `{"case": {...}}` | **Integrated & Verified** | Alternative case identifier search |
| **Case Management** | Case Statistics Card | `/api/cases/statistics` | `GET` | *None* | `{"statistics": {"total": N, "open": N, "under_review": N, "closed": N}}` | **Integrated & Verified** | Real-time counts from DB |
| **Case Management** | Create New Case | `/api/cases` | `POST` | `{"case_code": str, "title": str, "description": str, "location": str, "status": "open"}` | `{"case": {...}, "message": "Case created successfully"}` (201) | **Integrated & Verified** | Validated client-side & server-side |
| **Case Management** | Edit Existing Case | `/api/cases/<id>` | `PUT` | `{"case_code"?: str, "title"?: str, "description"?: str, "location"?: str, "status"?: str}` | `{"case": {...}, "message": "Case updated successfully"}` | **Integrated & Verified** | Partial update supported |
| **Case Management** | Expunge Case | `/api/cases/<id>` | `DELETE` | Path param: `case_id` | `{"message": "Case ... deleted successfully"}` | **Integrated & Verified** | Cascade-aware SQLite deletion |
| **Case Details Drawer** | Fetch Attached Evidence | `/api/cases/<case_id>/evidence` | `GET` | Path param: `case_id` | `{"case_id": N, "count": N, "evidence": [...]}` | **Integrated & Verified** | Nested relationship endpoint |
| **Case Details Drawer** | Fetch Correlated Links | `/api/cases/<case_id>/connections` | `GET` | Path param: `case_id` | `{"case_id": N, "count": N, "connections": [...]}` | **Integrated & Verified** | Filtered by normalized case ID pairs |
| **Evidence Vault** | Search & filter evidence | `/api/evidence` | `GET` | `?evidence_type=...&processing_status=...` | `{"count": N, "evidence": [...]}` | **Integrated & Verified** | Multi-type evidence store |
| **Evidence Vault** | Evidence Statistics | `/api/evidence/statistics` | `GET` | *None* | `{"statistics": {"total": N, "by_type": {...}, "by_status": {...}}}` | **Integrated & Verified** | Type and status breakdown |
| **Evidence Vault** | Inspect Evidence Record | `/api/evidence/<id>` | `GET` | Path param: `evidence_id` | `{"evidence": {...}}` | **Integrated & Verified** | Chain of custody metadata |
| **Evidence Vault** | Catalog New Evidence | `/api/evidence` | `POST` | `{"evidence_code": str, "case_id": int, "evidence_type": str, "description": str, "person_reference"?: str, "phone_reference"?: str, "location_reference"?: str, "processing_status"?: str}` | `{"evidence": {...}, "message": "Evidence created successfully"}` (201) | **Integrated & Verified** | Requires existing `case_id` FK |
| **Evidence Vault** | Edit Evidence Record | `/api/evidence/<id>` | `PUT` | `{"evidence_code"?: str, "evidence_type"?: str, ...}` | `{"evidence": {...}, "message": "Evidence updated successfully"}` | **Integrated & Verified** | Mutable chain-of-custody updates |
| **Evidence Vault** | Expunge Evidence Record | `/api/evidence/<id>` | `DELETE` | Path param: `evidence_id` | `{"message": "Evidence ... deleted successfully"}` | **Integrated & Verified** | Removes physical or digital item |
| **Network Analysis** | Run Analysis Button | `/api/analysis/run` | `POST` | `{"batch_size": 100}` (optional) | `{"message": "Analysis completed successfully", "results": {"analysis_time_seconds": float, "connections_created": int, "evidence_analyzed": int, "total_connections": int}}` | **Integrated & Verified** | Triggers backend correlation engine |
| **Network Analysis** | Render Network Graph | `/api/cases` + `/api/connections` | `GET` | *None* | All cases as nodes, connections as edges | **Integrated & Verified** | High-performance Cytoscape graph |
| **Network Analysis** | Deep Traversal Graph | `/api/connections/graph/<case_id>` | `GET` | `?max_depth=1..5` | `{"case_id": N, "connected_cases": [...], "connection_count": N, "max_depth": N}` | **Integrated & Verified** | Recursive BFS connection traversal |
| **Connections Review** | Search & review queue | `/api/connections` | `GET` | `?review_status=pending|confirmed_for_review|dismissed` | `{"connections": [...], "count": N}` | **Integrated & Verified** | Adjudication queue |
| **Connections Review** | Inspect Specific Link | `/api/connections/<id>` | `GET` | Path param: `connection_id` | `{"connection": {...}}` | **Integrated & Verified** | Both cases, value & explanation |
| **Connections Review** | Connection Statistics | `/api/connections/statistics` | `GET` | *None* | `{"statistics": {"total": N, "pending": N, "confirmed_for_review": N, "dismissed": N}}` | **Integrated & Verified** | Adjudication metrics |
| **Connections Review** | Adjudicate Lead | `/api/connections/<id>/review` | `PATCH` | `{"review_status": "confirmed_for_review"|"dismissed", "review_notes"?: str}` | `{"connection": {...}, "message": "Connection review status updated successfully"}` | **Integrated & Verified** | Sets formal analyst decision |
| **Intelligence Reports** | Aggregate System Report | `/api/reports/summary` | `GET` | *None* | `{"summary": {...}}` | **Integrated & Verified** | Overall intelligence briefing |
| **Intelligence Reports** | Inspect Case Report Metadata | `/api/reports/cases/<case_id>` | `GET` | Path param: `case_id` | `{"case_id": N, "case_code": str, "title": str, "evidence_count": N, "connection_count": N, "available_formats": ["csv", "txt"]}` | **Integrated & Verified** | Pre-export verification |
| **Intelligence Reports** | Export Case CSV Report | `/api/reports/cases/<case_id>/export?format=csv` | `GET` | `format=csv` | CSV text file download (`Content-Disposition: attachment; filename=case_X_report.csv`) | **Integrated & Verified** | Blob download with authentic file name |
| **Intelligence Reports** | Export Case Plain Text | `/api/reports/cases/<case_id>/export?format=txt` | `GET` | `format=txt` | TXT text file download (`Content-Disposition: attachment; filename=case_X_report.txt`) | **Integrated & Verified** | Formatted report with ASCII boundaries |

---

## 2. Cross-Origin Resource Sharing (CORS) Configuration

To enable the Vite frontend (`http://127.0.0.1:5173`) to communicate directly with the Flask backend (`http://127.0.0.1:5000`), development-only CORS was configured in `app.py`:

```python
from flask_cors import CORS

CORS(
    app,
    resources={r"/api/*": {"origins": [
        "http://127.0.0.1:5173", "http://localhost:5173",
        "http://127.0.0.1:3000", "http://localhost:3000",
        "http://127.0.0.1:4173", "http://localhost:4173"
    ]}},
    supports_credentials=True
)
```

No backend business logic, route handlers, or database schemas were modified.

---

## 3. Missing Backend Capabilities & Handled States

1. **Authentication / RBAC**:
   - The backend is a college academic demonstration without JWT or user session tables.
   - The frontend intentionally **does not display a fake logged-in user**. Instead, it surfaces clear academic labels and operator diagnostic indicators without pretending real auth exists.
2. **Batch Evidence Creation**:
   - Backend only supports single-item POST `/api/evidence`. The frontend handles single-item forms with validation.
3. **Graph Rendering Data**:
   - Backend exposes `/api/connections/graph/<case_id>` (which returns connected case IDs). For complete network visualization, the frontend fetches all active cases (`/api/cases`) and connections (`/api/connections`) to render the full interactive multi-node topology via Cytoscape.js.
