"""Configuration module for Phone Agent."""

from phone_agent.config.apps import APP_PACKAGES
from phone_agent.config.i18n import get_message, get_messages
from phone_agent.config.prompts_en import SYSTEM_PROMPT as SYSTEM_PROMPT_EN
from phone_agent.config.prompts_zh import SYSTEM_PROMPT as SYSTEM_PROMPT_ZH
# New import for automotive prompt
from phone_agent.config.prompts_automotive import AUTOMOTIVE_SYSTEM_PROMPT as SYSTEM_PROMPT_AUTOMOTIVE_ZH


def get_system_prompt(lang: str = "cn") -> str:
    """
    Get system prompt by language.

    Args:
        lang: Language code, 'cn' for Chinese, 'en' for English, 'automotive_cn' for automotive Chinese.

    Returns:
        System prompt string.
    """
    if lang == "en":
        return SYSTEM_PROMPT_EN
    elif lang == "automotive_cn": # New condition
        return SYSTEM_PROMPT_AUTOMOTIVE_ZH
    return SYSTEM_PROMPT_ZH


# Default to Chinese for backward compatibility
SYSTEM_PROMPT = SYSTEM_PROMPT_ZH

__all__ = [
    "APP_PACKAGES",
    "SYSTEM_PROMPT",
    "SYSTEM_PROMPT_ZH",
    "SYSTEM_PROMPT_EN",
    "SYSTEM_PROMPT_AUTOMOTIVE_ZH", # Add to all
    "get_system_prompt",
    "get_messages",
    "get_message",
]
