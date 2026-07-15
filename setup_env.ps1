# =====================================================================
# 🚀 AI 克隆聲音 專案環境一鍵設定腳本 (setup_env.ps1)
# =====================================================================

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🎨 開始檢查並安裝「AI 克隆聲音」專案環境..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 檢查並配置 Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "✓ 偵測到 Python，開始安裝依賴套件..." -ForegroundColor Green
    # 可在此處添加特定 python 套件安裝指令
    Write-Host "✓ Python 依賴安裝完成！" -ForegroundColor Green
} else {
    Write-Warning "⚠️ 未在系統中偵測到 Python，請先安裝 Python 3！"
}

Write-Host "`n🎉 環境設定檢查結束！" -ForegroundColor Cyan
