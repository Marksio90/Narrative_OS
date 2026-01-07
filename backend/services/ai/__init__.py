"""
Advanced AI Services for Narrative OS
Multi-agent prose generation with RAG and iterative refinement
"""
from .config import AIConfig, AIModel, GenerationMode, GENERATION_PRESETS, get_preset
from .orchestrator import AIOrchestrator, GenerationResult, Agent
from .rag_engine import RAGEngine, CanonFact
from .draft_service import DraftService

__all__ = [
    'AIConfig',
    'AIModel',
    'GenerationMode',
    'GENERATION_PRESETS',
    'get_preset',
    'AIOrchestrator',
    'GenerationResult',
    'Agent',
    'RAGEngine',
    'CanonFact',
    'DraftService',
]
