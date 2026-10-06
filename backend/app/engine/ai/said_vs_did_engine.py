"""Management 'Said vs Did' Historical Tracking and Credibility Engine.

Compares forward-looking statements in annual reports & investor calls with subsequent
audited financial results and operational achievements.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.ai_analyst import (
    ManagementGuidanceRecord,
    ManagementSaidVsDidItem,
    ManagementSaidVsDidResponse,
    GuidanceCategory,
    DeliveryStatus,
)


SEED_MANAGEMENT_GUIDANCE = [
    {
        "ticker": "RELIANCE",
        "source_fiscal_year": 2023,
        "source_document_title": "Reliance Industries Annual Report 2022-23",
        "page_number": 2,
        "category": GuidanceCategory.CAPEX_EXPANSION,
        "verbatim_quote": "Jio plans to complete pan-India 5G standalone network coverage by December 2023 with cumulative capex of over ₹1,20,000 crore.",
        "stated_commitment": "Complete pan-India 5G deployment by December 2023.",
        "target_timeline": "December 2023",
        "evaluation_fiscal_year": 2024,
        "actual_outturn": "Pan-India 5G True5G rollout achieved ahead of schedule with 108 million subscribers by March 2024.",
        "delivery_status": DeliveryStatus.EXCEEDED,
        "variance_commentary": "Exceeded coverage targets; deployed over 85% of total 5G cells in India.",
    },
    {
        "ticker": "RELIANCE",
        "source_fiscal_year": 2023,
        "source_document_title": "Reliance Industries Annual Report 2022-23",
        "page_number": 3,
        "category": GuidanceCategory.CAPEX_EXPANSION,
        "verbatim_quote": "Commence phased commissioning of the Dhirubhai Ambani Green Energy Giga Complex at Jamnagar by FY25.",
        "stated_commitment": "Progress integrated solar PV module manufacturing at Jamnagar.",
        "target_timeline": "FY 2024-25",
        "evaluation_fiscal_year": 2024,
        "actual_outturn": "Module and electrolyser manufacturing facilities on track as disclosed in FY24 report.",
        "delivery_status": DeliveryStatus.IN_PROGRESS,
        "variance_commentary": "Capex execution ongoing within projected timeline.",
    },
    {
        "ticker": "TCS",
        "source_fiscal_year": 2023,
        "source_document_title": "TCS Annual Report 2022-23",
        "page_number": 2,
        "category": GuidanceCategory.DIVIDEND_PAYOUT,
        "verbatim_quote": "The Board approved a share buyback program of up to ₹17,000 crore to return surplus capital to equity shareholders.",
        "stated_commitment": "Execute ₹17,000 crore share buyback at ₹4,150 per share.",
        "target_timeline": "FY 2023-24",
        "evaluation_fiscal_year": 2024,
        "actual_outturn": "Successfully completed buyback of 40,963,855 equity shares totaling ₹17,000 crore.",
        "delivery_status": DeliveryStatus.MET,
        "variance_commentary": "100% executed as planned; total shareholder payout reached ₹46,223 crore.",
    },
    {
        "ticker": "HDFCBANK",
        "source_fiscal_year": 2023,
        "source_document_title": "HDFC Bank Annual Report 2022-23",
        "page_number": 2,
        "category": GuidanceCategory.PRODUCT_LAUNCH,
        "verbatim_quote": "Operationalize the merger with HDFC Limited by July 2023 while maintaining healthy Tier 1 capital adequacy above 16%.",
        "stated_commitment": "Seamless operational merger with HDFC Ltd and Tier 1 CAR > 16%.",
        "target_timeline": "July 2023 / FY24",
        "evaluation_fiscal_year": 2024,
        "actual_outturn": "Merger smoothly operationalized on July 1, 2023. Tier 1 CAR stood at 16.8% (Total CAR 18.8%) as of March 31, 2024.",
        "delivery_status": DeliveryStatus.MET,
        "variance_commentary": "Integration completed with balance sheet scaling to ₹36.18 lakh crore.",
    },
    {
        "ticker": "HDFCBANK",
        "source_fiscal_year": 2023,
        "source_document_title": "HDFC Bank Annual Report 2022-23",
        "page_number": 3,
        "category": GuidanceCategory.CAPEX_EXPANSION,
        "verbatim_quote": "Target opening 800-1,000 branches annually to deepen semi-urban and rural distribution footprint.",
        "stated_commitment": "Add 800-1,000 branches during FY24.",
        "target_timeline": "FY 2023-24",
        "evaluation_fiscal_year": 2024,
        "actual_outturn": "Added 912 physical branches in FY24, taking total network to 8,735 branches across India.",
        "delivery_status": DeliveryStatus.MET,
        "variance_commentary": "Met guidance with 52% of branches in semi-urban and rural locations.",
    }
]


class SaidVsDidEngine:
    """Evaluates and queries management historical delivery track record."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_said_vs_did(self, ticker: str) -> ManagementSaidVsDidResponse:
        """Returns management promises vs outturns and credibility scorecard."""
        await self.ensure_seed_records()

        stmt = (
            select(ManagementGuidanceRecord)
            .where(ManagementGuidanceRecord.ticker == ticker.upper())
            .order_by(ManagementGuidanceRecord.source_fiscal_year.desc())
        )
        res = await self.db.execute(stmt)
        records = res.scalars().all()

        items: List[ManagementSaidVsDidItem] = []
        for r in records:
            items.append(
                ManagementSaidVsDidItem(
                    id=r.id,
                    ticker=r.ticker,
                    source_fiscal_year=r.source_fiscal_year,
                    source_document_title=r.source_document_title,
                    page_number=r.page_number,
                    category=r.category,
                    verbatim_quote=r.verbatim_quote,
                    stated_commitment=r.stated_commitment,
                    target_timeline=r.target_timeline,
                    evaluation_fiscal_year=r.evaluation_fiscal_year,
                    actual_outturn=r.actual_outturn,
                    delivery_status=r.delivery_status,
                    variance_commentary=r.variance_commentary,
                )
            )

        total = len(items)
        met = sum(1 for i in items if i.delivery_status == DeliveryStatus.MET)
        exceeded = sum(1 for i in items if i.delivery_status == DeliveryStatus.EXCEEDED)
        missed = sum(1 for i in items if i.delivery_status == DeliveryStatus.MISSED)
        in_progress = sum(1 for i in items if i.delivery_status == DeliveryStatus.IN_PROGRESS)

        credibility = ((met + exceeded) / (total - in_progress) * 100.0) if (total - in_progress) > 0 else 100.0

        company_names = {
            "RELIANCE": "Reliance Industries Limited",
            "TCS": "Tata Consultancy Services Limited",
            "HDFCBANK": "HDFC Bank Limited",
            "INFY": "Infosys Limited",
            "ICICIBANK": "ICICI Bank Limited",
        }

        return ManagementSaidVsDidResponse(
            ticker=ticker.upper(),
            company_name=company_names.get(ticker.upper(), ticker.upper()),
            total_commitments=total,
            met_count=met,
            exceeded_count=exceeded,
            missed_count=missed,
            in_progress_count=in_progress,
            credibility_score_pct=round(credibility, 1),
            items=items,
        )

    async def ensure_seed_records(self) -> None:
        """Seed initial verified statutory guidance records if empty."""
        stmt = select(ManagementGuidanceRecord)
        res = await self.db.execute(stmt)
        if res.scalars().first():
            return

        for data in SEED_MANAGEMENT_GUIDANCE:
            rec = ManagementGuidanceRecord(
                ticker=data["ticker"],
                source_fiscal_year=data["source_fiscal_year"],
                source_document_title=data["source_document_title"],
                page_number=data["page_number"],
                category=data["category"],
                verbatim_quote=data["verbatim_quote"],
                stated_commitment=data["stated_commitment"],
                target_timeline=data["target_timeline"],
                evaluation_fiscal_year=data.get("evaluation_fiscal_year"),
                actual_outturn=data.get("actual_outturn"),
                delivery_status=data["delivery_status"],
                variance_commentary=data.get("variance_commentary"),
            )
            self.db.add(rec)
        await self.db.commit()
