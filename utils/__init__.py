"""
Utility modules for Hijacking project.
Provides conversation management, parsing, and logging utilities.
"""

# Conversation utilities
from .conversation import (
    conv_template,
    get_init_msg,
    set_system_prompts,
    initialize_conversations
)

# Parsing utilities
from .parsing import (
    extract_json,
    count_step,
    process_target_response
)

# Logging utilities
from .logger import (
    logger,
    configure_logging,
    WandBLogger
)

__all__ = [
    # Conversation
    'conv_template',
    'get_init_msg',
    'set_system_prompts',
    'initialize_conversations',

    # Parsing
    'extract_json',
    'count_step',
    'process_target_response',

    # Logging
    'logger',
    'configure_logging',
    'WandBLogger',
]
