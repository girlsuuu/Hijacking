import os
from enum import Enum


class Model(Enum):
    gemini_2_5_pro = "gemini-2.5-pro"
    gpt_o4_mini = "gpt-o4-mini"
    gpt_5_mini = "gpt-5-mini"
    grok_3_mini = "grok-3-mini"
    claude_4_sonnet = "claude-4-sonnet"


# List of all model names
MODEL_NAMES = [model.value for model in Model]


# API key environment variable names for each model
API_KEY_NAMES: dict[Model | str, str] = {
    Model.gemini_2_5_pro: "GEMINI_API_KEY",
    Model.gpt_o4_mini: "OPENAI_API_KEY",
    Model.gpt_5_mini: "OPENAI_API_KEY",
    Model.grok_3_mini: "GROK_API_KEY",
    Model.claude_4_sonnet: "ANTHROPIC_API_KEY",
}


# LiteLLM model name mappings
# Maps our internal model names to LiteLLM-compatible model strings
LITELLM_MODEL_MAPPING = {
    "gpt-o4-mini": "o4-mini",
    "gpt-5-mini": "gpt-5-mini",
    "claude-4-sonnet": "anthropic/claude-sonnet-4-20250514",
    "grok-3-mini": "xai/grok-3-mini",
    "gemini-2.5-pro": "gemini/gemini-2.5-pro"
}


def get_api_key(model: Model) -> str:
    environ_var = API_KEY_NAMES[model]
    try:
        return os.environ[environ_var]
    except KeyError:
        raise ValueError(
            f"Missing API key for {model.value}. "
            f"Please set it by running: export {environ_var}='your-api-key-here'"
        )


def get_litellm_model_name(model_name: str) -> str:
    # Use our defined exact mapping
    if model_name in LITELLM_MODEL_MAPPING:
        return LITELLM_MODEL_MAPPING[model_name]

    # Fallback to model name itself
    return model_name
