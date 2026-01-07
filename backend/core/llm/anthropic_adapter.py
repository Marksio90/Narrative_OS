"""
Anthropic (Claude) LLM Adapter
"""
import httpx
from typing import List, AsyncIterator
from .base import (
    BaseLLMAdapter,
    LLMMessage,
    LLMResponse,
    LLMConfig,
    LLMProvider,
    LLMError,
    LLMRateLimitError,
    LLMInvalidRequestError,
    LLMAuthenticationError,
    LLMTimeoutError,
)


class AnthropicAdapter(BaseLLMAdapter):
    """
    Adapter for Anthropic API (Claude models)
    """

    BASE_URL = "https://api.anthropic.com/v1"
    API_VERSION = "2023-06-01"

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url", self.BASE_URL)
        self.timeout = kwargs.get("timeout", 60.0)

    def validate_config(self, config: LLMConfig) -> bool:
        """Validate Anthropic configuration"""
        valid_models = [
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
            "claude-2.1",
            "claude-2.0",
            "claude-instant",
        ]

        if not any(config.model.startswith(m) for m in valid_models):
            raise ValueError(f"Invalid Anthropic model: {config.model}")

        if config.temperature < 0 or config.temperature > 1:
            raise ValueError("Temperature must be between 0 and 1 for Anthropic")

        return True

    async def complete(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ) -> LLMResponse:
        """Generate completion using Anthropic API"""
        self.validate_config(config)

        # Separate system message from conversation
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })

        # Build request payload
        payload = {
            "model": config.model,
            "messages": conversation_messages,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "max_tokens": config.max_tokens or 4096,
        }

        if system_message:
            payload["system"] = system_message

        if config.stop:
            payload["stop_sequences"] = config.stop

        if config.extra:
            payload.update(config.extra)

        # Make API request
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": self.API_VERSION,
                        "content-type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            except httpx.TimeoutException:
                raise LLMTimeoutError("Anthropic API request timed out")
            except httpx.HTTPStatusError as e:
                self._handle_http_error(e)

        # Parse response
        content = data["content"][0]["text"]
        usage = data.get("usage", {})

        return LLMResponse(
            content=content,
            model=data["model"],
            provider=LLMProvider.ANTHROPIC,
            usage={
                "prompt_tokens": usage.get("input_tokens", 0),
                "completion_tokens": usage.get("output_tokens", 0),
                "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            },
            finish_reason=data.get("stop_reason", "end_turn"),
            raw_response=data,
        )

    async def stream_complete(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ) -> AsyncIterator[str]:
        """Stream completion from Anthropic"""
        self.validate_config(config)

        # Separate system message
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })

        payload = {
            "model": config.model,
            "messages": conversation_messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens or 4096,
            "stream": True,
        }

        if system_message:
            payload["system"] = system_message

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": self.API_VERSION,
                        "content-type": "application/json",
                    },
                    json=payload,
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunk = line[6:]  # Remove "data: " prefix

                            try:
                                import json
                                data = json.loads(chunk)

                                if data["type"] == "content_block_delta":
                                    delta = data["delta"]
                                    if delta["type"] == "text_delta":
                                        yield delta["text"]

                            except (json.JSONDecodeError, KeyError):
                                continue

            except httpx.TimeoutException:
                raise LLMTimeoutError("Anthropic streaming request timed out")
            except httpx.HTTPStatusError as e:
                self._handle_http_error(e)

    def _handle_http_error(self, error: httpx.HTTPStatusError):
        """Convert HTTP errors to appropriate LLM exceptions"""
        status_code = error.response.status_code

        if status_code == 401:
            raise LLMAuthenticationError("Invalid Anthropic API key")
        elif status_code == 429:
            raise LLMRateLimitError("Anthropic rate limit exceeded")
        elif status_code == 400:
            raise LLMInvalidRequestError(f"Invalid request: {error.response.text}")
        else:
            raise LLMError(f"Anthropic API error: {error.response.text}")
