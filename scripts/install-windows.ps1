<#
Install required developer tools on Windows using winget.

Run PowerShell as Administrator before executing this script.
Usage: Open an Administrative PowerShell and run:
  Set-ExecutionPolicy Bypass -Scope Process -Force
  .\scripts\install-windows.ps1

The script will:
- Install Docker Desktop, Python 3.11, Node.js 22, Git, curl, jq via winget
- Install `pnpm` globally using `npm`
- Print version checks for all installed tools

Note: Docker Desktop may require WSL2 or a reboot. Follow Docker Desktop prompts.
#>

## Auto-elevate: if not running as Administrator, re-launch the script with elevation
$scriptPath = $MyInvocation.MyCommand.Definition
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Not running elevated. Relaunching as Administrator to continue..." -ForegroundColor Yellow
    $argList = "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
    try {
        Start-Process -FilePath "powershell.exe" -ArgumentList $argList -Verb RunAs
        exit 0
    } catch {
        Write-Error "Elevation cancelled or failed. Please re-run this script as Administrator."
        exit 1
    }
}

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Starting Windows tool installer via winget..." -ForegroundColor Cyan

$packages = @(
    @{ id = 'Docker.DockerDesktop'; name = 'Docker Desktop' },
    @{ id = 'Python.Python.3.11'; name = 'Python 3.11' },
    @{ id = 'OpenJS.NodeJS.22'; name = 'Node.js 22 LTS' },
    @{ id = 'Git.Git'; name = 'Git' },
    @{ id = 'GnuWin32.Curl'; name = 'curl' },
    @{ id = 'jq'; name = 'jq' }
)

foreach ($pkg in $packages) {
    $id = $pkg.id
    $name = $pkg.name
    Write-Host "Installing $name ($id) via winget..." -ForegroundColor Yellow
    try {
        winget install --id $id -e --accept-package-agreements --accept-source-agreements
    } catch {
        Write-Warning "winget install failed for $id. You may already have it, or winget needs manual action: $_"
    }
}

# Install pnpm globally using npm (may be available after Node install)
Write-Host "Installing pnpm globally via npm..." -ForegroundColor Yellow
try {
    # Refresh environment for current session in case Node was just installed
    $env:PATH = [System.Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('PATH','User')
    npm install -g pnpm@latest
} catch {
    Write-Warning "Failed to install pnpm via npm. You can run 'npm install -g pnpm' after opening a new shell. Error: $_"
}

Write-Host "\nVerifying installed tools..." -ForegroundColor Cyan

function Show-Version($cmd, $args = '--version') {
    try {
        $out = & $cmd $args 2>&1
        Write-Host "$cmd -> $out"
    } catch {
        Write-Host "$cmd -> not found or failed to run" -ForegroundColor Red
    }
}

Show-Version docker --version
Show-Version docker compose version
Show-Version python --version
Show-Version pip --version
Show-Version node --version
Show-Version npm --version
Show-Version pnpm --version
Show-Version git --version
Show-Version curl --version
Show-Version jq --version

Write-Host "\nInstallation steps completed. If Docker Desktop prompts to enable WSL2, follow those instructions and reboot if required." -ForegroundColor Green
Write-Host "If any tools failed to install, run the failed commands shown above manually." -ForegroundColor Yellow

exit 0
