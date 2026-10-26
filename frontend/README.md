# CRIMESHIELD — Criminal Network Analysis System (Frontend)
> **Tagline**: From Fragmented Evidence to Connected Intelligence  
> **Course**: Advanced Python College Mini-Project (October 2026)

---

## Overview

CRIMESHIELD is a professional intelligence analysis dashboard designed for criminal investigators. It correlates fragmented forensic evidence (locations, suspects, phone numbers) across independent cases to automatically uncover criminal networks using the Strategy Pattern and graph traversal algorithms.

This directory houses the **React 19 + TypeScript + Vite + Tailwind CSS** frontend, seamlessly integrated with the existing Flask + SQLite3 backend.

---

## Key Features

1. **Operational Intelligence Dashboard**:
   - Real-time case distribution charts (Recharts donut/bar).
   - Evidence vault status breakdown.
   - Live backend health & latency monitor.
   - Quick-access recent cases and correlation leads.
2. **Case Dossier Management**:
   - Searchable, filterable case table (Status: `open`, `under_review`, `closed`).
   - Create, edit, and expunge cases with full validation.
   - Case dossier inspection drawer with attached evidence and connection links.
3. **Forensic Evidence Vault**:
   - Multi-discipline evidence records (`physical`, `digital`, `document`, `testimonial`, `biometric`).
   - Reference fields for algorithmic matching (`location_reference`, `person_reference`, `phone_reference`).
   - Real case selector populated dynamically from Flask backend.
4. **Network Analysis Workspace**:
   - **"Run Network Analysis" button** wired to real backend POST `/api/analysis/run`.
   - Real-time performance metrics (execution time, evidence items scanned, new links created).
   - Interactive Cytoscape.js network graph with custom color coding, zoom, pan, and fit controls.
   - Node and edge inspection with direct lead review actions.
   - Mandatory investigative disclaimer notice.
5. **Connections Review & Adjudication Queue**:
   - Adjudicate correlation leads (`confirmed_for_review` vs `dismissed`).
   - Add formal legal review notes submitted via PATCH `/api/connections/<id>/review`.
6. **Intelligence Reports & Forensic Export**:
   - Real CSV and Plain Text (TXT) file downloads via `/api/reports/cases/<id>/export?format=csv|txt`.
   - System aggregate summary report.
7. **System Health & Diagnostic Suite**:
   - Automated probe of all Flask endpoints.
   - Copyable demonstration terminal commands for viva evaluation.

---

## Technology Stack

- **Framework**: React 19 + Vite 6
- **Language**: TypeScript 5.7 (Strict Mode)
- **Styling**: Tailwind CSS 3.4 (Investigative Dark Navy theme: `#080D18`, `#0D1422`, `#111C2D`, `#22D3EE`)
- **Routing**: React Router 7
- **Graph Visualization**: Cytoscape.js
- **Charts**: Recharts 3
- **Icons**: Lucide React

---

## Getting Started

### 1. Start the Flask Backend (Terminal 1)
```powershell
cd crimeshield
python app.py
```
*Backend runs on `http://127.0.0.1:5000`*

### 2. Start the Vite Frontend (Terminal 2)
```powershell
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://127.0.0.1:5173`*

### 3. Verify Production Build
```powershell
npm run build
```

---

## Demonstration Workflow for College Viva

1. **Inspect Dashboard**: Verify operational stats and backend connectivity pill (`Flask API Online`).
2. **Create Cases**: Add Case 1 ("Financial District Heist") and Case 2 ("Warehouse Break-in").
3. **Add Evidence**:
   - Case 1: Add phone evidence with `+1-555-0199` and person `Marcus Vance`.
   - Case 2: Add SIM card evidence with `+1-555-0199`.
4. **Run Network Analysis**: Click "Run Network Analysis" in the Network Analysis page.
5. **Inspect Graph**: View the newly formed edge linking Case 1 and Case 2.
6. **Review Connection**: Adjudicate the lead as "Confirmed for Review" with notes.
7. **Export Report**: Download court-admissible CSV and TXT reports from the Reports page.
