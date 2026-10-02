"""Golden Fixtures for Indian Listed Companies and Edge Case Validation Sets.

All datasets are explicitly labeled: REAL, SYNTHETIC, MOCK, or DERIVED.
"""

from typing import Dict, Any, List
from app.models.source import DataClassification, SourceType
from app.models.financial_period import PeriodType, ReportingStandard, FinancialUnit
from app.models.financial_statements import StatementType
from app.models.corporate_actions import ActionType

# 1. RELIANCE INDUSTRIES LIMITED (REAL Audited Data)
RELIANCE_FIXTURE: Dict[str, Any] = {
    "company": {
        "cin": "L17110MH1973PLC019786",
        "ticker": "RELIANCE",
        "legal_name": "Reliance Industries Limited",
        "trade_name": "RIL",
        "sector": "Energy & Petrochemicals",
        "industry": "Oil, Gas & Diversified",
        "isin": "INE002A01018",
        "primary_exchange": "NSE",
        "founded_year": 1973,
        "registered_state": "Maharashtra",
        "description": "Reliance Industries Limited is India's largest private sector enterprise with businesses in hydrocarbon exploration, refining, petrochemicals, retail, and digital telecommunications.",
        "website": "https://www.ril.com",
        "securities": [
            {"symbol": "RELIANCE", "exchange": "NSE", "series": "EQ", "isin": "INE002A01018"}
        ]
    },
    "source_documents": [
        {
            "document_name": "Reliance Industries Annual Report 2023-24 (Audited)",
            "provider": "AUDITED_ANNUAL_REPORTS",
            "source_type": SourceType.ANNUAL_REPORT_PDF,
            "data_classification": DataClassification.REAL,
            "file_path_or_url": "https://www.ril.com/investor-relations/financial-reporting",
            "filing_date": "2024-05-15",
            "terms_and_license": "Statutory Audited Disclosure under Companies Act 2013 / SEBI LODR Regulations 2015",
            "redistribution_allowed": True,
            "attribution_notes": "Audited standalone and consolidated statements published by Reliance Industries Limited."
        }
    ],
    "periods": [
        {
            "fiscal_year": 2024,
            "period_label": "FY 2023-24",
            "period_type": PeriodType.ANNUAL,
            "start_date": "2023-04-01",
            "end_date": "2024-03-31",
            "filing_date": "2024-05-15",
            "reporting_standard": ReportingStandard.IND_AS,
            "canonical_unit": FinancialUnit.CRORES,
            "currency": "INR",
            "is_audited": True,
            "income_statements": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "revenue_from_operations": 914472.0,
                    "other_income": 15927.0,
                    "total_revenue": 930399.0,
                    "cost_of_materials_consumed": 448406.0,
                    "purchases_of_stock_in_trade": 128956.0,
                    "changes_in_inventories": 2841.0,
                    "employee_benefit_expenses": 25699.0,
                    "finance_costs": 23293.0,
                    "depreciation_and_amortization": 50832.0,
                    "other_expenses": 144783.0,
                    "total_expenses": 824810.0,
                    "profit_before_exceptional_items_and_tax": 105589.0,
                    "exceptional_items": 0.0,
                    "profit_before_tax": 105589.0,
                    "current_tax": 22358.0,
                    "deferred_tax": 4183.0,
                    "total_tax_expense": 26541.0,
                    "profit_after_tax": 79020.0,
                    "minority_interest": 9380.0,
                    "share_of_profit_associates": 0.0,
                    "net_profit_attributable_to_owners": 69624.0,
                    "basic_eps": 102.97,
                    "diluted_eps": 102.97,
                    "page_number": 348
                }
            ],
            "balance_sheets": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "property_plant_equipment": 756412.0,
                    "capital_work_in_progress": 139108.0,
                    "goodwill_and_intangibles": 132470.0,
                    "non_current_investments": 141208.0,
                    "deferred_tax_assets": 0.0,
                    "other_non_current_assets": 120532.0,
                    "total_non_current_assets": 1289730.0,
                    "inventories": 142106.0,
                    "trade_receivables": 25052.0,
                    "cash_and_cash_equivalents": 98930.0,
                    "bank_balances_other": 113425.0,
                    "short_term_loans_and_advances": 32014.0,
                    "other_current_assets": 68533.0,
                    "total_current_assets": 480060.0,
                    "total_assets": 1769790.0,
                    "equity_share_capital": 6766.0,
                    "other_equity_and_reserves": 786358.0,
                    "non_controlling_interests": 134120.0,
                    "total_equity": 927244.0,
                    "non_current_borrowings": 224398.0,
                    "deferred_tax_liabilities": 77218.0,
                    "other_non_current_liabilities": 54120.0,
                    "total_non_current_liabilities": 355736.0,
                    "current_borrowings": 100228.0,
                    "trade_payables": 196580.0,
                    "other_current_liabilities": 173812.0,
                    "short_term_provisions": 16190.0,
                    "total_current_liabilities": 486810.0,
                    "total_liabilities": 842546.0,
                    "total_equity_and_liabilities": 1769790.0,
                    "page_number": 346
                }
            ],
            "cash_flows": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "cash_from_operating_activities": 157294.0,
                    "cash_from_investing_activities": -118432.0,
                    "cash_from_financing_activities": -32654.0,
                    "net_increase_in_cash": 6208.0,
                    "foreign_exchange_effect": 0.0,
                    "cash_beginning_of_period": 92722.0,
                    "cash_end_of_period": 98930.0,
                    "capital_expenditure": 131769.0,
                    "free_cash_flow": 25525.0,
                    "dividend_paid": 6089.0,
                    "page_number": 350
                }
            ]
        },
        {
            "fiscal_year": 2023,
            "period_label": "FY 2022-23",
            "period_type": PeriodType.ANNUAL,
            "start_date": "2022-04-01",
            "end_date": "2023-03-31",
            "filing_date": "2023-05-18",
            "reporting_standard": ReportingStandard.IND_AS,
            "canonical_unit": FinancialUnit.CRORES,
            "currency": "INR",
            "is_audited": True,
            "income_statements": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "revenue_from_operations": 892915.0,
                    "other_income": 11848.0,
                    "total_revenue": 904763.0,
                    "cost_of_materials_consumed": 444390.0,
                    "purchases_of_stock_in_trade": 105655.0,
                    "changes_in_inventories": -15632.0,
                    "employee_benefit_expenses": 24888.0,
                    "finance_costs": 19571.0,
                    "depreciation_and_amortization": 40303.0,
                    "other_expenses": 196328.0,
                    "total_expenses": 815503.0,
                    "profit_before_exceptional_items_and_tax": 89260.0,
                    "exceptional_items": 0.0,
                    "profit_before_tax": 89260.0,
                    "current_tax": 17804.0,
                    "deferred_tax": 4774.0,
                    "total_tax_expense": 22578.0,
                    "profit_after_tax": 66682.0,
                    "minority_interest": 9974.0,
                    "share_of_profit_associates": 0.0,
                    "net_profit_attributable_to_owners": 56708.0,
                    "basic_eps": 98.53,
                    "diluted_eps": 98.53,
                    "page_number": 320
                }
            ],
            "balance_sheets": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "property_plant_equipment": 692804.0,
                    "capital_work_in_progress": 140360.0,
                    "goodwill_and_intangibles": 118940.0,
                    "non_current_investments": 128450.0,
                    "deferred_tax_assets": 0.0,
                    "other_non_current_assets": 111356.0,
                    "total_non_current_assets": 1191910.0,
                    "inventories": 139988.0,
                    "trade_receivables": 23512.0,
                    "cash_and_cash_equivalents": 92722.0,
                    "bank_balances_other": 98450.0,
                    "short_term_loans_and_advances": 28410.0,
                    "other_current_assets": 64808.0,
                    "total_current_assets": 447890.0,
                    "total_assets": 1639800.0,
                    "equity_share_capital": 6765.0,
                    "other_equity_and_reserves": 709565.0,
                    "non_controlling_interests": 122470.0,
                    "total_equity": 838800.0,
                    "non_current_borrowings": 218540.0,
                    "deferred_tax_liabilities": 70850.0,
                    "other_non_current_liabilities": 48210.0,
                    "total_non_current_liabilities": 337600.0,
                    "current_borrowings": 95400.0,
                    "trade_payables": 185600.0,
                    "other_current_liabilities": 167400.0,
                    "short_term_provisions": 15000.0,
                    "total_current_liabilities": 463400.0,
                    "total_liabilities": 801000.0,
                    "total_equity_and_liabilities": 1639800.0,
                    "page_number": 318
                }
            ],
            "cash_flows": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "cash_from_operating_activities": 114880.0,
                    "cash_from_investing_activities": -98450.0,
                    "cash_from_financing_activities": -13200.0,
                    "net_increase_in_cash": 3230.0,
                    "foreign_exchange_effect": 0.0,
                    "cash_beginning_of_period": 89492.0,
                    "cash_end_of_period": 92722.0,
                    "capital_expenditure": 125000.0,
                    "free_cash_flow": -10120.0,
                    "dividend_paid": 5412.0,
                    "page_number": 322
                }
            ]
        }
    ],
    "corporate_actions": [
        {
            "action_type": ActionType.DIVIDEND,
            "ex_date": "2024-08-19",
            "record_date": "2024-08-19",
            "dividend_per_share": 10.0,
            "notes": "Final dividend of Rs 10 per equity share for FY 2023-24"
        },
        {
            "action_type": ActionType.BONUS_ISSUE,
            "ex_date": "2024-10-28",
            "record_date": "2024-10-28",
            "ratio_numerator": 1.0,
            "ratio_denominator": 1.0,
            "notes": "1:1 Bonus share issue"
        }
    ]
}

