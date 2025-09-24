# in a powershell terminal at the project root
# cd C:\Users\damia\Documents\DEV\sweetNote
#./build.ps1 -Version "0.1.0"

param(
    [string]$Version = "0.1.0"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$configFile  = Join-Path $projectRoot "config.json"
$distDir     = Join-Path $projectRoot "dist"
$buildDir    = Join-Path $projectRoot "build"

# Config-Version/Datum setzen
if (Test-Path $configFile) {
    $json = Get-Content $configFile | ConvertFrom-Json
    $json.app_version = $Version
    $json.build_date  = (Get-Date).ToString("dd.MM.yyyy")
    $json | ConvertTo-Json -Depth 10 | Set-Content $configFile -Encoding UTF8
}

# Clean
if (Test-Path $distDir)  { Remove-Item $distDir  -Recurse -Force }
if (Test-Path $buildDir) { Remove-Item $buildDir -Recurse -Force }
if (Test-Path "$projectRoot\sweetNote.spec") { Remove-Item "$projectRoot\sweetNote.spec" -Force }

# Python-Launcher wählen (ohne Aliase)
if (Get-Command py -ErrorAction SilentlyContinue) {
    $python = "py"
} else {
    $python = "python"
}

# PyInstaller-Argumente als Array
$piArgs = @(
    "-m","PyInstaller",
    "--onedir","--noconsole",
    "--name","sweetNote",
    "--icon", (Join-Path $projectRoot "Frontend\assets\sweetNote_Icon128.ico"),
    "--hidden-import","customtkinter",
    (Join-Path $projectRoot "Frontend\ui.py")
)

# Build
& $python $piArgs
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller Build fehlgeschlagen."
    exit 1
}

# Release-Ordner aufbauen: komplette Runtime + gewünschte Dateien/Ordner
$releaseDir = Join-Path $distDir "sweetNote-release"
Copy-Item (Join-Path $distDir "sweetNote") $releaseDir -Recurse

# gewünschte Dateien daneben legen (editierbare config.json)
Copy-Item $configFile $releaseDir
if (Test-Path "$projectRoot\README.md")               { Copy-Item "$projectRoot\README.md"               $releaseDir }
if (Test-Path "$projectRoot\LICENSE")                 { Copy-Item "$projectRoot\LICENSE"                 $releaseDir }
if (Test-Path "$projectRoot\THIRD_PARTY_LICENSES.md") { Copy-Item "$projectRoot\THIRD_PARTY_LICENSES.md" $releaseDir }
if (Test-Path "$projectRoot\Licenses")                { Copy-Item "$projectRoot\Licenses" -Recurse $releaseDir }
if (Test-Path "$projectRoot\Frontend\assets")         { Copy-Item "$projectRoot\Frontend\assets" -Recurse $releaseDir }

# ZIP erstellen (nur fertiger Inhalt)
$zipPath = Join-Path $distDir "sweetNote-$Version.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path "$releaseDir\*" -DestinationPath $zipPath

# Aufräumen: nur ZIP in dist behalten
Remove-Item $releaseDir -Recurse -Force

Write-Host "Build abgeschlossen: $zipPath"
