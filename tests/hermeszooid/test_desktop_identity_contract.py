import json
from pathlib import Path


DESKTOP_PACKAGE = Path("apps/desktop/package.json")
ROOT_LOCK = Path("package-lock.json")
MAIN = Path("apps/desktop/electron/main.ts")
BOOTSTRAP = Path("apps/desktop/electron/bootstrap-runner.ts")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_desktop_package_has_unique_hermeszooid_os_identity():
    package = json.loads(_read(DESKTOP_PACKAGE))
    assert package["name"] == "hermeszooid-desktop"
    assert package["productName"] == "HermesZooid"
    assert package["repository"]["url"] == "git+https://github.com/funggier/Hermes-Zooid-Agent.git"

    build = package["build"]
    assert build["appId"] == "com.funggier.hermeszooid"
    assert build["productName"] == "HermesZooid"
    assert build["executableName"] == "HermesZooid"
    assert build["protocols"] == [{"name": "HermesZooid Protocol", "schemes": ["hermeszooid"]}]
    assert build["artifactName"].startswith("HermesZooid-")
    assert build["dmg"]["title"] == "Install HermesZooid"
    assert build["nsis"]["shortcutName"] == "HermesZooid"
    assert build["nsis"]["uninstallDisplayName"] == "HermesZooid"
    assert build["mac"]["extendInfo"]["CFBundleDisplayName"] == "HermesZooid"
    assert build["mac"]["extendInfo"]["CFBundleExecutable"] == "HermesZooid"
    assert build["mac"]["extendInfo"]["CFBundleName"] == "HermesZooid"


def test_desktop_package_lock_tracks_new_workspace_identity():
    lock = json.loads(_read(ROOT_LOCK))
    assert lock["packages"]["apps/desktop"]["name"] == "hermeszooid-desktop"


def test_desktop_main_owns_user_data_runtime_home_protocol_and_aumid():
    source = _read(MAIN)

    assert "process.env.HERMESZOOID_DESKTOP_USER_DATA_DIR" in source
    assert "process.env.HERMES_DESKTOP_USER_DATA_DIR" not in source

    assert "function resolveHermesZooidHome()" in source
    assert "process.env.HERMESZOOID_HOME" in source
    assert "readWindowsUserEnvVar('HERMESZOOID_HOME')" in source
    assert "process.env.HERMES_HOME" not in source
    assert "readWindowsUserEnvVar('HERMES_HOME')" not in source
    assert "path.join(process.env.LOCALAPPDATA, 'hermeszooid')" in source
    assert "path.join(app.getPath('home'), '.hermeszooid')" in source
    assert "path.join(process.env.LOCALAPPDATA, 'hermes')" not in source
    assert "path.join(app.getPath('home'), '.hermes')" not in source

    assert "const HERMESZOOID_HOME = resolveHermesZooidHome()" in source
    assert "const ACTIVE_HERMESZOOID_ROOT = path.join(HERMESZOOID_HOME, 'app')" in source
    assert "path.join(HERMES_HOME, 'hermes-agent')" not in source

    assert "app.setAppUserModelId('com.funggier.hermeszooid')" in source
    assert "com.nousresearch.hermes" not in source

    assert "const HERMESZOOID_PROTOCOL = DEV_SERVER ? 'hermeszooid-dev' : 'hermeszooid'" in source
    assert "const DEEPLINK_SCHEMES = DEV_SERVER ? ['hermeszooid-dev', 'hermeszooid'] : ['hermeszooid']" in source
    assert "const HERMES_PROTOCOL = DEV_SERVER ? 'hermes-dev' : 'hermes'" not in source


def test_desktop_bootstrap_uses_hermeszooid_repo_root_and_owner_env():
    source = _read(BOOTSTRAP)

    assert "https://raw.githubusercontent.com/funggier/Hermes-Zooid-Agent/" in source
    assert "https://raw.githubusercontent.com/NousResearch/hermes-agent/" not in source
    assert "path.join(hermesZooidHome, 'app', 'scripts', installScriptName())" in source
    assert "path.join(hermesHome, 'hermes-agent', 'scripts', installScriptName())" not in source

    assert "HERMESZOOID_HOME: hermesZooidHome" in source
    assert "HERMES_HOME: hermesHome || process.env.HERMES_HOME" not in source


def test_desktop_machine_identity_does_not_claim_bare_zooid_resources():
    package = json.loads(_read(DESKTOP_PACKAGE))
    build = package["build"]

    assert package["name"] != "zooid"
    assert build["appId"] != "com.funggier.zooid"
    assert "zooid" not in build["protocols"][0]["schemes"]
