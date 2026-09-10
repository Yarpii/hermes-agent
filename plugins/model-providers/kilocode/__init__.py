"""Kilo Code provider profile.

The Kilo AI Gateway (https://kilo.ai) is one OpenAI-compatible endpoint
serving hundreds of models — Anthropic, OpenAI, Google, Z.ai, MoonshotAI,
MiniMax, DeepSeek and more — with usage tracking and BYOK. ``GET /models``
is public and drives the live model picker, so ``fallback_models`` only
covers the offline case; it is curated from that endpoint (agentic,
tool-calling flagships only, never the rate-limited ``:free`` tier).
"""

from providers import register_provider
from providers.base import ProviderProfile

kilocode = ProviderProfile(
    name="kilocode", aliases=("kilo-code", "kilo", "kilo-gateway"), env_vars=("KILOCODE_API_KEY",),
    base_url="https://api.kilo.ai/api/gateway", default_aux_model="google/gemini-3.6-flash",
    display_name="Kilo Code",
    description="Kilo Code — one key, hundreds of models via the Kilo Gateway",
    signup_url="https://kilo.ai/",
    fallback_models=(
        "anthropic/claude-sonnet-4.6",
        "openai/gpt-5.6-sol",
        "google/gemini-3.8-flash",
        "z-ai/glm-5.3",
        "moonshotai/kimi-k3",
        "deepseek/deepseek-v4.1-flash",
    ),
)

register_provider(kilocode)
