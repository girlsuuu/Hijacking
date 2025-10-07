from google.generativeai.types import HarmCategory, HarmBlockThreshold


# Temperature and Top-P settings
ATTACK_TEMP = 1
TARGET_TEMP = 1
ATTACK_TOP_P = 0.9
TARGET_TOP_P = 0.95


# Maximum token limits per model
MODEL_TOKEN_LIMITS = {
    "gpt-o4-mini": 50000,
    "gpt-5-mini": 50000,
    "gemini-2.5-pro": 64000,
    "claude-4-sonnet": 40000,
    "grok-3-mini": 38000,
}


# API retry configuration
API_MAX_RETRY = 1


# Gemini Safety Settings - Attack Model (no blocking)
GEMINI_SAFETY_SETTINGS_ATTACK = [
    {
        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": HarmBlockThreshold.BLOCK_NONE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        "threshold": HarmBlockThreshold.BLOCK_NONE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        "threshold": HarmBlockThreshold.BLOCK_NONE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        "threshold": HarmBlockThreshold.BLOCK_NONE
    },
]


# Gemini Safety Settings - Target Model (medium blocking)
GEMINI_SAFETY_SETTINGS_TARGET = [
    {
        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    },
]


# Gemini Safety Settings - Judge Model (no blocking)
GEMINI_SAFETY_SETTINGS_JUDGE = [
    {
        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": HarmBlockThreshold.BLOCK_NONE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        "threshold": HarmBlockThreshold.BLOCK_NONE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        "threshold": HarmBlockThreshold.BLOCK_NONE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        "threshold": HarmBlockThreshold.BLOCK_NONE
    },
]
