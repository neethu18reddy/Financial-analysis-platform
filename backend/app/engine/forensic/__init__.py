"""Forensic Accounting & Anomaly Detection Engines."""

try:
    from app.engine.forensic.altman import AltmanZScoreEngine
    from app.engine.forensic.beneish import BeneishMScoreEngine
    from app.engine.forensic.forensic_service import ForensicAnalysisService
    from app.engine.forensic.piotroski import PiotroskiFScoreEngine
    from app.engine.forensic.signals import ForensicSignalsEngine
except ImportError:
    from backend.app.engine.forensic.altman import AltmanZScoreEngine
    from backend.app.engine.forensic.beneish import BeneishMScoreEngine
    from backend.app.engine.forensic.forensic_service import ForensicAnalysisService
    from backend.app.engine.forensic.piotroski import PiotroskiFScoreEngine
    from backend.app.engine.forensic.signals import ForensicSignalsEngine

__all__ = [
    "AltmanZScoreEngine",
    "BeneishMScoreEngine",
    "PiotroskiFScoreEngine",
    "ForensicSignalsEngine",
    "ForensicAnalysisService",
]
