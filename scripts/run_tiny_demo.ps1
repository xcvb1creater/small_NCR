# 小规模 NCR 实验快速启动脚本
# 用法:
#   方式1 (推荐): 双击 scripts\run_tiny_demo.bat
#   方式2: 先打开 PowerShell，cd 到项目根目录，再执行 .\scripts\run_tiny_demo.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$Python = "D:\Develop\pycharm\pyNewProject01\.venv\Scripts\python.exe"
$DataRoot = Join-Path $ProjectRoot "NCR-data\tiny"
$FullDataRoot = Join-Path $ProjectRoot "NCR-data\NCR-data"
$OutputDir = Join-Path $ProjectRoot "NCR\output\tiny_demo"

if (-not (Test-Path $Python)) {
    Write-Host "错误: 找不到 Python 解释器: $Python" -ForegroundColor Red
    Write-Host "请修改本脚本中的 `$Python` 变量为你的 venv 路径"
    exit 1
}

Write-Host "=== NCR 小规模复现 ===" -ForegroundColor Cyan
Write-Host "项目目录: $ProjectRoot"
Write-Host "输出目录: $OutputDir"
Write-Host ""

Write-Host "=== Step 1: 生成小规模数据集 ===" -ForegroundColor Yellow
if (-not (Test-Path (Join-Path $DataRoot "data\f30k_precomp\train_ims.npy"))) {
    & $Python (Join-Path $ProjectRoot "scripts\make_tiny_dataset.py") `
        --src_root $FullDataRoot `
        --dst_root $DataRoot `
        --dataset f30k_precomp `
        --train_images 100 `
        --dev_images 20 `
        --test_images 20
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host "tiny 数据集已存在，跳过生成"
}

Write-Host ""
Write-Host "=== Step 2: 开始训练 (小规模) ===" -ForegroundColor Yellow
Set-Location (Join-Path $ProjectRoot "NCR")
& $Python run_tiny.py
$ExitCode = $LASTEXITCODE

Write-Host ""
if ($ExitCode -eq 0) {
    Write-Host "=== 训练完成! ===" -ForegroundColor Green
    Write-Host "结果保存在: $OutputDir"
    Write-Host "  - config.json          实验配置"
    Write-Host "  - model_best.pth.tar   最优模型"
    Write-Host "  - f30k_precomp_0.2.npy 噪声索引"
} else {
    Write-Host "=== 训练失败 (exit code: $ExitCode) ===" -ForegroundColor Red
}

exit $ExitCode
