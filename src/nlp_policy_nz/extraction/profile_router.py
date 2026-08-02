"""Route explicit jurisdiction profiles to candidate-only adapters."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType

from nlp_policy_nz.jurisdiction_profiles import ProfileLoader


_ADAPTER_MODULES = {
    "foio_nz": "nlp_policy_nz.extraction.foio_nz_adapter",
    "foio_au": "nlp_policy_nz.extraction.foio_au_adapter",
}


def load_profile_adapter(profile_id: str, *, loader: ProfileLoader | None = None) -> ModuleType:
    """Load the adapter for a verified profile; never fall back silently."""
    profile = (loader or ProfileLoader()).load(profile_id)
    module_name = _ADAPTER_MODULES.get(profile.adapter)
    if module_name is None:
        raise ValueError(f"unsupported adapter in jurisdiction profile: {profile.adapter!r}")
    return import_module(module_name)
