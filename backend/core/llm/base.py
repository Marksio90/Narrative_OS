"""
LLM Gateway Base Classes

Provider-agnostic abstraction for LLM calls
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


@dataclass
class LLMMessage:
    """
    Standard message format for all providers
    """
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None  # For function calls


@dataclass
class LLMResponse:
    """
    Standardized response from any LLM provider
    """
    content: str
    model: str
    provider: LLMProvider
    usage: Dict[str, int]  # tokens used
    finish_reason: str
    raw_response: Optional[Any] = None  # Original provider response


@dataclass
class LLMConfig:
    """
    Configuration for LLM generation
    """
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None

    # Provider-specific overrides
    extra: Optional[Dict[str, Any]] = None


class BaseLLMAdapter(ABC):
    """
    Abstract base class for LLM adapters

    Each provider (OpenAI, Anthropic, custom) implements this interface
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.extra_config = kwargs

    @abstractmethod
    async def complete(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ) -> LLMResponse:
        """
        Generate completion from messages

        Args:
            messages: List of conversation messages
            config: Generation configuration

        Returns:
            LLMResponse with generated content
        """
        pass

    @abstractmethod
    async def stream_complete(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ):
        """
        Stream completion tokens as they're generated

        Args:
            messages: List of conversation messages
            config: Generation configuration

        Yields:
            Chunks of generated text
        """
        pass

    @abstractmethod
    def validate_config(self, config: LLMConfig) -> bool:
        """
        Validate that config is compatible with this provider

        Args:
            config: Configuration to validate

        Returns:
            True if valid

        Raises:
            ValueError: If configuration is invalid
        """
        pass


class LLMError(Exception):
    """Base exception for LLM-related errors"""
    pass


class LLMRateLimitError(LLMError):
    """Rate limit exceeded"""
    pass


class LLMInvalidRequestError(LLMError):
    """Invalid request parameters"""
    pass


class LLMAuthenticationError(LLMError):
    """Authentication failed"""
    pass


class LLMTimeoutError(LLMError):
    """Request timed out"""
    pass
