"""Kilo Code as a first-class provider: picker metadata, curated fallbacks,
and agreement between the two registries that surface it.

Kilo Code was registered but skeletal — no picker metadata, no fallback
models, no manifest — so it never rendered as more than a bare id in the
provider list. These tests pin the first-class contract.
"""

from pathlib import Path

import pytest

from providers import get_provider_profile
from providers.base import ProviderProfile

KILOCODE_DIR = (
    Path(__file__).resolve().parents[2] / "plugins" / "model-providers" / "kilocode"
)


@pytest.fixture
def profile() -> ProviderProfile:
    resolved = get_provider_profile("kilocode")
    assert resolved is not None
    return resolved


class TestPickerPresence:
    """The fields the provider list / setup picker render."""

    def test_resolves_by_every_alias(self):
        for alias in ("kilocode", "kilo-code", "kilo", "kilo-gateway"):
            resolved = get_provider_profile(alias)
            assert resolved is not None, alias
            assert resolved.name == "kilocode"

    def test_picker_metadata_is_filled_in(self, profile):
        # Bare-name entries read as an unfinished plugin in the picker.
        assert profile.display_name == "Kilo Code"
        assert profile.description
        assert profile.signup_url.startswith("https://")

    def test_base_url_is_the_documented_gateway_endpoint(self, profile):
        """Contract with Kilo's API, not a snapshot: every consumer (auth,
        doctor, transports) derives its endpoint from this one value."""
        assert profile.base_url == "https://api.kilo.ai/api/gateway"


class TestFallbackModels:
    def test_fallbacks_are_curated_agentic_models(self, profile):
        # The live /models endpoint drives the picker; this list only covers
        # the offline case, so it must exist and stay curated.
        assert len(profile.fallback_models) >= 3
        assert len(set(profile.fallback_models)) == len(profile.fallback_models)
        for model_id in profile.fallback_models:
            assert "/" in model_id, model_id
            # :free models are IP-rate-limited (200 req/h) — never a default.
            assert ":free" not in model_id, model_id


class TestRegistryAgreement:
    def test_auth_registry_matches_the_profile(self, profile):
        from hermes_cli.auth import PROVIDER_REGISTRY

        config = PROVIDER_REGISTRY["kilocode"]
        assert config.inference_base_url == profile.base_url
        assert "KILOCODE_API_KEY" in config.api_key_env_vars

    def test_manifest_declares_model_provider_kind(self):
        text = (KILOCODE_DIR / "plugin.yaml").read_text(encoding="utf-8")
        assert "kind: model-provider" in text
