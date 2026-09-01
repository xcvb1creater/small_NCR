# NCR 环境配置脚本
# 用法: .\setup_env.ps1
# 或指定 venv: .\setup_env.ps1 -VenvPath "D:\Develop\pycharm\pyNewProject01\.venv"

param(
    [string]$VenvPath = "D:\Develop\pycharm\pyNewProject01\.venv"
)

$Python = Join-Path $VenvPath "Scripts\python.exe"
$Pip = Join-Path $VenvPath "Scripts\pip.exe"

if (-not (Test-Path $Python)) {
    Write-Error "找不到 Python: $Python"
    exit 1
}

Write-Host "使用虚拟环境: $VenvPath"
& $Python --version

Write-Host "`n[1/3] 安装依赖..."
& $Pip install -r requirements.txt

Write-Host "`n[2/3] 下载 NLTK punkt 分词器..."
$nltkDir = Join-Path $env:APPDATA "nltk_data\tokenizers"
New-Item -ItemType Directory -Force -Path $nltkDir | Out-Null
$baseUrl = "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers"
foreach ($pkg in @("punkt", "punkt_tab")) {
    $zip = Join-Path $env:TEMP "$pkg.zip"
    Invoke-WebRequest -Uri "$baseUrl/$pkg.zip" -OutFile $zip -UseBasicParsing
    Expand-Archive -Path $zip -DestinationPath $nltkDir -Force
    Remove-Item $zip
}

Write-Host "`n[3/3] 验证导入..."
Set-Location "$PSScriptRoot\NCR"
& $Python -c @"
import torch
import nltk
nltk.data.find('tokenizers/punkt')
from model import SGRAF
from data import get_dataset
from co_train import main
print('torch:', torch.__version__, '| cuda:', torch.cuda.is_available())
print('环境配置成功!')
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n配置完成。在 PyCharm 中将解释器设为: $Python"
} else {
    Write-Error "验证失败，请检查上方报错。"
    exit 1
}
