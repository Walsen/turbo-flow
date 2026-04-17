"""
Model provider factory + automatic tier selection.

Replaces Ruflo's 3-tier model routing with a programmatic equivalent.
Selects opus/sonnet/haiku based on task complexity heuristics.
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Any

from turboflow_adapter.logger import get_logger

log = get_logger("tf-adapter.strands.models")


class ModelTier(str, Enum):
    OPUS = "opus"
    SONNET = "sonnet"
    HAIKU = "haiku"


# ── Bedrock model IDs ────────────────────────────────────────────────────

_BEDROCK_DEFAULTS = {
    ModelTier.OPUS: "us.anthropic.claude-opus-4-6-v1",
    ModelTier.SONNET: "us.anthropic.claude-sonnet-4-6",
    ModelTier.HAIKU: "us.anthropic.claude-haiku-4-5-20251001-v1:0",
}

_ANTHROPIC_DEFAULTS = {
    ModelTier.OPUS: "claude-opus-4-20250514",
    ModelTier.SONNET: "claude-sonnet-4-20250514",
    ModelTier.HAIKU: "claude-haiku-4-5-20251001",
}

_ENV_OVERRIDES = {
    ModelTier.OPUS: "ANTHROPIC_DEFAULT_OPUS_MODEL",
    ModelTier.SONNET: "ANTHROPIC_DEFAULT_SONNET_MODEL",
    ModelTier.HAIKU: "ANTHROPIC_DEFAULT_HAIKU_MODEL",
}


def resolve_model_id(tier: ModelTier) -> str:
    """Resolve a tier to a concrete model ID, respecting env overrides."""
    env_key = _ENV_OVERRIDES[tier]
    if override := os.environ.get(env_key):
        return override

    if os.environ.get("CLAUDE_CODE_USE_BEDROCK") == "1":
        return _BEDROCK_DEFAULTS[tier]
    return _ANTHROPIC_DEFAULTS[tier]


def create_model(tier: ModelTier | str = ModelTier.SONNET) -> Any:
    """Create a Strands model provider for the given tier."""
    if isinstance(tier, str):
        tier = ModelTier(tier)

    model_id = resolve_model_id(tier)
    is_bedrock = os.environ.get("CLAUDE_CODE_USE_BEDROCK") == "1"

    if is_bedrock:
        import boto3
        from strands.models.bedrock import BedrockModel

        region = os.environ.get("AWS_REGION", "us-east-1")
        profile = os.environ.get("AWS_PROFILE")
        session = boto3.Session(profile_name=profile, region_name=region)
        log.debug("Creating Bedrock model: %s (region: %s, profile: %s)", model_id, region, profile)
        return BedrockModel(model_id=model_id, boto_session=session)

    if os.environ.get("ANTHROPIC_API_KEY"):
        from strands.models.anthropic import AnthropicModel

        log.debug("Creating Anthropic model: %s", model_id)
        return AnthropicModel(model_id=model_id, max_tokens=4096)

    if os.environ.get("OPENAI_API_KEY"):
        from strands.models.openai import OpenAIModel

        log.debug("Creating OpenAI model: %s", model_id)
        return OpenAIModel(model_id=model_id)

    # Default to Bedrock
    import boto3
    from strands.models.bedrock import BedrockModel

    region = os.environ.get("AWS_REGION", "us-east-1")
    profile = os.environ.get("AWS_PROFILE")
    session = boto3.Session(profile_name=profile, region_name=region)
    return BedrockModel(model_id=model_id, boto_session=session)


# ── Automatic tier selection ─────────────────────────────────────────────
# Heuristics to pick the right model tier based on task characteristics.
# This replaces Ruflo's automatic model routing.

_OPUS_KEYWORDS = {
    "architect",
    "design",
    "refactor",
    "migration",
    "security audit",
    "system design",
    "database schema",
    "api design",
    "trade-off",
    "performance analysis",
    "threat model",
}

_HAIKU_KEYWORDS = {
    "format",
    "rename",
    "typo",
    "comment",
    "lint",
    "sort",
    "list",
    "simple",
    "quick",
    "trivial",
    "minor",
    "cleanup",
    "whitespace",
}


def select_tier(task_description: str) -> ModelTier:
    """
    Auto-select model tier based on task complexity.

    - Opus: architecture, design, complex reasoning
    - Haiku: formatting, simple lookups, trivial changes
    - Sonnet: everything else (default)
    """
    lower = task_description.lower()

    for keyword in _OPUS_KEYWORDS:
        if keyword in lower:
            log.debug("Task matched opus keyword '%s'", keyword)
            return ModelTier.OPUS

    for keyword in _HAIKU_KEYWORDS:
        if keyword in lower:
            log.debug("Task matched haiku keyword '%s'", keyword)
            return ModelTier.HAIKU

    # Length heuristic: very short prompts are likely simple
    if len(task_description) < 50:
        return ModelTier.HAIKU

    # Long, detailed prompts suggest complex work
    if len(task_description) > 500:
        return ModelTier.OPUS

    return ModelTier.SONNET
