"""
Model API abstraction layer.
Provides base interface and LiteLLM implementation for language model interactions.
"""

from .base import BaseLLM
from .litellm_api import APILiteLLM

__all__ = [
    'BaseLLM',
    'APILiteLLM',
]
