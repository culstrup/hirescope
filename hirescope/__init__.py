"""
HireScope - AI-powered candidate analysis for Greenhouse ATS

Copyright (c) 2025 GSD at Work LLC
https://gsdat.work

Licensed under MIT License
"""

__version__ = "1.0.0"
__author__ = "GSD at Work LLC"
__email__ = "contact@gsdat.work"

# Import all modules when package is imported
from .analyzer import CandidateAnalyzer
from .greenhouse_api import GreenhouseClient
from .document_processor import DocumentProcessor
from .ai_scorer import AIScorer
from .report_generator import ReportGenerator

__all__ = [
    "CandidateAnalyzer",
    "GreenhouseClient", 
    "DocumentProcessor",
    "AIScorer",
    "ReportGenerator"
]