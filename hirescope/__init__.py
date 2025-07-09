"""
HireScope - AI-powered candidate analysis for Greenhouse ATS

Copyright (c) 2025 GSD at Work LLC
https://gsdat.work

Licensed under MIT License
"""

__version__ = "1.0.0"
__author__ = "GSD at Work LLC"
__email__ = "christian@gsdat.work"

# Import all modules when package is imported
from .ai_scorer import AIScorer
from .analyzer import CandidateAnalyzer
from .document_processor import DocumentProcessor
from .greenhouse_api import GreenhouseClient
from .report_generator import ReportGenerator

__all__ = [
    "CandidateAnalyzer",
    "GreenhouseClient",
    "DocumentProcessor",
    "AIScorer",
    "ReportGenerator",
]
