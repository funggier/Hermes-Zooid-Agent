import os
import subprocess
import sys
import tomllib
from pathlib import Path

from hermeszooid.identity import build_runtime_env, resolve_home
from zooid_cnx.executors.hermes_kanban import HermesKanbanExecutor
from zooid_cnx.store import CogentNexusStore


def test_explicit_hermeszooid_home_wins_and_hermes_home_is_ignored(tmp_path):
    product_home = tmp_path / "hermeszooid"
    hermes_home = tmp_path / "hermes-existing"
    legacy_zooid = tmp_path / "legacy-zooid"

    env = {
        "HERMESZOOID_HOME": str(product_home),
        "HERMES_HOME": str(hermes_home),
        "ZOOID_HOME": str(legacy_zooid),
    }

    assert resolve_home(env=env, platform="win32", user_home=tmp_path) == product_home.resolve()


def test_windows_default_is_localappdata_hermeszooid_even_with_existing_hermes(tmp_path):
    local = tmp_path / "LocalAppData"
    hermes_home = tmp_path / "existing-hermes"

    resolved = resolve_home(
        env={
            "LOCALAPPDATA": str(local),
            "HERMES_HOME": str(hermes_home),
        },
        platform="win32",
        user_home=tmp_path / "Home",
    )

    assert resolved == (local / "hermeszooid").resolve()
    assert resolved != hermes_home.resolve()


def test_posix_default_is_dot_hermeszooid_and_ignores_legacy_roots(tmp_path):
    home = tmp_path / "user"
    resolved = resolve_home(
        env={
            "HERMES_HOME": str(tmp_path / ".hermes"),
            "ZOOID_HOME": str(tmp_path / ".zooid"),
        },
        platform="linux",
        user_home=home,
    )
    assert resolved == (home / ".hermeszooid").resolve()


def test_runtime_env_is_one_way_translation_without_mutating_parent(tmp_path):
    product_home = tmp_path / "hermeszooid"
    parent = {
        "HERMESZOOID_HOME": str(product_home),
        "HERMES_HOME": str(tmp_path / "live-hermes"),
        "ZOOID_HOME": str(tmp_path / "legacy-zooid"),
        "KEEP_ME": "yes",
    }
    before = dict(parent)

    child = build_runtime_env(parent, platform="win32", user_home=tmp_path)

    assert parent == before
    assert child["HERMESZOOID_HOME"] == str(product_home.resolve())
    assert child["HERMES_HOME"] == str(product_home.resolve())
    assert "ZOOID_HOME" not in child
    assert child["KEEP_ME"] == "yes"


def test_cogentnexus_and_kanban_defaults_use_hermeszooid_home(tmp_path, monkeypatch):
    product_home = tmp_path / "hermeszooid"
    monkeypatch.setenv("HERMESZOOID_HOME", str(product_home))
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "live-hermes"))
    monkeypatch.setenv("ZOOID_HOME", str(tmp_path / "legacy-zooid"))

    with CogentNexusStore.open_default() as store:
        assert store.db_path == (product_home / "cogentnexus.db").resolve()

    executor = HermesKanbanExecutor.open_default()
    assert executor.zooid_home == product_home.resolve()
    assert executor.db_path == (
        product_home / "kanban" / "boards" / "cogentnexus" / "kanban.db"
    ).resolve()


def test_pyproject_exposes_hermeszooid_cli_without_removing_hermes_compatibility():
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    scripts = data["project"]["scripts"]

    assert scripts["hermeszooid"] == "hermeszooid.cli:main"
    assert scripts["hermes"] == "hermes_cli.main:main"


def test_python_m_hermeszooid_print_home_ignores_hermes_home(tmp_path):
    product_home = tmp_path / "product"
    env = dict(os.environ)
    env["HERMESZOOID_HOME"] = str(product_home)
    env["HERMES_HOME"] = str(tmp_path / "live-hermes")
    env["ZOOID_HOME"] = str(tmp_path / "legacy-zooid")

    result = subprocess.run(
        [sys.executable, "-m", "hermeszooid", "--print-home"],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()) == product_home.resolve()
