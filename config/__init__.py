"""
Configuration package for Hijacking project.
Centralizes all configuration management including models, parameters, and prompts.
"""

from .models import (
    Model,
    MODEL_NAMES,
    API_KEY_NAMES,
    LITELLM_MODEL_MAPPING,
    get_litellm_model_name,
    get_api_key
)

from .parameters import (
    ATTACK_TEMP,
    TARGET_TEMP,
    ATTACK_TOP_P,
    TARGET_TOP_P,
    MODEL_TOKEN_LIMITS,
    GEMINI_SAFETY_SETTINGS_ATTACK,
    GEMINI_SAFETY_SETTINGS_TARGET,
    GEMINI_SAFETY_SETTINGS_JUDGE,
    API_MAX_RETRY
)

from .judge_prompt import (
    GEMINI_JUDGE_PROMPT_TEMPLATE
)

__all__ = [
    # Models
    'Model',
    'MODEL_NAMES',
    'API_KEY_NAMES',
    'LITELLM_MODEL_MAPPING',
    'get_litellm_model_name',
    'get_api_key',

    # Parameters
    'ATTACK_TEMP',
    'TARGET_TEMP',
    'ATTACK_TOP_P',
    'TARGET_TOP_P',
    'MODEL_TOKEN_LIMITS',
    'GEMINI_SAFETY_SETTINGS_ATTACK',
    'GEMINI_SAFETY_SETTINGS_TARGET',
    'GEMINI_SAFETY_SETTINGS_JUDGE',
    'API_MAX_RETRY',

    # Prompts
    'GEMINI_JUDGE_PROMPT_TEMPLATE',
]
