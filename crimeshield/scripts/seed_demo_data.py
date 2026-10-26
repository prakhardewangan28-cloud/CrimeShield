"""
Seed script for CRIMESHIELD college presentation / viva demonstration.
Inserts realistic, connected fictional cases and evidence into crimeshield.db.
"""

from pathlib import Path
import sys

base_dir = Path(r"C:\Users\prakh\OneDrive - Universal Ai University\Desktop\CrimeShield")
sys.path.insert(0, str(base_dir))

from crimeshield.config import DATABASE_PATH
from crimeshield.services.case_service import CaseService
from crimeshield.services.evidence_service import EvidenceService

def seed():
    print(f"Connecting to database: {DATABASE_PATH}")
    case_service = CaseService(DATABASE_PATH)
    evidence_service = EvidenceService(DATABASE_PATH)

    # 1. Create Case 1
    c1 = case_service.create_case(
        case_code="CASE-2026-VAL-01",
        title="Financial District Vault Penetration",
        description="Sophisticated unauthorized breach of subterranean safety deposit boxes at Manhattan Financial Depository. High-value gems and bearer bonds compromised.",
        location="40.7128,-74.0060",
        status="open"
    )
    print(f"Created Case 1: ID {c1.id} ({c1.case_code})")

    # 2. Create Case 2 (connected via phone and person)
    c2 = case_service.create_case(
        case_code="CASE-2026-HRB-02",
        title="Pier 42 Container Terminal Break-In",
        description="Armed hijacking of an industrial shipping container arriving from Antwerp. Surveillance recovered burner telecommunications and physical toolmarks.",
        location="40.7200,-74.0100",
        status="under_review"
    )
    print(f"Created Case 2: ID {c2.id} ({c2.case_code})")

    # 3. Create Case 3 (connected via person and location)
    c3 = case_service.create_case(
        case_code="CASE-2026-CYB-03",
        title="Midtown Shell Corporation Syndicate",
        description="Money laundering operation laundering cash through art auctions and offshore crypto cold-storage accounts.",
        location="40.7589,-73.9851",
        status="open"
    )
    print(f"Created Case 3: ID {c3.id} ({c3.case_code})")

    # 4. Attach Evidence to Case 1
    evidence_service.create_evidence(
        evidence_code="EVD-VAL-01-PHN",
        case_id=c1.id,
        evidence_type="telecom",
        description="Burner smartphone recovered near vault exhaust vent containing outgoing dispatch texts.",
        phone_reference="+1-555-0199",
        person_reference="Marcus Vance",
        location_reference="40.7128,-74.0060",
        processing_status="processed"
    )
    evidence_service.create_evidence(
        evidence_code="EVD-VAL-02-DOC",
        case_id=c1.id,
        evidence_type="document",
        description="Architectural blueprint of subterranean vault electrical grids with handwritten annotations.",
        person_reference="Elena Rostova",
        location_reference="40.7128,-74.0060",
        processing_status="pending"
    )

    # 5. Attach Evidence to Case 2 (matches phone +1-555-0199 and person Marcus Vance)
    evidence_service.create_evidence(
        evidence_code="EVD-HRB-01-SIM",
        case_id=c2.id,
        evidence_type="digital",
        description="Recovered SIM card found in abandoned getaway van near Pier 42.",
        phone_reference="+1-555-0199",
        person_reference="Marcus Vance",
        location_reference="40.7200,-74.0100",
        processing_status="processed"
    )
    evidence_service.create_evidence(
        evidence_code="EVD-HRB-02-PHY",
        case_id=c2.id,
        evidence_type="physical",
        description="Industrial hydraulic cutting shears matching vault penetration toolmarks.",
        location_reference="40.7200,-74.0100",
        processing_status="processed"
    )

    # 6. Attach Evidence to Case 3 (matches person Elena Rostova and nearby Manhattan location)
    evidence_service.create_evidence(
        evidence_code="EVD-CYB-01-REC",
        case_id=c3.id,
        evidence_type="document",
        description="Corporate registry documents listing executive board members and offshore trustees.",
        person_reference="Elena Rostova",
        location_reference="40.7589,-73.9851",
        processing_status="processed"
    )

    print("\n[SUCCESS] Seeded 3 cases and 5 connected evidence items.")
    print("Now go to 'Network Analysis' in CRIMESHIELD and click 'Run Network Analysis' to discover the links!")

if __name__ == "__main__":
    seed()
