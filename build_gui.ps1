# Build GUI (PySide6) EXE for Student Information Management System
param(
  [string]$AppName = "StudentIMS-GUI",
  [ValidateSet('onefile','onedir')]
  [string]$Mode = 'onefile',
  [switch]$NoConsole
)

$ErrorActionPreference = 'Stop'

function Resolve-Python {
  $venvPy = Join-Path -Path (Get-Location) -ChildPath ".venv/ Scripts/ python.exe" -Resolve -ErrorAction SilentlyContinue
  if (-not $venvPy) {
    $venvPy = Join-Path -Path (Get-Location) -ChildPath ".venv/\Scripts/\python.exe"
  }
  if (Test-Path $venvPy) { return $venvPy }
  return 'python'
}

$python = Resolve-Python
Write-Host "[1/3] Python: $python" -ForegroundColor Cyan
& $python --version | Out-Host

Write-Host "[2/3] Installing deps (PySide6, openpyxl, pyinstaller)..." -ForegroundColor Cyan
& $python -m pip install --upgrade pip | Out-Host
& $python -m pip install PySide6 openpyxl pyinstaller | Out-Host

Write-Host "[3/3] Building GUI executable..." -ForegroundColor Cyan
$icon = Join-Path (Get-Location) 'app.ico'
$iconArgs = @()
if (Test-Path $icon) { $iconArgs = @('--icon', $icon) }
$noConArg = @()
if ($NoConsole.IsPresent) { $noConArg = @('--noconsole') }

# Build GUI only; no web templates needed. Include hidden import for openpyxl.
$cmd = @('-m','PyInstaller','--noconfirm','--clean',"--$Mode") + 
  $iconArgs + $noConArg + @('--hidden-import','openpyxl','--name', $AppName, 'desktop_app/gui_main.py')

& $python $cmd | Out-Host

$dist = Join-Path (Get-Location) "dist/$AppName.exe"
if (Test-Path $dist) {
  Write-Host "Done. Output: $dist" -ForegroundColor Green
} else {
  Write-Host "Finished. Check dist folder." -ForegroundColor Yellow
}
