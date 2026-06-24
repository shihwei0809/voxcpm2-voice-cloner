# install.ps1 - VoxCPM2 Voice Cloner Auto Installer
# Automatically detects GPU type and installs corresponding PyTorch + voxcpm
#
# Usage: .\install.ps1

$ErrorActionPreference = 'Stop'
$venvName = '.venv'
$venvPython = Join-Path $venvName 'Scripts\python.exe'
$venvPip = Join-Path $venvName 'Scripts\pip.exe'

Write-Host ''
Write-Host '============================================' -ForegroundColor Cyan
Write-Host '  VoxCPM2 Voice Cloner - Auto Installer' -ForegroundColor Cyan
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''

# --- Step 1: Check uv ---
Write-Host '[1/6] Checking uv package manager...' -ForegroundColor Yellow
$uvExists = $false
$null = python -m uv --version 2>&1
if ($LASTEXITCODE -eq 0) {
    $uvExists = $true
}

if (-not $uvExists) {
    Write-Host '  uv is not installed, installing...' -ForegroundColor Yellow
    python -m pip install -U uv
    if ($LASTEXITCODE -ne 0) {
        Write-Host '  [Error] Failed to install uv via pip.' -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  uv is installed and accessible via 'python -m uv'." -ForegroundColor Green
}

# --- Step 2: Create Python 3.12 venv ---
Write-Host '[2/6] Creating Python 3.12 virtual environment...' -ForegroundColor Yellow
if (Test-Path $venvPython) {
    Write-Host "  $venvName already exists, skipping creation." -ForegroundColor Green
} else {
    python -m uv venv --python 3.12 $venvName
    if ($LASTEXITCODE -ne 0) {
        Write-Host '  [Error] Failed to create virtual environment.' -ForegroundColor Red
        exit 1
    }
    Write-Host "  venv created successfully: $venvName" -ForegroundColor Green
}

# --- Step 3: Detect GPU ---
Write-Host '[3/6] Detecting GPU type...' -ForegroundColor Yellow
$gpuType = 'cpu'
$gpuName = ''

$videoControllers = Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue
foreach ($vc in $videoControllers) {
    $name = $vc.Name
    if ($name -match 'NVIDIA') {
        $gpuType = 'cuda'
        $gpuName = $name
        break
    }
    if ($name -match 'Intel.*Arc|Arc.*Intel|Arc\(TM\)') {
        $gpuType = 'xpu'
        $gpuName = $name
        break
    }
}

switch ($gpuType) {
    'cuda' {
        Write-Host "  Detected NVIDIA GPU: $gpuName" -ForegroundColor Green
        Write-Host '  -> Installing CUDA version of PyTorch' -ForegroundColor Green
        $torchIndex = 'https://download.pytorch.org/whl/cu128'
    }
    'xpu' {
        Write-Host "  Detected Intel Arc GPU: $gpuName" -ForegroundColor Green
        Write-Host '  -> Installing XPU version of PyTorch (with auto patch)' -ForegroundColor Green
        $torchIndex = 'https://download.pytorch.org/whl/xpu'
    }
    default {
        Write-Host '  No dedicated GPU detected, using CPU mode.' -ForegroundColor Yellow
        Write-Host '  -> Installing CPU version of PyTorch (inference will be slower)' -ForegroundColor Yellow
        $torchIndex = 'https://download.pytorch.org/whl/cpu'
    }
}

# --- Step 4: Install PyTorch ---
Write-Host '[4/6] Installing PyTorch...' -ForegroundColor Yellow
$torchVer = if ($gpuType -eq 'xpu') { 'torch==2.12.0+xpu' } else { 'torch' }
if ($gpuType -eq 'xpu') {
    python -m uv pip install --python $venvPython $torchVer --index-url $torchIndex
} else {
    python -m uv pip install --python $venvPython torch --index-url $torchIndex
}
if ($LASTEXITCODE -ne 0) {
    Write-Host '  [Error] Failed to install PyTorch.' -ForegroundColor Red
    exit 1
}
Write-Host "  PyTorch installation completed." -ForegroundColor Green

# --- Step 5: Install voxcpm + sounddevice + resampy ---
Write-Host '[5/6] Installing voxcpm + sounddevice + resampy...' -ForegroundColor Yellow
python -m uv pip install --python $venvPython voxcpm sounddevice resampy
if ($LASTEXITCODE -ne 0) {
    Write-Host '  [Error] Failed to install voxcpm + sounddevice + resampy.' -ForegroundColor Red
    exit 1
}
Write-Host "  voxcpm + sounddevice + resampy installation completed." -ForegroundColor Green

# --- Step 6: XPU Auto patch ---
if ($gpuType -eq 'xpu') {
    Write-Host '[6/6] Applying XPU patch...' -ForegroundColor Yellow
    $repatchScript = Join-Path $PSScriptRoot 'patches\repatch_xpu.ps1'
    if (Test-Path $repatchScript) {
        & $repatchScript
    } else {
        Write-Host '  Warning: patches\repatch_xpu.ps1 not found, skipping patch.' -ForegroundColor Red
        Write-Host '  Intel Arc GPU requires manual patch to function.' -ForegroundColor Red
    }
} else {
    Write-Host '[6/6] No patch needed (non-XPU mode).' -ForegroundColor Green
}

# --- Verification ---
Write-Host ''
Write-Host '============================================' -ForegroundColor Cyan
Write-Host '  Installation Completed!' -ForegroundColor Cyan
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''
Write-Host 'GPU Mode: ' -NoNewline
switch ($gpuType) {
    'cuda' { Write-Host 'NVIDIA CUDA' -ForegroundColor Green }
    'xpu'  { Write-Host 'Intel XPU (patched)' -ForegroundColor Green }
    default { Write-Host 'CPU (Slower)' -ForegroundColor Yellow }
}
Write-Host ''
Write-Host 'Next Steps:' -ForegroundColor Cyan
Write-Host '  1. Record reference voice: .\.venv\Scripts\python.exe record.py'
Write-Host '  2. Generate voice: .\.venv\Scripts\python.exe clone.py "your text here"'
Write-Host ''

# Store GPU type for other scripts
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $PSScriptRoot '.gpu_type'), $gpuType, $utf8NoBom)
