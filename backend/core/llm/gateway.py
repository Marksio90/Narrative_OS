"""
LLM Gateway

Factory and manager for LLM adapters
"""
import os
from typing import Optional, Dict
from .base import BaseLLMAdapter, LLMProvider, LLMError
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter


class LLMGateway:
    """
    Central gateway for LLM operations

    Manages adapter instances and provides a unified interface
    """

    _adapters: Dict[LLMProvider, BaseLLMAdapter] = {}

    @classmethod
    def get_adapter(
        cls,
        provider: Optional[LLMProvider] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> BaseLLMAdapter:
        """
        Get or create an adapter for the specified provider

        Args:
            provider: LLM provider (defaults to env LLM_PROVIDER)
            api_key: API key (defaults to provider-specific env var)
            **kwargs: Additional provider-specific configuration

        Returns:
            Configured LLM adapter

        Raises:
            LLMError: If provider is not configured or invalid
        """
        # Determine provider
        if provider is None:
            provider_str = os.getenv("LLM_PROVIDER", "openai")
            try:
                provider = LLMProvider(provider_str)
            except ValueError:
                raise LLMError(f"Invalid LLM provider: {provider_str}")

        # Check cache
        if provider in cls._adapters:
            return cls._adapters[provider]

        # Create new adapter
        if provider == LLMProvider.OPENAI:
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise LLMError("OPENAI_API_KEY not set")
            adapter = OpenAIAdapter(api_key=api_key, **kwargs)

        elif provider == LLMProvider.ANTHROPIC:
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise LLMError("ANTHROPIC_API_KEY not set")
            adapter = AnthropicAdapter(api_key=api_key, **kwargs)

        elif provider == LLMProvider.CUSTOM:
            # Custom adapter would be implemented here
            # For now, raise not implemented
            raise LLMError("Custom LLM provider not yet implemented")

        else:
            raise LLMError(f"Unsupported provider: {provider}")

        # Cache and return
        cls._adapters[provider] = adapter
        return adapter

    @classmethod
    def clear_cache(cls):
        """Clear adapter cache (useful for testing)"""
        cls._adapters.clear()


# Convenience function
def get_llm(
    provider: Optional[LLMProvider] = None,
    **kwargs
) -> BaseLLMAdapter:
    """
    Convenience function to get an LLM adapter

    Args:
        provider: LLM provider
        **kwargs: Additional configuration

    Returns:
        Configured LLM adapter
    """
    return LLMGateway.get_adapter(provider=provider, **kwargs)
