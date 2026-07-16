"""Model-provider interfaces and built-in adapters."""

from cyberdeck.providers.base import ModelProvider, ModelResponse, ProviderError
from cyberdeck.providers.ollama import OllamaProvider

__all__ = ["ModelProvider", "ModelResponse", "OllamaProvider", "ProviderError"]
