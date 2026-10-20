$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw '还没有找到 uv。请先安装 uv，安装方法在 README 的“第一次怎么装”里。装好后重新打开窗口，再双击安装.cmd。'
}
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue) -or -not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw '还没有找到 Node.js。请先安装 Node.js 22.12 或更高版本，装好后重新打开窗口。'
}
$nodeVersion = [version]((& node --version).Trim().TrimStart('v'))
if ($nodeVersion -lt [version]'22.12.0') {
    throw "当前 Node.js 版本是 $nodeVersion，请升级到 22.12 或更高版本。"
}
if (-not (Test-Path -LiteralPath 'backend/.env')) {
    Copy-Item -LiteralPath 'backend/.env.example' -Destination 'backend/.env'
}
Write-Host '第 1 步：准备 Python 3.12 和运行所需的库，第一次可能需要下载。'
Push-Location -LiteralPath 'backend'
try {
    uv sync --frozen --python 3.12
    if ($LASTEXITCODE -ne 0) { throw 'Python 环境安装失败。请查看上方报错，检查网络后重新双击安装.cmd。' }
} finally { Pop-Location }
Write-Host '第 2 步：安装网页所需的库。'
Push-Location -LiteralPath 'frontend'
try {
    npm.cmd ci
    if ($LASTEXITCODE -ne 0) { throw '网页依赖下载失败。请查看上方报错，检查网络后重试。' }
    Write-Host '第 3 步：生成网页。'
    npm.cmd run build
    if ($LASTEXITCODE -ne 0) { throw '网页生成失败，请查看上方报错。' }
} finally { Pop-Location }
Write-Host ''
Write-Host '安装完成。'
Write-Host '接下来：双击“配置.cmd”，填写 DeepSeek 和 Tavily 密钥并保存。'
Write-Host '然后：双击“启动.cmd”，等待浏览器打开。'
