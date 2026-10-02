import sys
import os
import asyncio

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db.session import AsyncSessionLocal
from app.engine.ingestion_service import IngestionService
from app.fixtures.seed_data import ALL_FIXTURES


async def seed_database():
    """Load all fixtures through the deterministic IngestionService."""
    async with AsyncSessionLocal() as session:
        ingestion = IngestionService(session)
        print(f"[*] Starting ingestion of {len(ALL_FIXTURES)} fixture datasets...")
        
        for fixture in ALL_FIXTURES:
            comp_data = fixture["company"]
            print(f" -> Ingesting company: {comp_data['ticker']} ({comp_data['legal_name']})")
            company = await ingestion.ingest_company(comp_data)
            
            # Source Docs
            source_docs = []
            for s_data in fixture.get("source_documents", []):
                doc = await ingestion.ingest_source_document(s_data)
                source_docs.append(doc)
            primary_doc = source_docs[0] if source_docs else None

            # Financial Periods
            for p_data in fixture.get("periods", []):
                period = await ingestion.ingest_financial_period(company.id, p_data)
                print(f"    * Period {period.period_label}")

                # Income Statements
                for is_data in p_data.get("income_statements", []):
                    _, val_res = await ingestion.ingest_income_statement(period, is_data, primary_doc)
                    fails = [v for v in val_res if v.status == "FAILED"]
                    print(f"      - IS: {len(val_res)} validation checks ({len(fails)} failures)")

                # Balance Sheets
                for bs_data in p_data.get("balance_sheets", []):
                    _, val_res = await ingestion.ingest_balance_sheet(period, bs_data, primary_doc)
                    fails = [v for v in val_res if v.status == "FAILED"]
                    print(f"      - BS: {len(val_res)} validation checks ({len(fails)} failures)")

                # Cash Flows
                for cf_data in p_data.get("cash_flows", []):
                    _, val_res = await ingestion.ingest_cash_flow_statement(period, cf_data, primary_doc)
                    fails = [v for v in val_res if v.status == "FAILED"]
                    print(f"      - CF: {len(val_res)} validation checks ({len(fails)} failures)")

            # Corporate Actions
            for ca_data in fixture.get("corporate_actions", []):
                await ingestion.ingest_corporate_action(company.id, ca_data)
                print(f"    + Corporate Action: {ca_data['action_type']} on {ca_data['ex_date']}")

        await session.commit()
        print("[+] Seeding and deterministic validation complete!")


if __name__ == "__main__":
    asyncio.run(seed_database())
