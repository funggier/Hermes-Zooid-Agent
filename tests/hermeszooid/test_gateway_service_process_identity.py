from pathlib import Path

from hermeszooid.gateway_identity import (
    LAUNCHD_LABEL_BASE,
    SYSTEMD_SERVICE_BASE,
    WINDOWS_TASK_BASE,
    command_belongs_to_product,
)


GATEWAY = Path("hermes_cli/gateway.py")
WINDOWS = Path("hermes_cli/gateway_windows.py")


def test_canonical_gateway_identity_is_hermeszooid_owned():
    assert WINDOWS_TASK_BASE == "HermesZooid_Gateway"
    assert SYSTEMD_SERVICE_BASE == "hermeszooid-gateway"
    assert LAUNCHD_LABEL_BASE == "com.funggier.hermeszooid.gateway"


def test_product_command_matcher_rejects_existing_hermes_and_bare_zooid():
    assert command_belongs_to_product(
        r"C:\Users\u\AppData\Local\hermeszooid\bin\hermeszooid.exe gateway run"
    )
    assert command_belongs_to_product(
        r"C:\Python311\python.exe -m hermeszooid gateway run"
    )
    assert command_belongs_to_product(
        "/opt/hermeszooid/venv/bin/python -m hermeszooid --profile ops gateway restart"
    )

    assert not command_belongs_to_product(
        r"C:\Users\u\AppData\Local\hermes\bin\hermes.exe gateway run"
    )
    assert not command_belongs_to_product(
        r"C:\Python311\python.exe -m hermes_cli.main gateway run"
    )
    assert not command_belongs_to_product(
        r"C:\Users\u\AppData\Local\zooid\zooid.exe gateway run"
    )
    assert not command_belongs_to_product("python -m zooid gateway run")


def test_gateway_source_wires_product_fence_into_scan_and_capture_paths():
    source = GATEWAY.read_text(encoding="utf-8")

    assert "from hermeszooid.gateway_identity import" in source
    assert "command_belongs_to_product(command)" in source
    assert 'command = " ".join(argv)' in source
    assert "command_belongs_to_product(command)" in source

    assert "_SERVICE_BASE = SYSTEMD_SERVICE_BASE" in source
    assert 'pattern = f"{SYSTEMD_SERVICE_BASE}*"' in source
    assert "startswith(LAUNCHD_LABEL_BASE)" in source
    assert (
        'return f"{LAUNCHD_LABEL_BASE}-{suffix}" if suffix else LAUNCHD_LABEL_BASE'
        in source
    )
    assert '"-m", "hermeszooid"' in source

    assert 'pattern = "hermes-gateway*"' not in source
    assert 'startswith("ai.hermes.gateway")' not in source


def test_windows_gateway_launchers_reenter_through_hermeszooid_boundary():
    source = WINDOWS.read_text(encoding="utf-8")

    assert "WINDOWS_TASK_BASE" in source
    assert "_TASK_NAME_DEFAULT = WINDOWS_TASK_BASE" in source
    assert "HermesZooid Gateway - Messaging Platform Integration" in source
    assert 'args = ["-m", "hermeszooid"' in source
    assert 'argv = [python_exe, "-m", "hermeszooid"]' in source
    assert 'set "HERMESZOOID_HOME={hermes_home}"' in source
    assert "env.Item({q('HERMESZOOID_HOME')})" in source

    assert 'set "HERMES_HOME={hermes_home}"' not in source
    assert "env.Item({q('HERMES_HOME')})" not in source
    assert 'args = ["-m", "hermes_cli.main"' not in source
