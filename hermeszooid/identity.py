"""Canonical product identity for HermesZooid.

This module is stdlib-only so the launcher can resolve ownership before
importing inherited Hermes runtime modules.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Mapping

PRODUCT_TOKEN = "hermeszooid"
HOME_ENV = "HERMESZOOID_HOME"
LEGACY_ZOOID_HOME_ENV = "ZOOID_HOME"
INHERITED_HERMES_HOME_ENV = "HERMES_HOME"


def resolve_home(
    *,
    env: Mapping[str, str] | None = None,
    platform: str | None = None,
    user_home: Path | str | None = None,
) -> Path:
    """Resolve HermesZooid writable root without consulting Hermes/Zooid homes."""
    source = os.environ if env is None else env
    explicit = str(source.get(HOME_ENV, "")).strip()
    if explicit:
        return Path(explicit).expanduser().resolve()

    plat = (platform or sys.platform).lower()
    home = Path(user_home if user_home is not None else Path.home()).expanduser()

    if plat.startswith("win"):
        local = str(source.get("LOCALAPPDATA", "")).strip()
        base = Path(local).expanduser() if local else home / "AppData" / "Local"
        return (base / PRODUCT_TOKEN).resolve()

    return (home / f".{PRODUCT_TOKEN}").resolve()


def build_runtime_env(
    base_env: Mapping[str, str] | None = None,
    *,
    platform: str | None = None,
    user_home: Path | str | None = None,
) -> dict[str, str]:
    """Translate HermesZooid ownership into inherited Hermes process variables.

    The input mapping is copied. Bare Zooid state is explicitly removed.
    HERMES_HOME is overwritten only in the returned child/process environment,
    never used as an input to product-home selection.
    """
    source = os.environ if base_env is None else base_env
    result = dict(source)
    home = resolve_home(env=source, platform=platform, user_home=user_home)

    result.pop(LEGACY_ZOOID_HOME_ENV, None)
    result[HOME_ENV] = str(home)
    result[INHERITED_HERMES_HOME_ENV] = str(home)
    result["HERMESZOOID_PRODUCT"] = "1"
    return result
