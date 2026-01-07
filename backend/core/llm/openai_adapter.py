"""
OpenAI LLM Adapter
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


class OpenAIAdapter(BaseLLMAdapter):
    """
    Adapter for OpenAI API (GPT-4, GPT-3.5, etc.)
    """

    BASE_URL = "https://api.openai.com/v1"

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url", self.BASE_URL)
        self.timeout = kwargs.get("timeout", 60.0)

    def validate_config(self, config: LLMConfig) -> bool:
        """Validate OpenAI configuration"""
        valid_models = [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
        ]

        if not any(config.model.startswith(m) for m in valid_models):
            raise ValueError(f"Invalid OpenAI model: {config.model}")

        if config.temperature < 0 or config.temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")

        return True

    async def complete(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ) -> LLMResponse:
        """Generate completion using OpenAI API"""
        self.validate_config(config)

        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Build request payload
        payload = {
            "model": config.model,
            "messages": openai_messages,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "frequency_penalty": config.frequency_penalty,
            "presence_penalty": config.presence_penalty,
        }

        if config.max_tokens:
            payload["max_tokens"] = config.max_tokens

        if config.stop:
            payload["stop"] = config.stop

        if config.extra:
            payload.update(config.extra)

        # Make API request
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            except httpx.TimeoutException:
                raise LLMTimeoutError("OpenAI API request timed out")
            except httpx.HTTPStatusError as e:
                self._handle_http_error(e)

        # Parse response
        choice = data["choices"][0]
        usage = data.get("usage", {})

        return LLMResponse(
            content=choice["message"]["content"],
            model=data["model"],
            provider=LLMProvider.OPENAI,
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
            finish_reason=choice.get("finish_reason", "stop"),
            raw_response=data,
        )

    async def stream_complete(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ) -> AsyncIterator[str]:
        """Stream completion from OpenAI"""
        self.validate_config(config)

        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        payload = {
            "model": config.model,
            "messages": openai_messages,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "stream": True,
        }

        if config.max_tokens:
            payload["max_tokens"] = config.max_tokens

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunk = line[6:]  # Remove "data: " prefix
                            if chunk == "[DONE]":
                                break

                            try:
                                import json
                                data = json.loads(chunk)
                                delta = data["choices"][0]["delta"]
                                if "content" in delta:
                                    yield delta["content"]
                            except (json.JSONDecodeError, KeyError):
                                continue

            except httpx.TimeoutException:
                raise LLMTimeoutError("OpenAI streaming request timed out")
            except httpx.HTTPStatusError as e:
                self._handle_http_error(e)

    def _handle_http_error(self, error: httpx.HTTPStatusError):
        """Convert HTTP errors to appropriate LLM exceptions"""
        status_code = error.response.status_code

        if status_code == 401:
            raise LLMAuthenticationError("Invalid OpenAI API key")
        elif status_code == 429:
            raise LLMRateLimitError("OpenAI rate limit exceeded")
        elif status_code == 400:
            raise LLMInvalidRequestError(f"Invalid request: {error.response.text}")
        else:
            raise LLMError(f"OpenAI API error: {error.response.text}")
