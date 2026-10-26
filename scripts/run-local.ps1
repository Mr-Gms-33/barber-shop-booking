# Run API + UI without Docker (Windows PowerShell)
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"

Write-Host "Starting backend on http://127.0.0.1:8000 ..."
$env:DATABASE_URL = "sqlite+pysqlite:///$((Join-Path $Backend 'local.db'))"
$env:OTEL_EXPORTER_OTLP_ENDPOINT = ""
$env:CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$Backend'; `$env:DATABASE_URL='$($env:DATABASE_URL)'; `$env:OTEL_EXPORTER_OTLP_ENDPOINT=''; `$env:CORS_ORIGINS='$($env:CORS_ORIGINS)'; uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
)

Start-Sleep -Seconds 2

Write-Host "Starting frontend on http://localhost:5173 ..."
$env:VITE_API_URL = "http://127.0.0.1:8000"
Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$Frontend'; `$env:VITE_API_URL='http://127.0.0.1:8000'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Write-Host "Done. Open http://localhost:5173 and http://127.0.0.1:8000/docs"
