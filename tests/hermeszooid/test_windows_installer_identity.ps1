$ErrorActionPreference = 'Stop'

function Invoke-ResolvedPaths {
    param(
        [string]$LocalAppData,
        [string]$HermesHome,
        [string]$ZooidHome,
        [string]$HermesZooidHome = ''
    )

    $old = @{
        LOCALAPPDATA = $env:LOCALAPPDATA
        HERMES_HOME = $env:HERMES_HOME
        ZOOID_HOME = $env:ZOOID_HOME
        HERMESZOOID_HOME = $env:HERMESZOOID_HOME
    }
    try {
        $env:LOCALAPPDATA = $LocalAppData
        $env:HERMES_HOME = $HermesHome
        $env:ZOOID_HOME = $ZooidHome
        if ($HermesZooidHome) {
            $env:HERMESZOOID_HOME = $HermesZooidHome
        } else {
            Remove-Item Env:HERMESZOOID_HOME -ErrorAction SilentlyContinue
        }

        $raw = & pwsh -NoProfile -File scripts/install.ps1 -ShowResolvedPaths
        if ($LASTEXITCODE -ne 0) {
            throw "install.ps1 -ShowResolvedPaths failed with exit $LASTEXITCODE"
        }
        return (($raw -join [Environment]::NewLine) | ConvertFrom-Json)
    } finally {
        foreach ($name in $old.Keys) {
            $value = $old[$name]
            if ($null -eq $value) {
                Remove-Item "Env:$name" -ErrorAction SilentlyContinue
            } else {
                Set-Item "Env:$name" $value
            }
        }
    }
}

$root = Join-Path $env:RUNNER_TEMP 'identity-root'
$local = Join-Path $root 'local'
$existingHermes = Join-Path $root 'existing-hermes'
$existingZooid = Join-Path $root 'existing-zooid'
$expectedHome = Join-Path $local 'hermeszooid'
$expectedApp = Join-Path $expectedHome 'app'

$default = Invoke-ResolvedPaths -LocalAppData $local -HermesHome $existingHermes -ZooidHome $existingZooid

if ($default.hermeszooid_home -ne $expectedHome) { throw "default HermesZooid home mismatch: $($default.hermeszooid_home) != $expectedHome" }
if ($default.install_dir -ne $expectedApp) { throw "default app dir mismatch: $($default.install_dir) != $expectedApp" }
if ($null -ne $default.hermes_home) { throw "legacy hermes_home must not be exposed by resolved-path report" }
if ($default.hermeszooid_home -eq $existingHermes -or $default.hermeszooid_home -eq $existingZooid) { throw "HermesZooid inherited another product home" }

$explicit = Join-Path $root 'explicit-hermeszooid'
$explicitResult = Invoke-ResolvedPaths -LocalAppData $local -HermesHome $existingHermes -ZooidHome $existingZooid -HermesZooidHome $explicit
if ($explicitResult.hermeszooid_home -ne $explicit) { throw "explicit HERMESZOOID_HOME was not honored" }
if ($explicitResult.install_dir -ne (Join-Path $explicit "app")) { throw "explicit HermesZooid app dir mismatch" }

Write-Host "HermesZooid Windows resolved-path contract PASS"
