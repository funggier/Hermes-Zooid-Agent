from pathlib import Path


INSTALLER = Path("scripts/install.ps1")


def test_installer_owns_hermeszooid_product_identity_only():
    source = INSTALLER.read_text(encoding="utf-8")

    assert "[string]$HermesZooidHome" in source
    assert "[string]$HermesHome" not in source
    assert "$env:HERMESZOOID_HOME" in source
    assert '"HERMESZOOID_HOME", "User"' in source

    assert '[Environment]::SetEnvironmentVariable("HERMES_HOME"' not in source
    assert '[Environment]::SetEnvironmentVariable("ZOOID_HOME"' not in source
    assert "if ($env:HERMES_HOME)" not in source
    assert "if ($env:ZOOID_HOME)" not in source

    assert "git@github.com:funggier/Hermes-Zooid-Agent.git" in source
    assert "https://github.com/funggier/Hermes-Zooid-Agent.git" in source
    assert "NousResearch/hermes-agent.git" not in source
    assert "github.com/NousResearch/hermes-agent/archive/" not in source

    assert 'foreach ($launcher in @("hermeszooid"))' in source
    assert "hermeszooid.exe" in source
    assert 'foreach ($launcher in @("hermes", "hermes-acp"))' not in source

    assert "taskkill /F /T /IM hermes.exe" not in source
    assert "*Hermes_Gateway*" not in source

    assert r"$env:LOCALAPPDATA\\zooid" not in source
    assert r"$env:LOCALAPPDATA\\Zooid" not in source


def test_installer_persistent_helper_env_is_hermeszooid_owned():
    source = INSTALLER.read_text(encoding="utf-8")
    assert "HERMESZOOID_GIT_BASH_PATH" in source
    assert '[Environment]::SetEnvironmentVariable("HERMES_GIT_BASH_PATH"' not in source
