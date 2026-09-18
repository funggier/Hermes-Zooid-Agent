"""HermesZooid-owned fixed listener defaults.

Only fallback values live here. Explicit config/environment values remain
authoritative in the inherited adapters.

The Hermes values are recorded as compatibility evidence so coexistence tests
can prove the product defaults do not overlap with the upstream product.
"""

from __future__ import annotations

from types import MappingProxyType


HERMES_PORT_DEFAULTS = MappingProxyType({
    "api_server": 8642,
    "webhook": 8644,
    "msgraph_webhook": 8646,
    "feishu": 8765,
    "wecom_callback": 8645,
    "bluebubbles": 8645,
    "sms": 8080,
    "whatsapp_cloud": 8090,
    "line": 8646,
    "teams": 3978,
})

PORT_DEFAULTS = MappingProxyType({
    "api_server": 18642,
    "webhook": 18644,
    "msgraph_webhook": 18646,
    "feishu": 18765,
    "wecom_callback": 18647,
    "bluebubbles": 18645,
    "sms": 18080,
    "whatsapp_cloud": 18090,
    "line": 18648,
    "teams": 13978,
})

HERMES_DASHBOARD_PORT = 9119
DASHBOARD_PORT = 19119


def listener_port(platform: str) -> int:
    """Return the fixed HermesZooid fallback port for a port-binding platform."""
    try:
        return PORT_DEFAULTS[str(platform)]
    except KeyError as exc:
        raise KeyError(f"unknown HermesZooid listener surface: {platform!r}") from exc
