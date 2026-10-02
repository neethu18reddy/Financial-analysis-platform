"""Deterministic normalizer for financial units, currencies, and statement items."""

from typing import Union
from app.models.financial_period import FinancialUnit


class NormalizerError(Exception):
    """Raised when financial normalization cannot be deterministically resolved."""
    pass


# Conversion multipliers to convert from source unit into canonical CRORES (1 Crore = 10,000,000 INR)
UNIT_TO_CRORE_MULTIPLIERS = {
    FinancialUnit.CRORES: 1.0,
    FinancialUnit.LAKHS: 0.01,           # 1 Lakh = 0.01 Crore
    FinancialUnit.MILLIONS: 0.1,         # 1 Million = 0.10 Crore (10 Lakhs)
    FinancialUnit.BILLIONS: 100.0,       # 1 Billion = 100 Crores
    FinancialUnit.UNITS: 0.0000001,      # 1 Unit = 1e-7 Crore
}

# Multipliers to convert from CRORES into other target presentation units
CRORE_TO_TARGET_MULTIPLIERS = {
    FinancialUnit.CRORES: 1.0,
    FinancialUnit.LAKHS: 100.0,
    FinancialUnit.MILLIONS: 10.0,
    FinancialUnit.BILLIONS: 0.01,
    FinancialUnit.UNITS: 10000000.0,
}


class FinancialNormalizer:
    """Deterministic normalizer converting financial values into canonical scale."""

    @staticmethod
    def normalize_to_crores(value: Union[float, int], from_unit: Union[FinancialUnit, str]) -> float:
        """Convert any financial value into canonical INR Crores with precision preservation."""
        if value is None:
            return 0.0
        
        unit_enum = FinancialUnit(from_unit) if isinstance(from_unit, str) else from_unit
        multiplier = UNIT_TO_CRORE_MULTIPLIERS.get(unit_enum)
        if multiplier is None:
            raise NormalizerError(f"Unsupported financial unit: {from_unit}")
        
        return round(float(value) * multiplier, 4)

    @staticmethod
    def convert_from_crores(value_in_crores: float, to_unit: Union[FinancialUnit, str]) -> float:
        """Convert a canonical INR Crores value into a target display unit."""
        if value_in_crores is None:
            return 0.0
        
        unit_enum = FinancialUnit(to_unit) if isinstance(to_unit, str) else to_unit
        multiplier = CRORE_TO_TARGET_MULTIPLIERS.get(unit_enum)
        if multiplier is None:
            raise NormalizerError(f"Unsupported target unit: {to_unit}")
        
        return round(float(value_in_crores) * multiplier, 4)

    @staticmethod
    def parse_raw_string(raw_val: Union[str, float, int]) -> float:
        """Sanitize raw string values from filings into deterministic floats."""
        if raw_val is None:
            return 0.0
        if isinstance(raw_val, (int, float)):
            return float(raw_val)
        
        cleaned = str(raw_val).strip().replace(",", "").replace("₹", "").replace("Rs.", "").replace(" ", "")
        if not cleaned or cleaned in ("-", "--", "N/A", "NA", "nil", "Nil"):
            return 0.0
        
        # Check for parentheses indicating negative values: (123.45) -> -123.45
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = f"-{cleaned[1:-1]}"
        
        try:
            return float(cleaned)
        except ValueError as exc:
            raise NormalizerError(f"Failed to parse numeric value from raw string: '{raw_val}'") from exc
