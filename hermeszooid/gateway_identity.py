"""Machine-global gateway identity owned by HermesZooid.

Stdlib-only so lifecycle code can import it before provider/config surfaces.
"""

from __future__ import annotations

import shlex
from pathlib import PurePosixPath


WINDOWS_TASK_BASE = "HermesZooid_Gateway"
SYSTEMD_SERVICE_BASE = "hermeszooid-gateway"
LAUNCHD_LABEL_BASE = "com.funggier.hermeszooid.gateway"


def _tokens(command: str) -> list[str]:
    text = str(command or "").strip()
    if not text:
        return []
    try:
        raw = shlex.split(text, posix=False)
    except ValueError:
        raw = text.split()
    return [token.strip().strip('"').strip("'") for token in raw if token.strip()]


def command_belongs_to_product(command: str) -> bool:
    """Return True only when argv identifies the HermesZooid launcher.

    A directory named hermeszooid is not sufficient: either the executable
    itself is hermeszooid or Python explicitly uses -m hermeszooid.
    """
    tokens = _tokens(command)
    if not tokens:
        return False

    executable = tokens[0].replace("\\", "/")
    basename = PurePosixPath(executable).name.lower()
    if basename in {"hermeszooid", "hermeszooid.exe", "hermeszooid.cmd"}:
        return True

    for index, token in enumerate(tokens[:-1]):
        if token == "-m" and tokens[index + 1].lower() == "hermeszooid":
            return True
    return False