# 2. TATA CONSULTANCY SERVICES (REAL Audited Data)
TCS_FIXTURE: Dict[str, Any] = {
    "company": {
        "cin": "L22210MH1995PLC084781",
        "ticker": "TCS",
        "legal_name": "Tata Consultancy Services Limited",
        "trade_name": "TCS",
        "sector": "Information Technology",
        "industry": "IT Services & Consulting",
        "isin": "INE467B01029",
        "primary_exchange": "NSE",
        "founded_year": 1968,
        "registered_state": "Maharashtra",
        "description": "Tata Consultancy Services is a world-leading IT services, consulting and business solutions organization.",
        "website": "https://www.tcs.com",
        "securities": [
            {"symbol": "TCS", "exchange": "NSE", "series": "EQ", "isin": "INE467B01029"}
        ]
    },
    "source_documents": [
        {
            "document_name": "TCS Annual Integrated Report 2023-24 (Audited)",
            "provider": "AUDITED_ANNUAL_REPORTS",
            "source_type": SourceType.ANNUAL_REPORT_PDF,
            "data_classification": DataClassification.REAL,
            "file_path_or_url": "https://www.tcs.com/investor-relations/annual-reports",
            "filing_date": "2024-04-12",
            "terms_and_license": "Statutory Audited Disclosure under Companies Act 2013",
            "redistribution_allowed": True,
            "attribution_notes": "Audited standalone and consolidated statements published by Tata Consultancy Services Limited."
        }
    ],
    "periods": [
        {
            "fiscal_year": 2024,
            "period_label": "FY 2023-24",
            "period_type": PeriodType.ANNUAL,
            "start_date": "2023-04-01",
            "end_date": "2024-03-31",
            "filing_date": "2024-04-12",
            "reporting_standard": ReportingStandard.IND_AS,
            "canonical_unit": FinancialUnit.CRORES,
            "currency": "INR",
            "is_audited": True,
            "income_statements": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "revenue_from_operations": 240893.0,
                    "other_income": 4184.0,
                    "total_revenue": 245077.0,
                    "cost_of_materials_consumed": 0.0,
                    "purchases_of_stock_in_trade": 0.0,
                    "changes_in_inventories": 0.0,
                    "employee_benefit_expenses": 139126.0,
                    "finance_costs": 1058.0,
                    "depreciation_and_amortization": 4983.0,
                    "other_expenses": 38781.0,
                    "total_expenses": 183948.0,
                    "profit_before_exceptional_items_and_tax": 61129.0,
                    "exceptional_items": 958.0,
                    "profit_before_tax": 60171.0,
                    "current_tax": 14758.0,
                    "deferred_tax": -413.0,
                    "total_tax_expense": 14345.0,
                    "profit_after_tax": 45826.0,
                    "minority_interest": 243.0,
                    "share_of_profit_associates": 0.0,
                    "net_profit_attributable_to_owners": 45583.0,
                    "basic_eps": 125.88,
                    "diluted_eps": 125.88,
                    "page_number": 210
                }
            ],
            "balance_sheets": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "property_plant_equipment": 22350.0,
                    "capital_work_in_progress": 1820.0,
                    "goodwill_and_intangibles": 4910.0,
                    "non_current_investments": 3280.0,
                    "deferred_tax_assets": 2490.0,
                    "other_non_current_assets": 9860.0,
                    "total_non_current_assets": 44710.0,
                    "inventories": 25.0,
                    "trade_receivables": 48920.0,
                    "cash_and_cash_equivalents": 12340.0,
                    "bank_balances_other": 18450.0,
                    "short_term_loans_and_advances": 3120.0,
                    "other_current_assets": 19685.0,
                    "total_current_assets": 102540.0,
                    "total_assets": 147250.0,
                    "equity_share_capital": 362.0,
                    "other_equity_and_reserves": 90138.0,
                    "non_controlling_interests": 780.0,
                    "total_equity": 91280.0,
                    "non_current_borrowings": 0.0,
                    "deferred_tax_liabilities": 1420.0,
                    "other_non_current_liabilities": 8940.0,
                    "total_non_current_liabilities": 10360.0,
                    "current_borrowings": 0.0,
                    "trade_payables": 11840.0,
                    "other_current_liabilities": 31820.0,
                    "short_term_provisions": 1950.0,
                    "total_current_liabilities": 45610.0,
                    "total_liabilities": 55970.0,
                    "total_equity_and_liabilities": 147250.0,
                    "page_number": 208
                }
            ],
            "cash_flows": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "cash_from_operating_activities": 44342.0,
                    "cash_from_investing_activities": -1382.0,
                    "cash_from_financing_activities": -41820.0,
                    "net_increase_in_cash": 1140.0,
                    "foreign_exchange_effect": 0.0,
                    "cash_beginning_of_period": 11200.0,
                    "cash_end_of_period": 12340.0,
                    "capital_expenditure": 3100.0,
                    "free_cash_flow": 41242.0,
                    "dividend_paid": 36190.0,
                    "page_number": 212
                }
            ]
        }
    ],
    "corporate_actions": [
        {
            "action_type": ActionType.DIVIDEND,
            "ex_date": "2024-05-16",
            "record_date": "2024-05-16",
            "dividend_per_share": 28.0,
            "notes": "Final dividend Rs 28 per share"
        },
        {
            "action_type": ActionType.BUYBACK,
            "ex_date": "2023-11-25",
            "record_date": "2023-11-25",
            "notes": "Share buyback at Rs 4,150 per share (Aggregate Rs 17,000 Cr)"
        }
    ]
}

