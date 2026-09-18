import importlib.util
import subprocess
import sys
from pathlib import Path

import hermeszooid.cnx as cnx


def test_hermeszooid_cnx_namespace_is_canonical():
    assert hasattr(cnx, "CogentNexusStore")
    assert hasattr(cnx, "RecoveryAction")
    assert cnx.__package__ == "hermeszooid.cnx"


def test_legacy_zooid_cnx_top_level_package_is_absent():
    assert importlib.util.find_spec("zooid_cnx") is None
    assert not Path("zooid_cnx").exists()


def test_python_m_hermeszooid_cnx_is_operator_surface():
    result = subprocess.run(
        [sys.executable, "-m", "hermeszooid.cnx", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "create" in result.stdout
    assert "status" in result.stdout
    assert "recover" in result.stdout
