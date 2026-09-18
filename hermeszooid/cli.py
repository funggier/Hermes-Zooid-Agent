"""HermesZooid product launcher."""

from __future__ import annotations

import os
import sys

from .identity import build_runtime_env, resolve_home


def main(argv: list[str] | None = None) -> int | None:
    args = list(sys.argv[1:] if argv is None else argv)

    if args == ["--print-home"]:
        print(resolve_home())
        return 0

    # Establish the product boundary before importing inherited Hermes code.
    runtime_env = build_runtime_env(os.environ)
    os.environ.clear()
    os.environ.update(runtime_env)

    if argv is not None:
        sys.argv = [sys.argv[0], *args]

    from hermes_cli.main import main as hermes_main

    result = hermes_main()
    return result if isinstance(result, int) else None