# 3. SYNTHETIC BROKEN BALANCE SHEET FIXTURE (Validation Rejection Test)
BROKEN_BALANCE_SHEET_FIXTURE: Dict[str, Any] = {
    "company": {
        "cin": "U99999MH2024PTC999991",
        "ticker": "SYNTH_BROKEN_BS",
        "legal_name": "Synthetic Broken Balance Sheet Corporation",
        "trade_name": "Broken BS Corp",
        "sector": "Testing",
        "industry": "Synthetic Mismatch Testing",
        "isin": "INE999A01099",
        "primary_exchange": "NSE",
        "securities": [{"symbol": "SYNTH_BROKEN_BS", "exchange": "NSE", "series": "EQ", "isin": "INE999A01099"}]
    },
    "source_documents": [
        {
            "document_name": "Synthetic Broken BS Fixture v1.0",
            "provider": "FIXTURE_ENGINE",
            "source_type": SourceType.MOCK_FIXTURE,
            "data_classification": DataClassification.SYNTHETIC,
            "terms_and_license": "MIT Test Harness",
            "redistribution_allowed": True
        }
    ],
    "periods": [
        {
            "fiscal_year": 2024,
            "period_label": "FY 2023-24",
            "period_type": PeriodType.ANNUAL,
            "start_date": "2023-04-01",
            "end_date": "2024-03-31",
            "reporting_standard": ReportingStandard.IND_AS,
            "canonical_unit": FinancialUnit.CRORES,
            "currency": "INR",
            "income_statements": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "revenue_from_operations": 1000.0,
                    "other_income": 50.0,
                    "total_revenue": 1050.0,
                    "total_expenses": 800.0,
                    "profit_before_tax": 250.0,
                    "total_tax_expense": 50.0,
                    "profit_after_tax": 200.0,
                    "net_profit_attributable_to_owners": 200.0
                }
            ],
            "balance_sheets": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "total_non_current_assets": 500.0,
                    "total_current_assets": 300.0,
                    "total_assets": 800.0,  # 500 + 300 = 800
                    "total_equity": 400.0,
                    "total_non_current_liabilities": 200.0,
                    "total_current_liabilities": 100.0,
                    # Intentional mismatch: 400 + 200 + 100 = 700 != 800
                    "total_liabilities": 300.0,
                    "total_equity_and_liabilities": 700.0
                }
            ],
            "cash_flows": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "cash_from_operating_activities": 150.0,
                    "cash_from_investing_activities": -50.0,
                    "cash_from_financing_activities": -50.0,
                    "net_increase_in_cash": 50.0,
                    "cash_beginning_of_period": 100.0,
                    "cash_end_of_period": 150.0
                }
            ]
        }
    ]
}

