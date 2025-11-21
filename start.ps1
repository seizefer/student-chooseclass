# 在线大学生选课系统 - 快速启动脚本
# v1.2.0

Write-Host "🚀 启动在线大学生选课系统 v1.2.0" -ForegroundColor Green

# 检查Python
try {
    $pythonVersion = python --version
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 请先安装Python 3.8+" -ForegroundColor Red
    exit 1
}

# 检查Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 请先安装Node.js 16+" -ForegroundColor Red
    exit 1
}

Write-Host "`n🔧 准备启动服务..." -ForegroundColor Yellow

# 询问启动选项
$choice = Read-Host "选择启动方式: [1] 只启动后端 [2] 只启动前端 [3] 同时启动 (1/2/3)"

if ($choice -eq "1" -or $choice -eq "3") {
    Write-Host "📡 启动后端API服务..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-Command", "cd backend; python main_simple.py"
    Start-Sleep 2
    Write-Host "✅ 后端启动完成 - http://localhost:8000" -ForegroundColor Green
}

if ($choice -eq "2" -or $choice -eq "3") {
    Write-Host "🎨 启动前端开发服务器..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-Command", "cd frontend; npm run dev"
    Start-Sleep 3
    Write-Host "✅ 前端启动完成 - 查看终端显示的地址" -ForegroundColor Green
}

Write-Host "`n🔗 访问地址:" -ForegroundColor Magenta
Write-Host "   后端API: http://localhost:8000" -ForegroundColor White
Write-Host "   API文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   前端页面: http://localhost:3001 (或终端显示地址)" -ForegroundColor White

Write-Host "`n🛑 按任意键退出..." -ForegroundColor Yellow
Read-Host 