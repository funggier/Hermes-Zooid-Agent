from pathlib import Path

from hermeszooid.update_identity import (
    APP_DIR_NAME,
    CANONICAL_REMOTE,
    HTTPS_REPO_URL,
    RELEASE_URL_BASE,
    SSH_REPO_URL,
    origin_is_product_repo,
)


ROOT = Path(__file__).resolve().parents[2]


def test_update_authority_accepts_only_hermeszooid_repo_forms():
    assert APP_DIR_NAME == "app"
    assert CANONICAL_REMOTE == "github.com/funggier/hermes-zooid-agent"
    assert HTTPS_REPO_URL == "https://github.com/funggier/Hermes-Zooid-Agent.git"
    assert SSH_REPO_URL == "git@github.com:funggier/Hermes-Zooid-Agent.git"
    assert RELEASE_URL_BASE == "https://github.com/funggier/Hermes-Zooid-Agent/releases/tag"

    assert origin_is_product_repo(HTTPS_REPO_URL)
    assert origin_is_product_repo(SSH_REPO_URL)
    assert origin_is_product_repo("https://github.com/funggier/Hermes-Zooid-Agent")
    assert origin_is_product_repo("ssh://git@github.com/funggier/Hermes-Zooid-Agent.git")

    assert not origin_is_product_repo("https://github.com/NousResearch/hermes-agent.git")
    assert not origin_is_product_repo("git@github.com:NousResearch/hermes-agent.git")
    assert not origin_is_product_repo("https://github.com/funggier/Zooid-Agent.git")
    assert not origin_is_product_repo("")
    assert not origin_is_product_repo(None)


def test_runtime_git_updater_has_no_hermes_upstream_auto_sync_or_push():
    source = (ROOT / "hermes_cli/update_cmd_git.py").read_text(encoding="utf-8")
    update_source = (ROOT / "hermes_cli/update_cmd.py").read_text(encoding="utf-8")

    assert "from hermeszooid.update_identity import" in source
    assert "origin_is_product_repo" in source
    assert "NousResearch/hermes-agent" not in source
    assert "git remote add upstream" not in source
    assert '["push", "origin", "main", "--force-with-lease"]' not in source

    assert "_sync_with_upstream_if_needed(" not in update_source
    assert '"fetch" + depth_args + ["upstream", branch]' not in update_source
    assert 'compare_branch = f"upstream/{branch}"' not in update_source


def test_passive_update_and_release_metadata_is_product_owned():
    banner = (ROOT / "hermes_cli/banner.py").read_text(encoding="utf-8")
    remote = (ROOT / "apps/desktop/electron/update-remote.ts").read_text(encoding="utf-8")

    assert "from hermeszooid.update_identity import" in banner
    assert "NousResearch/hermes-agent" not in banner
    assert "nousresearch/hermes-agent" not in banner.lower()
    assert '/ "app"' in banner
    assert "RELEASE_URL_BASE" in banner

    assert "funggier/Hermes-Zooid-Agent.git" in remote
    assert "github.com/funggier/hermes-zooid-agent" in remote.lower()
    assert "NousResearch/hermes-agent" not in remote


def test_bootstrap_updater_uses_product_app_cli_and_home():
    source = (ROOT / "apps/bootstrap-installer/src-tauri/src/update.rs").read_text(encoding="utf-8")
    updater = (ROOT / "apps/desktop/electron/updater-process.ts").read_text(encoding="utf-8")

    assert 'hermes_home.join("app")' in source
    assert 'join("hermeszooid.exe")' in source
    assert 'join("hermeszooid")' in source
    assert '"HERMESZOOID_HOME".to_string()' in source
    assert 'join("hermes-agent")' not in source
    assert 'join("hermes.exe")' not in source
    assert '"HERMES_HOME".to_string()' not in source

    assert "hermeszooid-setup.exe" in updater
    assert "hermes-setup.exe" not in updater


def test_update_cleanup_and_restart_fences_reject_existing_hermes_identity():
    dashboard = (ROOT / "hermes_cli/dashboard_procs.py").read_text(encoding="utf-8")
    blockers = (ROOT / "hermes_cli/_scan_venv_blockers.py").read_text(encoding="utf-8")
    recovery = (ROOT / "hermes_cli/update_restart_recovery.py").read_text(encoding="utf-8")
    fleet = (ROOT / "hermes_cli/update_cmd_fleet.py").read_text(encoding="utf-8")

    assert "command_belongs_to_product" in dashboard
    assert "command_belongs_to_product(cmd)" in dashboard
    assert '"hermes_cli.main"' not in dashboard.split("_DASHBOARD_PATTERNS", 1)[1].split(")", 1)[0]

    assert "command_belongs_to_product(cmdline)" in blockers

    assert '"-m", "hermeszooid"' in recovery
    assert "hermeszooid-gateway" in recovery
    assert "hermeszooid-serve" in recovery
    assert '"hermes-gateway.service"' not in recovery
    assert '_SERVE_UNIT_PATTERN = "hermes-serve*"' not in recovery

    assert '"hermeszooid-gateway*"' in fleet
    assert '"hermeszooid-serve*"' in fleet
    assert '"hermes-gateway*"' not in fleet
    assert '"hermes-serve*"' not in fleet
