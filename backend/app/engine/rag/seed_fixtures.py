"""Seed statutory Annual Report fixtures for Indian Equities (NSE/BSE).

Provides realistic multi-page annual report filings with full section structure,
page numbers, and financial disclosures for:
- RELIANCE (Reliance Industries Limited - FY 2023-24)
- TCS (Tata Consultancy Services Limited - FY 2023-24)
- HDFCBANK (HDFC Bank Limited - FY 2023-24)
"""

from typing import List, Dict, Any

SEED_ANNUAL_REPORTS: List[Dict[str, Any]] = [
    {
        "ticker": "RELIANCE",
        "fiscal_year": 2024,
        "title": "Reliance Industries Limited Integrated Annual Report 2023-24",
        "file_name": "RIL_Integrated_Annual_Report_FY24.pdf",
        "source_url": "https://www.ril.com/investor-relations/financial-reporting",
        "pages": [
            {
                "page_number": 1,
                "section": "GENERAL_CORPORATE_INFORMATION",
                "text": """RELIANCE INDUSTRIES LIMITED
INTEGRATED ANNUAL REPORT 2023-24
GROWTH FOR ALL - TRANSFORMING INDIA'S DIGITAL & ENERGY LANDSCAPE

Corporate Overview:
Reliance Industries Limited (RIL) is India's largest private sector company, with consolidated gross revenue of ₹10,00,122 crore (US$ 119.9 billion) for the financial year ended March 31, 2024.
Consolidated EBITDA stood at ₹1,78,677 crore (US$ 21.4 billion), up 16.1% YoY, driven by robust performance in Consumer businesses and upstream Oil & Gas segment.
Net profit for the year was ₹79,020 crore (US$ 9.5 billion).
Exports from RIL's India operations stood at ₹2,99,832 crore (US$ 36.0 billion).

Segment Contributions to Consolidated EBITDA:
- Jio Platforms (Digital Services): ₹52,438 crore (29.3% contribution)
- Reliance Retail Ventures: ₹23,082 crore (12.9% contribution)
- Oil to Chemicals (O2C): ₹62,393 crore (34.9% contribution)
- Oil and Gas Exploration & Production: ₹20,191 crore (11.3% contribution)
- Others & Treasury: ₹20,573 crore (11.5% contribution)"""
            },
            {
                "page_number": 2,
                "section": "DIRECTORS_REPORT",
                "text": """DIRECTORS' REPORT TO THE SHAREHOLDERS

Capital Expenditure & Project Execution:
During FY 2023-24, RIL incurred consolidated capital expenditure (capex) of ₹1,31,769 crore (US$ 15.8 billion), primarily directed towards the pan-India 5G rollout for Jio True5G, retail store footprint expansion, and initial infrastructure investments for the Dhirubhai Ambani Green Energy Giga Complex at Jamnagar.

Dividend Recommendation:
The Board of Directors has recommended a dividend of ₹10.00 per fully paid-up equity share of ₹10 each for the financial year ended March 31, 2024, reflecting our enduring commitment to shareholder value creation.

Credit Ratings:
RIL continued to maintain investment-grade credit ratings above India's sovereign rating from international rating agencies:
- Moody's: Baa2 (Stable Outlook)
- S&P: BBB+ (Stable Outlook)
- CRISIL / India Ratings: AAA (Stable)"""
            },
            {
                "page_number": 3,
                "section": "MANAGEMENT_DISCUSSION_AND_ANALYSIS",
                "text": """MANAGEMENT DISCUSSION AND ANALYSIS (MD&A)

Digital Services - Jio Platforms Limited:
Jio continued its leadership in 5G adoption, crossing 108 million 5G subscribers and deploying over 85% of total 5G cells in India. Monthly per capita data consumption rose to 28.7 GB with total network data traffic reaching 148.5 Exabytes during the year. Total customer base reached 481.8 million.

Retail Ventures:
Reliance Retail expanded its physical footprint to 18,836 stores covering 79.1 million sq. ft., recording over 1.06 billion customer transactions. Registered customer base expanded to 304 million.

Oil-to-Chemicals (O2C) & New Energy:
Despite global refining margin headwinds and volatile crude prices, O2C segment demonstrated operational flexibility, processing 70.8 MMT of crude. The New Energy business achieved significant milestones in setting up integrated solar PV module manufacturing and green hydrogen electrolyser facilities at Jamnagar."""
            },
            {
                "page_number": 4,
                "section": "INDEPENDENT_AUDITORS_REPORT",
                "text": """INDEPENDENT AUDITOR'S REPORT
To the Members of Reliance Industries Limited

Opinion:
We have audited the consolidated financial statements of Reliance Industries Limited and its subsidiaries, which comprise the Consolidated Balance Sheet as at March 31, 2024, the Consolidated Statement of Profit and Loss, and the Consolidated Statement of Cash Flows for the year then ended.
In our opinion and to the best of our information and according to the explanations given to us, the aforesaid consolidated financial statements give a true and fair view in conformity with Ind AS and the accounting principles generally accepted in India.

Key Audit Matters:
1. Impairment assessment of Goodwill and Property, Plant and Equipment in E&P and Telecom assets. We evaluated management's discount rates, future cash flow projections, and reserve estimation reports.
2. Revenue recognition across complex digital telecom contracts and retail loyalty programs.
3. Valuation and classification of complex derivative financial instruments.

Internal Financial Controls:
In our opinion, the Company has, in all material respects, an adequate internal financial controls system over financial reporting and such controls were operating effectively as at March 31, 2024."""
            },
            {
                "page_number": 5,
                "section": "NOTES_TO_CONSOLIDATED_FINANCIAL_STATEMENTS",
                "text": """NOTES TO CONSOLIDATED FINANCIAL STATEMENTS
FOR THE YEAR ENDED MARCH 31, 2024

Note 28: Related Party Disclosures (Ind AS 24)
Transactions with Key Management Personnel (KMP) and joint ventures:
- Total managerial remuneration approved in accordance with Section 197 of the Companies Act, 2013: ₹24.5 crore.
- Sales of goods/services to Joint Ventures / Associates: ₹14,820 crore.
- Purchases from Joint Ventures / Associates: ₹22,110 crore.
All related party contracts are entered at arm's length basis and in the ordinary course of business.

Note 34: Contingent Liabilities and Commitments
- Guarantees issued on behalf of joint ventures and subsidiaries: ₹18,450 crore.
- Disputed customs, excise, and GST matters pending before appellate authorities: ₹8,920 crore.
- Outstanding capital commitments contracted but not provided for: ₹42,180 crore (primarily relating to telecom and new energy assets)."""
            }
        ]
    },
    {
        "ticker": "TCS",
        "fiscal_year": 2024,
        "title": "Tata Consultancy Services Limited Integrated Annual Report 2023-24",
        "file_name": "TCS_Annual_Report_FY24.pdf",
        "source_url": "https://www.tcs.com/investor-relations/financial-statements",
        "pages": [
            {
                "page_number": 1,
                "section": "GENERAL_CORPORATE_INFORMATION",
                "text": """TATA CONSULTANCY SERVICES LIMITED
ANNUAL REPORT 2023-24
INNOVATION, RESILIENCE AND LONG-TERM VALUE CREATION

Financial Performance Highlights:
- Consolidated Revenue: ₹2,40,893 crore (US$ 29.1 billion), growing 6.8% YoY in constant currency.
- Operating Margin (EBIT): 24.6%, expanding 50 bps YoY despite macroeconomic headwinds.
- Net Income (PAT): ₹46,099 crore (US$ 5.56 billion), recording net margin of 19.1%.
- Total Contract Value (TCV) order book stood at an all-time high of $42.7 billion.
- Free Cash Flow conversion: 100.4% of net income, generating ₹44,282 crore in free cash flow."""
            },
            {
                "page_number": 2,
                "section": "DIRECTORS_REPORT",
                "text": """DIRECTORS' REPORT TO THE MEMBERS

Capital Return & Share Buyback:
During FY 2023-24, TCS returned ₹46,223 crore to shareholders through dividends and share buyback:
- Completed share buyback of 40,963,855 equity shares at ₹4,150 per share, totaling ₹17,000 crore.
- Total dividend for the year: ₹73.00 per share (including final dividend of ₹28.00 and special dividend of ₹18.00).

Human Capital & Talent:
Total employee headcount stood at 601,546 as on March 31, 2024, representing 152 nationalities with 35.6% women in the workforce. TCS trained over 350,000 employees in foundational AI and Generative AI skills."""
            },
            {
                "page_number": 3,
                "section": "MANAGEMENT_DISCUSSION_AND_ANALYSIS",
                "text": """MANAGEMENT DISCUSSION AND ANALYSIS (MD&A)

Industry Trends & Market Overview:
Enterprises worldwide prioritized cost optimization, vendor consolidation, and operating model transformations while continuing selective investments in AI, Cloud, and Cybersecurity.

Segment Performance:
- BFSI (Banking, Financial Services & Insurance): ₹91,540 crore (38.0% of revenue)
- Consumer Business & Retail: ₹37,820 crore (15.7% of revenue)
- Life Sciences & Healthcare: ₹26,500 crore (11.0% of revenue)
- Manufacturing: ₹23,600 crore (9.8% of revenue)
- Technology & Services: ₹20,950 crore (8.7% of revenue)

Generative AI Pipeline:
TCS built a dedicated AI/GenAI services practice with an active pipeline exceeding $900 million, deploying proprietary platforms like TCS AI WisdomNext and enterprise co-pilots."""
            },
            {
                "page_number": 4,
                "section": "INDEPENDENT_AUDITORS_REPORT",
                "text": """INDEPENDENT AUDITOR'S REPORT
To the Members of Tata Consultancy Services Limited

Report on the Audit of Consolidated Financial Statements:
We have audited the consolidated financial statements of Tata Consultancy Services Limited and its subsidiaries, comprising the Balance Sheet as at March 31, 2024, the Statement of Profit and Loss, and the Cash Flow Statement.
In our opinion, the accompanying consolidated financial statements give a true and fair view in conformity with Ind AS.

Key Audit Matters:
1. Fixed Price Contracts & Unbilled Revenue: Estimation of costs to complete and percentage of completion revenue recognition. We tested management's project governance controls, billing reconciliation, and historical estimation accuracy.
2. Tax Provisions and Contingent Tax Liabilities: Assessment of direct tax matters involving transfer pricing and overseas branch taxation.

Auditor Independence:
We confirm that we are independent of the Group in accordance with the Code of Ethics issued by the Institute of Chartered Accountants of India (ICAI)."""
            },
            {
                "page_number": 5,
                "section": "NOTES_TO_CONSOLIDATED_FINANCIAL_STATEMENTS",
                "text": """NOTES FORMING PART OF THE CONSOLIDATED FINANCIAL STATEMENTS
FOR THE YEAR ENDED MARCH 31, 2024

Note 31: Related Party Disclosures
- Transactions with Tata Sons Private Limited (Promoter Entity): Brand equity contribution fee of ₹185 crore.
- Operating lease rentals and shared service charges paid to Tata group companies: ₹240 crore.
- All transactions were conducted on an arm's length basis.

Note 33: Contingent Liabilities & Legal Claims
- Direct and indirect tax matters under appeal: ₹4,120 crore. Management does not expect any material financial outflow.
- Other claims against the Company not acknowledged as debt: ₹380 crore.
- Capital commitments for infrastructure development and software licenses: ₹1,850 crore."""
            }
        ]
    },
    {
        "ticker": "HDFCBANK",
        "fiscal_year": 2024,
        "title": "HDFC Bank Limited Integrated Annual Report 2023-24",
        "file_name": "HDFCBANK_Annual_Report_FY24.pdf",
        "source_url": "https://www.hdfcbank.com/personal/about-us/investor-relations",
        "pages": [
            {
                "page_number": 1,
                "section": "GENERAL_CORPORATE_INFORMATION",
                "text": """HDFC BANK LIMITED
INTEGRATED ANNUAL REPORT 2023-24
SCALE, STABILITY AND NATION BUILDING - POST MERGER TRANSFORMATION

Key Highlights (First Full Year Post Merger with HDFC Limited):
- Total Balance Sheet size reached ₹36,17,623 crore (US$ 434 billion) as on March 31, 2024.
- Total Deposits stood at ₹23,79,786 crore, up 26.4% YoY; CASA ratio stood at 38.2%.
- Gross Advances reached ₹24,84,861 crore, recording 55.4% YoY growth including merged mortgage portfolio.
- Net Interest Income (NII) for FY24 stood at ₹1,08,532 crore.
- Consolidated Net Profit (PAT) was ₹64,060 crore."""
            },
            {
                "page_number": 2,
                "section": "DIRECTORS_REPORT",
                "text": """DIRECTORS' REPORT TO SHAREHOLDERS

Merger Integration & Capital Adequacy:
The amalgamation of erstwhile Housing Development Finance Corporation Limited (HDFC Limited) with HDFC Bank was smoothly operationalized on July 1, 2023.
Capital Adequacy Ratio (CAR) under Basel III stood at 18.8% (Tier 1 CAR at 16.8%) as on March 31, 2024, well above the regulatory requirement of 11.5%.

Branch Network Expansion:
The Bank added 912 branches during the year, taking the total physical branch network to 8,735 branches and 20,938 ATMs across 3,836 cities and towns in India. Over 52% of branches are situated in semi-urban and rural areas."""
            },
            {
                "page_number": 3,
                "section": "MANAGEMENT_DISCUSSION_AND_ANALYSIS",
                "text": """MANAGEMENT DISCUSSION AND ANALYSIS (MD&A)

Asset Quality & Credit Cost Management:
- Gross Non-Performing Assets (GNPA) stood at 1.24% of gross advances as on March 31, 2024.
- Net Non-Performing Assets (NNPA) stood at 0.33%.
- Provision Coverage Ratio (PCR) was healthy at 74.0%.
- Total floating provisions and contingent provisions maintained stood at ₹15,600 crore, providing strong balance sheet resilience against unexpected macro shocks.

Retail and Commercial Banking:
Retail loans comprised 54% of advances, Commercial and Rural Banking comprised 25%, and Corporate & Wholesale comprised 21%. Average Return on Assets (RoA) was 1.95% and Return on Equity (RoE) was 15.3%."""
            },
            {
                "page_number": 4,
                "section": "INDEPENDENT_AUDITORS_REPORT",
                "text": """INDEPENDENT AUDITOR'S REPORT
To the Members of HDFC Bank Limited

Report on the Standalone and Consolidated Financial Statements:
We have audited the financial statements of HDFC Bank Limited, which comprise the Balance Sheet as at March 31, 2024, the Profit and Loss Account, and the Cash Flow Statement for the year then ended.
In our opinion, the financial statements give a true and fair view in conformity with the Banking Regulation Act, 1949 and applicable Ind AS / RBI prudential guidelines.

Key Audit Matters:
1. Accounting for the Amalgamation of HDFC Limited: Verification of purchase price allocation, statutory reserve adjustments, and tax harmonization.
2. Expected Credit Loss (ECL) / Loan Loss Provisioning: Evaluation of staging criteria, default risk models, and collateral valuation.
3. Information Technology and Cybersecurity Controls over Core Banking Systems."""
            },
            {
                "page_number": 5,
                "section": "NOTES_TO_CONSOLIDATED_FINANCIAL_STATEMENTS",
                "text": """NOTES TO ACCOUNTS FORMING PART OF THE FINANCIAL STATEMENTS
FOR THE YEAR ENDED MARCH 31, 2024

Note 18: Related Party Disclosures
- Transactions with Key Management Personnel: Compensation paid to MD & CEO and Executive Directors totaled ₹16.8 crore.
- Deposits and borrowings with subsidiary entities (HDFC Life, HDFC AMC, HDFC ERGO) conducted in normal course of banking operations under RBI guidelines.

Note 24: Contingent Liabilities & Off-Balance Sheet Exposures
- Claims against the Bank not acknowledged as debts: ₹1,240 crore.
- Guarantees given on behalf of constituents: ₹1,12,400 crore.
- Acceptances, endorsements and other obligations: ₹54,800 crore.
- Outstanding forward exchange contracts and interest rate derivatives: ₹14,80,000 crore (notional value)."""
            }
        ]
    }
]
