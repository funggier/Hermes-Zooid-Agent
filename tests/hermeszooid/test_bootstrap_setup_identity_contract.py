import json
import tomllib
from pathlib import Path


ROOT_LOCK = Path("package-lock.json")
WEB_PACKAGE = Path("apps/bootstrap-installer/package.json")
TAURI_CONFIG = Path("apps/bootstrap-installer/src-tauri/tauri.conf.json")
CARGO = Path("apps/bootstrap-installer/src-tauri/Cargo.toml")
MANIFEST = Path("apps/bootstrap-installer/src-tauri/hermes-setup.manifest")
BUILD_RS = Path("apps/bootstrap-installer/src-tauri/build.rs")
MAIN_RS = Path("apps/bootstrap-installer/src-tauri/src/main.rs")
LIB_RS = Path("apps/bootstrap-installer/src-tauri/src/lib.rs")
PATHS_RS = Path("apps/bootstrap-installer/src-tauri/src/paths.rs")
INSTALL_SCRIPT_RS = Path("apps/bootstrap-installer/src-tauri/src/install_script.rs")
BOOTSTRAP_RS = Path("apps/bootstrap-installer/src-tauri/src/bootstrap.rs")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_bootstrap_package_and_tauri_identity_are_hermeszooid_owned():
    web = json.loads(_read(WEB_PACKAGE))
    assert web["name"] == "@hermeszooid/bootstrap-installer"

    lock = json.loads(_read(ROOT_LOCK))
    assert lock["packages"]["apps/bootstrap-installer"]["name"] == "@hermeszooid/bootstrap-installer"
    assert "node_modules/@hermeszooid/bootstrap-installer" in lock["packages"]
    assert "node_modules/@hermes/bootstrap-installer" not in lock["packages"]

    tauri = json.loads(_read(TAURI_CONFIG))
    assert tauri["productName"] == "HermesZooid Setup"
    assert tauri["identifier"] == "com.funggier.hermeszooid.setup"
    assert tauri["app"]["windows"][0]["title"] == "HermesZooid Setup"
    assert tauri["bundle"]["shortDescription"] == "HermesZooid Setup"
    assert "HermesZooid" in tauri["bundle"]["longDescription"]
    assert tauri["bundle"]["publisher"] == "funggier"


def test_bootstrap_cargo_binary_and_windows_manifest_are_unique():
    cargo = tomllib.loads(_read(CARGO))
    assert cargo["package"]["name"] == "hermeszooid-bootstrap"
    assert cargo["bin"][0]["name"] == "HermesZooid-Setup"
    assert cargo["lib"]["name"] == "hermeszooid_bootstrap_lib"

    main = _read(MAIN_RS)
    assert "hermeszooid_bootstrap_lib::run()" in main
    assert "hermes_bootstrap_lib::run()" not in main

    manifest = _read(MANIFEST)
    assert 'name="Funggier.HermesZooid.Setup"' in manifest
    assert "<description>HermesZooid Setup</description>" in manifest
    assert "NousResearch.Hermes.Setup" not in manifest


def test_bootstrap_home_helper_and_log_env_do_not_claim_hermes_or_zooid_roots():
    source = _read(PATHS_RS)
    assert 'std::env::var("HERMESZOOID_HOME")' in source
    assert 'std::env::var("HERMES_HOME")' not in source
    assert 'local_app_data.join("hermeszooid")' in source
    assert 'home.join(".hermeszooid")' in source
    assert 'PathBuf::from(".hermeszooid")' in source
    assert '"hermeszooid-setup.exe"' in source
    assert '"hermeszooid-setup"' in source
    assert '"HERMESZOOID_BOOTSTRAP_LOG"' in source
    assert '"HERMES_BOOTSTRAP_LOG"' not in source


def test_bootstrap_build_and_install_script_source_are_product_owned():
    build = _read(BUILD_RS)
    assert "HERMESZOOID_BUILD_PIN_COMMIT" in build
    assert "HERMESZOOID_BUILD_PIN_BRANCH" in build
    assert "HERMES_BUILD_PIN_COMMIT" not in build
    assert "HERMES_BUILD_PIN_BRANCH" not in build

    source = _read(INSTALL_SCRIPT_RS)
    assert "HERMESZOOID_SETUP_DEV_REPO_ROOT" in source
    assert "HERMES_SETUP_DEV_REPO_ROOT" not in source
    assert "https://raw.githubusercontent.com/funggier/Hermes-Zooid-Agent/" in source
    assert "https://raw.githubusercontent.com/NousResearch/hermes-agent/" not in source
    assert 'User-Agent", "hermeszooid-setup/0.0.1"' in source


def test_bootstrap_fast_path_targets_hermeszooid_app_tree_only():
    lib = _read(LIB_RS)
    assert 'paths::hermes_home().join("app")' in lib
    assert 'paths::hermes_home().join("hermes-agent")' not in lib

    bootstrap = _read(BOOTSTRAP_RS)
    assert 'join("app")' in bootstrap
    assert 'join("HermesZooid.exe")' in bootstrap
    assert 'join("HermesZooid.app")' in bootstrap
    assert 'join("Hermes.exe")' not in bootstrap
    assert 'join("Hermes.app")' not in bootstrap
    assert "HERMESZOOID_BOOTSTRAP_STDIO_HELPER" in bootstrap
    assert "HERMESZOOID_BOOTSTRAP_STDIO_SLEEPER" in bootstrap


def test_bootstrap_identity_does_not_claim_bare_zooid_product_resources():
    tauri = json.loads(_read(TAURI_CONFIG))
    assert tauri["productName"] != "Zooid Setup"
    assert tauri["identifier"] != "com.funggier.zooid.setup"
