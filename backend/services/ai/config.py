"""
Advanced AI Configuration for Narrative OS
Multi-model orchestration with cutting-edge 2026 techniques
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum
import os


class AIModel(str, Enum):
    """Available AI models with different capabilities"""
    # OpenAI GPT-4 family (2024-2026)
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT4_O = "gpt-4o"  # Omni model (multimodal)
    GPT4_O_MINI = "gpt-4o-mini"  # Fast, cheap

    # Anthropic Claude family (2024-2026)
    CLAUDE_OPUS = "claude-opus-4"  # Best quality
    CLAUDE_SONNET = "claude-sonnet-3.5"  # Balanced
    CLAUDE_HAIKU = "claude-haiku-3"  # Fast, cheap

    # Open source alternatives
    LLAMA_3_70B = "meta/llama-3-70b"
    MIXTRAL_8X7B = "mistralai/mixtral-8x7b"


class GenerationMode(str, Enum):
    """Generation strategies for different needs"""
    FAST = "fast"  # Quick drafts, lower quality
    BALANCED = "balanced"  # Good quality/speed ratio
    PREMIUM = "premium"  # Best quality, slower
    CREATIVE = "creative"  # High temperature, experimental
    PRECISE = "precise"  # Low temperature, factual


class AIConfig(BaseModel):
    """Configuration for AI generation"""

    # Model selection
    primary_model: AIModel = Field(
        default=AIModel.CLAUDE_SONNET,
        description="Main model for prose generation"
    )
    critique_model: AIModel = Field(
        default=AIModel.CLAUDE_HAIKU,
        description="Fast model for quality checks"
    )
    planning_model: AIModel = Field(
        default=AIModel.CLAUDE_OPUS,
        description="Best model for story planning"
    )

    # Generation parameters
    temperature: float = Field(
        default=0.8,
        ge=0.0,
        le=2.0,
        description="Creativity level (0=precise, 2=wild)"
    )
    max_tokens: int = Field(
        default=4096,
        ge=100,
        le=32000,
        description="Maximum output length"
    )
    top_p: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling threshold"
    )
    frequency_penalty: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Reduce repetition"
    )
    presence_penalty: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Encourage topic diversity"
    )

    # Advanced features
    use_rag: bool = Field(
        default=True,
        description="Use Retrieval Augmented Generation (canon context)"
    )
    use_chain_of_thought: bool = Field(
        default=True,
        description="Enable reasoning before generation"
    )
    use_self_critique: bool = Field(
        default=True,
        description="Enable iterative refinement"
    )
    max_refinement_iterations: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum refinement passes"
    )

    # Context management
    max_context_tokens: int = Field(
        default=16000,
        description="Maximum context window to use"
    )
    canon_context_weight: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="How much to prioritize canon consistency"
    )

    # API keys (from environment)
    openai_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    anthropic_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )

    class Config:
        use_enum_values = True


# Preset configurations for different use cases
GENERATION_PRESETS = {
    "fast_draft": AIConfig(
        primary_model=AIModel.GPT4_O_MINI,
        temperature=0.9,
        max_tokens=2048,
        use_self_critique=False,
        max_refinement_iterations=1
    ),
    "balanced": AIConfig(
        primary_model=AIModel.CLAUDE_SONNET,
        temperature=0.8,
        max_tokens=4096,
        use_self_critique=True,
        max_refinement_iterations=2
    ),
    "premium": AIConfig(
        primary_model=AIModel.CLAUDE_OPUS,
        critique_model=AIModel.CLAUDE_SONNET,
        temperature=0.7,
        max_tokens=8192,
        use_self_critique=True,
        max_refinement_iterations=3
    ),
    "creative_burst": AIConfig(
        primary_model=AIModel.GPT4_O,
        temperature=1.2,
        top_p=0.9,
        max_tokens=4096,
        frequency_penalty=0.5,
        presence_penalty=0.5
    ),
    "canon_strict": AIConfig(
        primary_model=AIModel.CLAUDE_OPUS,
        temperature=0.6,
        canon_context_weight=0.95,
        use_rag=True,
        use_chain_of_thought=True
    )
}


def get_preset(name: str) -> AIConfig:
    """Get a preset configuration by name"""
    return GENERATION_PRESETS.get(name, GENERATION_PRESETS["balanced"])


# Model capabilities matrix
MODEL_CAPABILITIES = {
    AIModel.CLAUDE_OPUS: {
        "context_window": 200000,
        "output_tokens": 4096,
        "cost_per_1k_input": 0.015,
        "cost_per_1k_output": 0.075,
        "best_for": ["complex reasoning", "long context", "quality"],
        "speed": "slow"
    },
    AIModel.CLAUDE_SONNET: {
        "context_window": 200000,
        "output_tokens": 4096,
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
        "best_for": ["balanced quality/speed", "general purpose"],
        "speed": "medium"
    },
    AIModel.CLAUDE_HAIKU: {
        "context_window": 200000,
        "output_tokens": 4096,
        "cost_per_1k_input": 0.00025,
        "cost_per_1k_output": 0.00125,
        "best_for": ["fast iterations", "cheap operations", "QC"],
        "speed": "fast"
    },
    AIModel.GPT4_O: {
        "context_window": 128000,
        "output_tokens": 4096,
        "cost_per_1k_input": 0.005,
        "cost_per_1k_output": 0.015,
        "best_for": ["multimodal", "creative", "balanced"],
        "speed": "medium"
    },
    AIModel.GPT4_O_MINI: {
        "context_window": 128000,
        "output_tokens": 16000,
        "cost_per_1k_input": 0.00015,
        "cost_per_1k_output": 0.0006,
        "best_for": ["cheap", "fast", "high volume"],
        "speed": "very_fast"
    }
}


def get_ai_config(preset: str = "balanced") -> AIConfig:
    """
    Get AI configuration (default or preset)

    Args:
        preset: Name of preset configuration (default: "balanced")

    Returns:
        AIConfig instance
    """
    return get_preset(preset)


def select_best_model(
    task_type: Literal["generation", "critique", "planning", "expansion"],
    quality_preference: Literal["fast", "balanced", "premium"],
    context_size: int
) -> AIModel:
    """
    Intelligently select the best model for a task

    Args:
        task_type: Type of task to perform
        quality_preference: Speed vs quality tradeoff
        context_size: Number of tokens in context

    Returns:
        Best model for the task
    """
    if quality_preference == "fast":
        if task_type == "critique":
            return AIModel.CLAUDE_HAIKU
        else:
            return AIModel.GPT4_O_MINI

    elif quality_preference == "premium":
        if task_type == "planning":
            return AIModel.CLAUDE_OPUS
        elif task_type == "generation":
            return AIModel.CLAUDE_OPUS if context_size > 50000 else AIModel.GPT4_O
        elif task_type == "critique":
            return AIModel.CLAUDE_SONNET
        else:
            return AIModel.CLAUDE_OPUS

    else:  # balanced
        if task_type == "critique":
            return AIModel.CLAUDE_HAIKU
        elif task_type == "planning":
            return AIModel.CLAUDE_SONNET
        else:
            return AIModel.CLAUDE_SONNET
