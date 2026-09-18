import ast
import socket
from pathlib import Path

from hermeszooid.listener_defaults import (
    DASHBOARD_PORT,
    HERMES_DASHBOARD_PORT,
    HERMES_PORT_DEFAULTS,
    PORT_DEFAULTS,
)


ROOT = Path(__file__).resolve().parents[2]


def _registry_values() -> set[str]:
    tree = ast.parse((ROOT / "gateway/config.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if not any(isinstance(t, ast.Name) and t.id == "PORT_BINDING_PLATFORM_VALUES" for t in node.targets):
                continue
            call = node.value
            assert isinstance(call, ast.Call)
            assert isinstance(call.func, ast.Name) and call.func.id == "frozenset"
            literal = ast.literal_eval(call.args[0])
            return set(literal)
    raise AssertionError("PORT_BINDING_PLATFORM_VALUES not found")


def test_product_allocation_covers_every_builtin_port_binder_and_is_unique():
    registry = _registry_values()
    assert set(PORT_DEFAULTS) == registry
    assert set(HERMES_PORT_DEFAULTS) == registry
    assert len(set(PORT_DEFAULTS.values())) == len(PORT_DEFAULTS)

    for name in sorted(registry):
        assert PORT_DEFAULTS[name] != HERMES_PORT_DEFAULTS[name]
        assert 1024 <= PORT_DEFAULTS[name] <= 65535

    assert DASHBOARD_PORT == 19119
    assert HERMES_DASHBOARD_PORT == 9119
    assert DASHBOARD_PORT not in PORT_DEFAULTS.values()


def test_expected_hermeszooid_default_allocation():
    assert PORT_DEFAULTS == {
        "api_server": 18642,
        "webhook": 18644,
        "bluebubbles": 18645,
        "msgraph_webhook": 18646,
        "wecom_callback": 18647,
        "line": 18648,
        "whatsapp_cloud": 18090,
        "sms": 18080,
        "feishu": 18765,
        "teams": 13978,
    }


def test_adapter_sources_use_product_default_authority():
    expected = {
        "gateway/platforms/api_server.py": 'DEFAULT_PORT = listener_port("api_server")',
        "gateway/platforms/webhook.py": 'DEFAULT_PORT = listener_port("webhook")',
        "gateway/platforms/msgraph_webhook.py": 'DEFAULT_PORT = listener_port("msgraph_webhook")',
        "gateway/platforms/whatsapp_cloud.py": 'DEFAULT_WEBHOOK_PORT = listener_port("whatsapp_cloud")',
        "gateway/platforms/bluebubbles.py": 'DEFAULT_WEBHOOK_PORT = listener_port("bluebubbles")',
        "plugins/platforms/feishu/adapter.py": '_DEFAULT_WEBHOOK_PORT = listener_port("feishu")',
        "plugins/platforms/wecom/callback_adapter.py": 'DEFAULT_PORT = listener_port("wecom_callback")',
        "plugins/platforms/sms/adapter.py": 'DEFAULT_WEBHOOK_PORT = listener_port("sms")',
        "plugins/platforms/line/adapter.py": 'DEFAULT_WEBHOOK_PORT = listener_port("line")',
        "plugins/platforms/teams/adapter.py": '_DEFAULT_PORT = listener_port("teams")',
    }
    for relpath, marker in expected.items():
        source = (ROOT / relpath).read_text(encoding="utf-8")
        assert "from hermeszooid.listener_defaults import listener_port" in source, relpath
        assert marker in source, relpath


def test_config_env_does_not_reintroduce_inherited_8645_defaults():
    source = (ROOT / "gateway/config_env.py").read_text(encoding="utf-8")
    assert "from hermeszooid.listener_defaults import listener_port" in source
    assert '_int_or(listener_port("wecom_callback"))' in source
    assert '_int_or(listener_port("bluebubbles"))' in source
    assert '_int_or(8645)' not in source


def test_dashboard_uses_product_default_but_desktop_serve_stays_ephemeral():
    parser_source = (ROOT / "hermes_cli/subcommands/dashboard.py").read_text(encoding="utf-8")
    runtime_source = (ROOT / "hermes_cli/main_dashboard.py").read_text(encoding="utf-8")
    desktop_source = (ROOT / "apps/desktop/electron/backend-command.ts").read_text(encoding="utf-8")

    assert "from hermeszooid.listener_defaults import DASHBOARD_PORT" in parser_source
    assert "default=DASHBOARD_PORT" in parser_source
    assert "from hermeszooid.listener_defaults import DASHBOARD_PORT" in runtime_source
    assert "port = DASHBOARD_PORT" in runtime_source
    assert "'--port', '0'" in desktop_source


def _bind(port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
    sock.bind(("127.0.0.1", port))
    sock.listen(1)
    return sock


def test_hermes_and_hermeszooid_api_defaults_bind_simultaneously():
    with _bind(HERMES_PORT_DEFAULTS["api_server"]) as hermes_sock:
        with _bind(PORT_DEFAULTS["api_server"]) as zooid_sock:
            assert hermes_sock.getsockname()[1] == 8642
            assert zooid_sock.getsockname()[1] == 18642


def test_representative_webhook_defaults_bind_simultaneously():
    pairs = [
        ("webhook", 8644, 18644),
        ("bluebubbles", 8645, 18645),
        ("msgraph_webhook", 8646, 18646),
    ]
    for name, hermes_port, product_port in pairs:
        assert HERMES_PORT_DEFAULTS[name] == hermes_port
        assert PORT_DEFAULTS[name] == product_port
        with _bind(hermes_port):
            with _bind(product_port):
                pass
