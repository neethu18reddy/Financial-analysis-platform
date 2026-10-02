"""Source registry tracking provider credentials, terms, licenses, and rate limits."""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.models.source import SourceType, DataClassification


class SourceProviderMetadata(BaseModel):
    """Compliance and operational metadata for external data providers."""
    provider_id: str
    provider_name: str
    source_type: SourceType
    access_method: str
    terms_and_license: str
    storage_restrictions: str
    redistribution_restrictions: str
    attribution_requirements: str
    rate_limits: str
    primary_url: str
    supported_classifications: List[DataClassification]


# Comprehensive registry of legitimate Indian data sources and fixture providers
SOURCE_REGISTRY: Dict[str, SourceProviderMetadata] = {
    "NSE_INDIA": SourceProviderMetadata(
        provider_id="NSE_INDIA",
        provider_name="National Stock Exchange of India (NSE)",
        source_type=SourceType.NSE_FILING,
        access_method="Direct statutory filings under SEBI LODR Regulations / Exchange Disclosures",
        terms_and_license="Public statutory regulatory disclosures under SEBI LODR 2015. Non-commercial and research use allowed.",
        storage_restrictions="Local caching allowed for historical audit trail and academic/analytical research.",
        redistribution_restrictions="Raw dissemination prohibited without explicit exchange licensing; derived analytics permitted.",
        attribution_requirements="Source: National Stock Exchange of India (NSE)",
        rate_limits="Standard web access rate-limits; respectful queuing (<= 2 req/sec).",
        primary_url="https://www.nseindia.com",
        supported_classifications=[DataClassification.REAL]
    ),
    "BSE_INDIA": SourceProviderMetadata(
        provider_id="BSE_INDIA",
        provider_name="Bombay Stock Exchange (BSE)",
        source_type=SourceType.BSE_FILING,
        access_method="Corporate Filings & XBRL Portal",
        terms_and_license="Public regulatory repository under SEBI disclosures. Statutory filing access.",
        storage_restrictions="Audit log preservation compliant with regulatory archival norms.",
        redistribution_restrictions="Proprietary redistribution restricted. Analytical processing permitted.",
        attribution_requirements="Source: BSE India Corporate Filings",
        rate_limits="<= 2 req/sec with exponential backoff.",
        primary_url="https://www.bseindia.com",
        supported_classifications=[DataClassification.REAL]
    ),
    "MCA_XBRL": SourceProviderMetadata(
        provider_id="MCA_XBRL",
        provider_name="Ministry of Corporate Affairs (MCA)",
        source_type=SourceType.MCA_XBRL,
        access_method="MCA21 Portal / XBRL Ind AS Taxonomy Filings",
        terms_and_license="Government Open Data / Statutory Corporate Repository.",
        storage_restrictions="Permanent storage allowed for enterprise compliance and historical records.",
        redistribution_restrictions="Public record disclosures permitted for analytical dissemination.",
        attribution_requirements="Source: Ministry of Corporate Affairs, Government of India",
        rate_limits="Batch retrieval only during permitted off-peak hours.",
        primary_url="https://www.mca.gov.in",
        supported_classifications=[DataClassification.REAL]
    ),
    "RBI_DBIE": SourceProviderMetadata(
        provider_id="RBI_DBIE",
        provider_name="Reserve Bank of India - Data Warehouse (DBIE)",
        source_type=SourceType.RBI_DBIE,
        access_method="Open Data API / Macro & Sectoral Banking Statistics",
        terms_and_license="RBI Open Data Policy (Open Access).",
        storage_restrictions="Full historical retention allowed.",
        redistribution_restrictions="Permitted with mandatory attribution to Reserve Bank of India.",
        attribution_requirements="Source: Reserve Bank of India (DBIE Portal)",
        rate_limits="50 req/min.",
        primary_url="https://dbie.rbi.org.in",
        supported_classifications=[DataClassification.REAL, DataClassification.DERIVED]
    ),
    "AUDITED_ANNUAL_REPORTS": SourceProviderMetadata(
        provider_id="AUDITED_ANNUAL_REPORTS",
        provider_name="Company Audited Annual Reports & Shareholder Disclosures",
        source_type=SourceType.ANNUAL_REPORT_PDF,
        access_method="Official Investor Relations Annual Reports (PDF) under Companies Act 2013",
        terms_and_license="Statutory audited shareholder disclosures. Publicly published reports.",
        storage_restrictions="Unrestricted local archiving for audit verification and lineage.",
        redistribution_restrictions="Quotes and extracts permitted with source report reference.",
        attribution_requirements="Source: Audited Annual Report of the respective company",
        rate_limits="N/A (Local / CDN ingestion).",
        primary_url="https://www.nseindia.com/companies-listing/corporate-filings-annual-reports",
        supported_classifications=[DataClassification.REAL]
    ),
    "FIXTURE_ENGINE": SourceProviderMetadata(
        provider_id="FIXTURE_ENGINE",
        provider_name="Antigravity Deterministic Golden Fixture Registry",
        source_type=SourceType.AUDITED_FINANCIALS_FIXTURE,
        access_method="Pre-validated golden JSON fixtures derived directly from audited financial statements",
        terms_and_license="Internal testing and golden dataset verification under MIT License.",
        storage_restrictions="Committed to repository under deterministic test harness.",
        redistribution_restrictions="Open source repository fixture.",
        attribution_requirements="Antigravity Test Fixture Registry",
        rate_limits="Unrestricted (Local file system).",
        primary_url="file://backend/app/fixtures",
        supported_classifications=[DataClassification.REAL, DataClassification.SYNTHETIC, DataClassification.MOCK, DataClassification.DERIVED]
    )
}


def get_source_metadata(provider_id: str) -> SourceProviderMetadata:
    """Retrieve metadata for a given provider or return default fixture metadata."""
    return SOURCE_REGISTRY.get(provider_id, SOURCE_REGISTRY["FIXTURE_ENGINE"])