# 4. SYNTHETIC BROKEN CASH FLOW FIXTURE (Validation Rejection Test)
BROKEN_CASH_FLOW_FIXTURE: Dict[str, Any] = {
    "company": {
        "cin": "U99999MH2024PTC999992",
        "ticker": "SYNTH_BROKEN_CF",
        "legal_name": "Synthetic Broken Cash Flow Corporation",
        "trade_name": "Broken CF Corp",
        "sector": "Testing",
        "industry": "Synthetic Mismatch Testing",
        "isin": "INE999A01098",
        "primary_exchange": "NSE",
        "securities": [{"symbol": "SYNTH_BROKEN_CF", "exchange": "NSE", "series": "EQ", "isin": "INE999A01098"}]
    },
    "source_documents": [
        {
            "document_name": "Synthetic Broken CF Fixture v1.0",
            "provider": "FIXTURE_ENGINE",
            "source_type": SourceType.MOCK_FIXTURE,
            "data_classification": DataClassification.SYNTHETIC,
            "terms_and_license": "MIT Test Harness",
            "redistribution_allowed": True
        }
    ],
    "periods": [
        {
            "fiscal_year": 2024,
            "period_label": "FY 2023-24",
            "period_type": PeriodType.ANNUAL,
            "start_date": "2023-04-01",
            "end_date": "2024-03-31",
            "reporting_standard": ReportingStandard.IND_AS,
            "canonical_unit": FinancialUnit.CRORES,
            "currency": "INR",
            "income_statements": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "revenue_from_operations": 500.0,
                    "total_revenue": 500.0,
                    "total_expenses": 400.0,
                    "profit_before_tax": 100.0,
                    "total_tax_expense": 25.0,
                    "profit_after_tax": 75.0,
                    "net_profit_attributable_to_owners": 75.0
                }
            ],
            "balance_sheets": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "total_non_current_assets": 200.0,
                    "total_current_assets": 100.0,
                    "total_assets": 300.0,
                    "total_equity": 200.0,
                    "total_non_current_liabilities": 50.0,
                    "total_current_liabilities": 50.0,
                    "total_liabilities": 100.0,
                    "total_equity_and_liabilities": 300.0
                }
            ],
            "cash_flows": [
                {
                    "statement_type": StatementType.CONSOLIDATED,
                    "unit": FinancialUnit.CRORES,
                    "cash_from_operating_activities": 100.0,
                    "cash_from_investing_activities": -40.0,
                    "cash_from_financing_activities": -30.0,
                    "net_increase_in_cash": 30.0,
                    "cash_beginning_of_period": 100.0,
                    # Intentional mismatch: 100 + 30 = 130 != 200
                    "cash_end_of_period": 200.0
                }
            ]
        }
    ]
}

ALL_FIXTURES = [
    RELIANCE_FIXTURE,
    TCS_FIXTURE,
    BROKEN_BALANCE_SHEET_FIXTURE,
    BROKEN_CASH_FLOW_FIXTURE
]
