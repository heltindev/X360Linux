# Double-click BUILD-LOCAL.cmd after Ubuntu WSL2 is installed.
$ErrorActionPreference = 'Stop'
Write-Host "X360Linux | Build Linux on this PC (Ubuntu WSL2)" -ForegroundColor Cyan
$distro = 'Ubuntu-24.04'
# wsl --list --quiet can return UTF-16 output with embedded NUL characters
# in Windows PowerShell. Check bootability rather than parsing the listing.
& wsl.exe -d $distro -u root -- true 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ubuntu WSL2 is not installed on this PC." -ForegroundColor Yellow
    Write-Host "Enable CPU virtualization in BIOS/UEFI if required."
    Write-Host "Then install Ubuntu WSL2 from elevated PowerShell and reboot if prompted."
    Write-Host "Double-click BUILD-LOCAL.cmd again after finishing Ubuntu setup."
    exit 2
}
$download = Join-Path $env:USERPROFILE 'Downloads'
# Build a /mnt/<drive>/... path locally. Sending Windows backslashes
# through WSL's command-line parser strips them before wslpath receives them.
$drive = $download.Substring(0, 1).ToLowerInvariant()
$relative = $download.Substring(3).Replace('\', '/')
$linuxDownload = "/mnt/$drive/$relative"
$linux = @'
set -euo pipefail
cd "$HOME"
if [ ! -d X360Linux-local/.git ]; then
  git clone --recurse-submodules https://github.com/heltindev/X360Linux.git X360Linux-local
fi
cd X360Linux-local
git pull --ff-only
git submodule update --init --recursive
bash scripts/build-local-inputs.sh
cp dist/X360Linux-local-inputs-*.tar.gz "$LINUX_DOWNLOADS/"
'@
Write-Host "Compiling on this PC. The first build can take a long time."
& wsl.exe -d $distro -u root -- env "LINUX_DOWNLOADS=$linuxDownload" bash -lc $linux
if ($LASTEXITCODE -ne 0) { throw "Local Linux compilation failed. No release was modified." }
$archive = Get-ChildItem -Path $download -Filter 'X360Linux-local-inputs-*.tar.gz' |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (!$archive) { throw "Precompiled Linux archive not found in Downloads." }
Write-Host "Built: $($archive.FullName)" -ForegroundColor Green
python.exe (Join-Path $PSScriptRoot 'upload-local-inputs.py') $archive.FullName
if ($LASTEXITCODE -ne 0) { throw "GitHub cache upload failed; file remains in Downloads." }
Write-Host "Open GitHub Actions -> Package precompiled Linux with XeLL and ISO." -ForegroundColor Green
