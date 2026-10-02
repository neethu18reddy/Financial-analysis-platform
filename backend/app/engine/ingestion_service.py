"""Comprehensive Ingestion Service.

Orchestrates clean separation of concerns:
Source Acquisition / Fixture Loading -> Normalization -> Deterministic Validation -> Provenance Recording -> Storage.
"""

import json
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.source import SourceDocument, SourceType, DataClassification
from app.models.company import Company, Security
from app.models.financial_period import FinancialPeriod, PeriodType, ReportingStandard, FinancialUnit
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement, StatementType
from app.models.corporate_actions import CorporateAction, ActionType, ShareCountHistory
from app.models.provenance import DataProvenance
from app.models.validation import ValidationResult, ValidationStatus, ValidationCategory
from app.engine.normalizer import FinancialNormalizer
from app.engine.validator import DeterministicValidator
from app.engine.corporate_actions_calculator import CorporateActionsCalculator
from app.engine.provenance_tracker import ProvenanceTracker


class IngestionService:
    """End-to-end ingestion pipeline executing normalized ingestion with provenance and validation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def ingest_company(self, data: Dict[str, Any]) -> Company:
        """Upsert company record."""
        stmt = select(Company).where(Company.ticker == data["ticker"])
        result = await self.db.execute(stmt)
        company = result.scalar_one_or_none()

        if not company:
            company = Company(
                cin=data["cin"],
                ticker=data["ticker"],
                legal_name=data["legal_name"],
                trade_name=data.get("trade_name", data["legal_name"]),
                sector=data["sector"],
                industry=data["industry"],
                isin=data["isin"],
                primary_exchange=data.get("primary_exchange", "NSE"),
                founded_year=data.get("founded_year"),
                registered_state=data.get("registered_state"),
                description=data.get("description"),
                website=data.get("website"),
                is_active=data.get("is_active", True)
            )
            self.db.add(company)
            await self.db.flush()
        else:
            # Update fields
            company.legal_name = data["legal_name"]
            company.sector = data["sector"]
            company.industry = data["industry"]
            company.isin = data["isin"]
            company.description = data.get("description", company.description)
            await self.db.flush()

        # Handle Securities
        if "securities" in data:
            for sec_data in data["securities"]:
                sec_stmt = select(Security).where(
                    Security.company_id == company.id,
                    Security.symbol == sec_data["symbol"],
                    Security.exchange == sec_data.get("exchange", "NSE")
                )
                sec_res = await self.db.execute(sec_stmt)
                sec = sec_res.scalar_one_or_none()
                if not sec:
                    sec = Security(
                        company_id=company.id,
                        symbol=sec_data["symbol"],
                        series=sec_data.get("series", "EQ"),
                        isin=sec_data.get("isin", company.isin),
                        exchange=sec_data.get("exchange", "NSE"),
                        currency=sec_data.get("currency", "INR"),
                        lot_size=sec_data.get("lot_size", 1)
                    )
                    self.db.add(sec)
            await self.db.flush()

        return company

    async def ingest_source_document(self, data: Dict[str, Any]) -> SourceDocument:
        """Register source document preserving license and provenance origins."""
        source_doc = SourceDocument(
            document_name=data["document_name"],
            provider=data["provider"],
            source_type=SourceType(data.get("source_type", SourceType.AUDITED_FINANCIALS_FIXTURE)),
            data_classification=DataClassification(data.get("data_classification", DataClassification.REAL)),
            file_path_or_url=data.get("file_path_or_url"),
            filing_date=datetime.strptime(data["filing_date"], "%Y-%m-%d") if data.get("filing_date") else None,
            checksum_sha256=data.get("checksum_sha256"),
            terms_and_license=data.get("terms_and_license", "Direct statutory audited disclosure"),
            redistribution_allowed=data.get("redistribution_allowed", True),
            attribution_notes=data.get("attribution_notes"),
            raw_metadata_json=json.dumps(data.get("raw_metadata", {}))
        )
        self.db.add(source_doc)
        await self.db.flush()
        return source_doc

    async def ingest_financial_period(self, company_id: int, data: Dict[str, Any]) -> FinancialPeriod:
        """Upsert financial period record."""
        stmt = select(FinancialPeriod).where(
            FinancialPeriod.company_id == company_id,
            FinancialPeriod.period_type == PeriodType(data.get("period_type", PeriodType.ANNUAL)),
            FinancialPeriod.fiscal_year == data["fiscal_year"],
            FinancialPeriod.fiscal_quarter == data.get("fiscal_quarter")
        )
        result = await self.db.execute(stmt)
        period = result.scalar_one_or_none()

        start_dt = date.fromisoformat(data["start_date"]) if isinstance(data["start_date"], str) else data["start_date"]
        end_dt = date.fromisoformat(data["end_date"]) if isinstance(data["end_date"], str) else data["end_date"]
        filing_dt = date.fromisoformat(data["filing_date"]) if data.get("filing_date") and isinstance(data["filing_date"], str) else data.get("filing_date")

        if not period:
            period = FinancialPeriod(
                company_id=company_id,
                period_type=PeriodType(data.get("period_type", PeriodType.ANNUAL)),
                fiscal_year=data["fiscal_year"],
                fiscal_quarter=data.get("fiscal_quarter"),
                period_label=data.get("period_label", f"FY {data['fiscal_year']}"),
                start_date=start_dt,
                end_date=end_dt,
                filing_date=filing_dt,
                reporting_standard=ReportingStandard(data.get("reporting_standard", ReportingStandard.IND_AS)),
                currency=data.get("currency", "INR"),
                canonical_unit=FinancialUnit(data.get("canonical_unit", FinancialUnit.CRORES)),
                is_audited=data.get("is_audited", True)
            )
            self.db.add(period)
            await self.db.flush()
        return period

    async def ingest_income_statement(
        self,
        period: FinancialPeriod,
        data: Dict[str, Any],
        source_doc: Optional[SourceDocument] = None
    ) -> Tuple[IncomeStatement, List[ValidationResult]]:
        """Ingest, normalize, validate, and record provenance for Income Statement."""
        st_type = StatementType(data.get("statement_type", StatementType.CONSOLIDATED))
        from_unit = data.get("unit", FinancialUnit.CRORES)

        # Helper to normalize field
        def norm(k: str) -> float:
            raw = data.get(k, 0.0)
            parsed = FinancialNormalizer.parse_raw_string(raw)
            return FinancialNormalizer.normalize_to_crores(parsed, from_unit)

        stmt = select(IncomeStatement).where(
            IncomeStatement.period_id == period.id,
            IncomeStatement.statement_type == st_type
        )
        res = await self.db.execute(stmt)
        income_stmt = res.scalar_one_or_none()

        if not income_stmt:
            income_stmt = IncomeStatement(
                period_id=period.id,
                statement_type=st_type,
                revenue_from_operations=norm("revenue_from_operations"),
                other_income=norm("other_income"),
                total_revenue=norm("total_revenue"),
                cost_of_materials_consumed=norm("cost_of_materials_consumed"),
                purchases_of_stock_in_trade=norm("purchases_of_stock_in_trade"),
                changes_in_inventories=norm("changes_in_inventories"),
                employee_benefit_expenses=norm("employee_benefit_expenses"),
                finance_costs=norm("finance_costs"),
                depreciation_and_amortization=norm("depreciation_and_amortization"),
                other_expenses=norm("other_expenses"),
                total_expenses=norm("total_expenses"),
                operating_profit=norm("operating_profit"),
                profit_before_exceptional_items_and_tax=norm("profit_before_exceptional_items_and_tax"),
                exceptional_items=norm("exceptional_items"),
                profit_before_tax=norm("profit_before_tax"),
                current_tax=norm("current_tax"),
                deferred_tax=norm("deferred_tax"),
                total_tax_expense=norm("total_tax_expense"),
                profit_after_tax=norm("profit_after_tax"),
                minority_interest=norm("minority_interest"),
                share_of_profit_associates=norm("share_of_profit_associates"),
                net_profit_attributable_to_owners=norm("net_profit_attributable_to_owners"),
                basic_eps=data.get("basic_eps"),
                diluted_eps=data.get("diluted_eps"),
                raw_payload_json=json.dumps(data)
            )
            self.db.add(income_stmt)
            await self.db.flush()

        # Run Deterministic Validation
        val_results = DeterministicValidator.validate_income_statement(
            inc=income_stmt,
            period=period,
            company_id=period.company_id
        )
        for vr in val_results:
            self.db.add(vr)

        # Record Provenance if source document is present
        if source_doc:
            prov_items = [
                ("revenue_from_operations", "Revenue from Operations", data.get("revenue_from_operations"), income_stmt.revenue_from_operations),
                ("total_revenue", "Total Revenue", data.get("total_revenue"), income_stmt.total_revenue),
                ("total_expenses", "Total Expenses", data.get("total_expenses"), income_stmt.total_expenses),
                ("profit_before_tax", "Profit Before Tax", data.get("profit_before_tax"), income_stmt.profit_before_tax),
                ("profit_after_tax", "Profit After Tax (PAT)", data.get("profit_after_tax"), income_stmt.profit_after_tax),
                ("net_profit_attributable_to_owners", "Net Profit for the Period", data.get("net_profit_attributable_to_owners"), income_stmt.net_profit_attributable_to_owners)
            ]
            for field, label, raw_v, norm_v in prov_items:
                if raw_v is not None:
                    prov = ProvenanceTracker.create_field_provenance(
                        source_doc=source_doc,
                        entity_type="income_statements",
                        entity_id=income_stmt.id,
                        field_name=field,
                        reported_label=label,
                        reported_value_raw=str(raw_v),
                        reported_unit=str(from_unit),
                        normalized_value=norm_v,
                        page_number=data.get("page_number"),
                        table_reference=data.get("table_reference", "Statement of Profit and Loss"),
                        note_reference=data.get("note_reference")
                    )
                    self.db.add(prov)

        await self.db.flush()
        return income_stmt, val_results

    async def ingest_balance_sheet(
        self,
        period: FinancialPeriod,
        data: Dict[str, Any],
        source_doc: Optional[SourceDocument] = None
    ) -> Tuple[BalanceSheet, List[ValidationResult]]:
        """Ingest, normalize, validate, and record provenance for Balance Sheet."""
        st_type = StatementType(data.get("statement_type", StatementType.CONSOLIDATED))
        from_unit = data.get("unit", FinancialUnit.CRORES)

        def norm(k: str) -> float:
            raw = data.get(k, 0.0)
            parsed = FinancialNormalizer.parse_raw_string(raw)
            return FinancialNormalizer.normalize_to_crores(parsed, from_unit)

        stmt = select(BalanceSheet).where(
            BalanceSheet.period_id == period.id,
            BalanceSheet.statement_type == st_type
        )
        res = await self.db.execute(stmt)
        balance_sheet = res.scalar_one_or_none()

        if not balance_sheet:
            balance_sheet = BalanceSheet(
                period_id=period.id,
                statement_type=st_type,
                property_plant_equipment=norm("property_plant_equipment"),
                capital_work_in_progress=norm("capital_work_in_progress"),
                goodwill_and_intangibles=norm("goodwill_and_intangibles"),
                non_current_investments=norm("non_current_investments"),
                deferred_tax_assets=norm("deferred_tax_assets"),
                other_non_current_assets=norm("other_non_current_assets"),
                total_non_current_assets=norm("total_non_current_assets"),
                inventories=norm("inventories"),
                trade_receivables=norm("trade_receivables"),
                cash_and_cash_equivalents=norm("cash_and_cash_equivalents"),
                bank_balances_other=norm("bank_balances_other"),
                short_term_loans_and_advances=norm("short_term_loans_and_advances"),
                other_current_assets=norm("other_current_assets"),
                total_current_assets=norm("total_current_assets"),
                total_assets=norm("total_assets"),
                equity_share_capital=norm("equity_share_capital"),
                other_equity_and_reserves=norm("other_equity_and_reserves"),
                non_controlling_interests=norm("non_controlling_interests"),
                total_equity=norm("total_equity"),
                non_current_borrowings=norm("non_current_borrowings"),
                deferred_tax_liabilities=norm("deferred_tax_liabilities"),
                other_non_current_liabilities=norm("other_non_current_liabilities"),
                total_non_current_liabilities=norm("total_non_current_liabilities"),
                current_borrowings=norm("current_borrowings"),
                trade_payables=norm("trade_payables"),
                other_current_liabilities=norm("other_current_liabilities"),
                short_term_provisions=norm("short_term_provisions"),
                total_current_liabilities=norm("total_current_liabilities"),
                total_liabilities=norm("total_liabilities"),
                total_equity_and_liabilities=norm("total_equity_and_liabilities"),
                raw_payload_json=json.dumps(data)
            )
            self.db.add(balance_sheet)
            await self.db.flush()

        # Run Deterministic Validation
        val_results = DeterministicValidator.validate_balance_sheet(
            bs=balance_sheet,
            period=period,
            company_id=period.company_id
        )
        for vr in val_results:
            self.db.add(vr)

        # Record Provenance if source document is present
        if source_doc:
            prov_items = [
                ("total_assets", "Total Assets", data.get("total_assets"), balance_sheet.total_assets),
                ("total_equity", "Total Equity", data.get("total_equity"), balance_sheet.total_equity),
                ("total_liabilities", "Total Liabilities", data.get("total_liabilities"), balance_sheet.total_liabilities),
                ("total_equity_and_liabilities", "Total Equity & Liabilities", data.get("total_equity_and_liabilities"), balance_sheet.total_equity_and_liabilities),
                ("cash_and_cash_equivalents", "Cash and Cash Equivalents", data.get("cash_and_cash_equivalents"), balance_sheet.cash_and_cash_equivalents),
                ("inventories", "Inventories", data.get("inventories"), balance_sheet.inventories),
                ("trade_receivables", "Trade Receivables", data.get("trade_receivables"), balance_sheet.trade_receivables)
            ]
            for field, label, raw_v, norm_v in prov_items:
                if raw_v is not None:
                    prov = ProvenanceTracker.create_field_provenance(
                        source_doc=source_doc,
                        entity_type="balance_sheets",
                        entity_id=balance_sheet.id,
                        field_name=field,
                        reported_label=label,
                        reported_value_raw=str(raw_v),
                        reported_unit=str(from_unit),
                        normalized_value=norm_v,
                        page_number=data.get("page_number"),
                        table_reference=data.get("table_reference", "Balance Sheet")
                    )
                    self.db.add(prov)

        await self.db.flush()
        return balance_sheet, val_results

    async def ingest_cash_flow_statement(
        self,
        period: FinancialPeriod,
        data: Dict[str, Any],
        source_doc: Optional[SourceDocument] = None
    ) -> Tuple[CashFlowStatement, List[ValidationResult]]:
        """Ingest, normalize, validate, and record provenance for Cash Flow Statement."""
        st_type = StatementType(data.get("statement_type", StatementType.CONSOLIDATED))
        from_unit = data.get("unit", FinancialUnit.CRORES)

        def norm(k: str) -> float:
            raw = data.get(k, 0.0)
            parsed = FinancialNormalizer.parse_raw_string(raw)
            return FinancialNormalizer.normalize_to_crores(parsed, from_unit)

        stmt = select(CashFlowStatement).where(
            CashFlowStatement.period_id == period.id,
            CashFlowStatement.statement_type == st_type
        )
        res = await self.db.execute(stmt)
        cash_flow = res.scalar_one_or_none()

        if not cash_flow:
            cash_flow = CashFlowStatement(
                period_id=period.id,
                statement_type=st_type,
                cash_from_operating_activities=norm("cash_from_operating_activities"),
                cash_from_investing_activities=norm("cash_from_investing_activities"),
                cash_from_financing_activities=norm("cash_from_financing_activities"),
                net_increase_in_cash=norm("net_increase_in_cash"),
                foreign_exchange_effect=norm("foreign_exchange_effect"),
                cash_beginning_of_period=norm("cash_beginning_of_period"),
                cash_end_of_period=norm("cash_end_of_period"),
                capital_expenditure=norm("capital_expenditure"),
                free_cash_flow=norm("free_cash_flow"),
                dividend_paid=norm("dividend_paid"),
                raw_payload_json=json.dumps(data)
            )
            self.db.add(cash_flow)
            await self.db.flush()

        # Run Deterministic Validation
        val_results = DeterministicValidator.validate_cash_flow(
            cf=cash_flow,
            period=period,
            company_id=period.company_id
        )
        for vr in val_results:
            self.db.add(vr)

        # Record Provenance if source document is present
        if source_doc:
            prov_items = [
                ("cash_from_operating_activities", "Net Cash from Operating Activities", data.get("cash_from_operating_activities"), cash_flow.cash_from_operating_activities),
                ("cash_from_investing_activities", "Net Cash from Investing Activities", data.get("cash_from_investing_activities"), cash_flow.cash_from_investing_activities),
                ("cash_from_financing_activities", "Net Cash from Financing Activities", data.get("cash_from_financing_activities"), cash_flow.cash_from_financing_activities),
                ("net_increase_in_cash", "Net Increase in Cash and Cash Equivalents", data.get("net_increase_in_cash"), cash_flow.net_increase_in_cash),
                ("cash_end_of_period", "Cash and Cash Equivalents at End of Period", data.get("cash_end_of_period"), cash_flow.cash_end_of_period)
            ]
            for field, label, raw_v, norm_v in prov_items:
                if raw_v is not None:
                    prov = ProvenanceTracker.create_field_provenance(
                        source_doc=source_doc,
                        entity_type="cash_flow_statements",
                        entity_id=cash_flow.id,
                        field_name=field,
                        reported_label=label,
                        reported_value_raw=str(raw_v),
                        reported_unit=str(from_unit),
                        normalized_value=norm_v,
                        page_number=data.get("page_number"),
                        table_reference=data.get("table_reference", "Statement of Cash Flows")
                    )
                    self.db.add(prov)

        await self.db.flush()
        return cash_flow, val_results

    async def ingest_corporate_action(self, company_id: int, data: Dict[str, Any]) -> CorporateAction:
        """Ingest corporate action with factor calculation."""
        ex_dt = date.fromisoformat(data["ex_date"]) if isinstance(data["ex_date"], str) else data["ex_date"]
        rec_dt = date.fromisoformat(data["record_date"]) if data.get("record_date") and isinstance(data["record_date"], str) else data.get("record_date")
        
        act_type = ActionType(data["action_type"])
        num = data.get("ratio_numerator", 1.0)
        den = data.get("ratio_denominator", 1.0)
        adj_factor = CorporateActionsCalculator.calculate_adjustment_factor(act_type, num, den)

        ca = CorporateAction(
            company_id=company_id,
            action_type=act_type,
            ex_date=ex_dt,
            record_date=rec_dt,
            ratio_numerator=num,
            ratio_denominator=den,
            adjustment_factor=adj_factor,
            dividend_per_share=data.get("dividend_per_share"),
            notes=data.get("notes")
        )
        self.db.add(ca)
        await self.db.flush()
        return ca
