"""Unit tests for FinancialNormalizer and scale unit transformations."""

import pytest
from app.models.financial_period import FinancialUnit
from app.engine.normalizer import FinancialNormalizer, NormalizerError


def test_normalize_to_crores_from_all_units():
    """Verify precision and scale factors across all Indian and standard accounting units."""
    # 100 Crores -> 100 Crores
    assert FinancialNormalizer.normalize_to_crores(100.0, FinancialUnit.CRORES) == 100.0
    
    # 10,000 Lakhs -> 100 Crores (1 Lakh = 0.01 Crore)
    assert FinancialNormalizer.normalize_to_crores(10000.0, FinancialUnit.LAKHS) == 100.0

    # 1,000 Millions -> 100 Crores (1 Million = 0.1 Crore)
    assert FinancialNormalizer.normalize_to_crores(1000.0, FinancialUnit.MILLIONS) == 100.0

    # 1 Billion -> 100 Crores
    assert FinancialNormalizer.normalize_to_crores(1.0, FinancialUnit.BILLIONS) == 100.0

    # 1,000,000,000 Units (Exact INR) -> 100 Crores (1 Crore = 10,000,000 INR)
    assert FinancialNormalizer.normalize_to_crores(1000000000.0, FinancialUnit.UNITS) == 100.0


def test_convert_from_crores():
    """Verify back-conversion from canonical Crores to target display scale."""
    assert FinancialNormalizer.convert_from_crores(100.0, FinancialUnit.CRORES) == 100.0
    assert FinancialNormalizer.convert_from_crores(100.0, FinancialUnit.LAKHS) == 10000.0
    assert FinancialNormalizer.convert_from_crores(100.0, FinancialUnit.MILLIONS) == 1000.0
    assert FinancialNormalizer.convert_from_crores(100.0, FinancialUnit.BILLIONS) == 1.0
    assert FinancialNormalizer.convert_from_crores(100.0, FinancialUnit.UNITS) == 1000000000.0


def test_parse_raw_strings():
    """Verify parsing of formatted financial strings with commas, symbols, and parentheses."""
    assert FinancialNormalizer.parse_raw_string("89,922.50") == 89922.50
    assert FinancialNormalizer.parse_raw_string("₹ 1,234.56") == 1234.56
    assert FinancialNormalizer.parse_raw_string("Rs. 500") == 500.0
    assert FinancialNormalizer.parse_raw_string("(1,450.25)") == -1450.25
    assert FinancialNormalizer.parse_raw_string("-") == 0.0
    assert FinancialNormalizer.parse_raw_string("N/A") == 0.0
    assert FinancialNormalizer.parse_raw_string(None) == 0.0
    assert FinancialNormalizer.parse_raw_string(12345) == 12345.0
