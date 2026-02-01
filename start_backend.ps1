# Script para iniciar el backend
# Uso: .\start_backend.ps1

Write-Host "🚀 Iniciando Backend - Catálogo de Rutas" -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual
Write-Host "📦 Activando entorno virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Ir al directorio backend
Set-Location backend

# Iniciar servidor
Write-Host "🔥 Iniciando servidor FastAPI..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 Documentación: http://localhost:8000/docs" -ForegroundColor Magenta
Write-Host "🛑 Detener: Ctrl+C" -ForegroundColor Red
Write-Host ""

python -m uvicorn app.main:app --reload
