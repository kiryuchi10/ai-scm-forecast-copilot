# Run all SQL files in db/ against MySQL (Docker container scmcore-mysql).
# Usage: .\scripts\run_db_sql.ps1
# Prereq: docker compose up -d mysql

$ErrorActionPreference = "Stop"
$root = if ($PSScriptRoot) { Split-Path $PSScriptRoot -Parent } else { (Get-Location).Path }
if (Test-Path (Join-Path $root "db")) { Set-Location $root }
$dbPath = Join-Path (Get-Location) "db"

# Order: create DB -> create tables -> verify
$order = @("01_init.sql", "02_schema.sql", "03_verify.sql")
foreach ($f in $order) {
    $p = Join-Path $dbPath $f
    if (-not (Test-Path $p)) { Write-Warning "Skip (not found): $p"; continue }
    Write-Host "Running $f ..."
    Get-Content $p -Raw -Encoding UTF8 | docker exec -i scmcore-mysql mysql -u root -p12345
    if ($LASTEXITCODE -ne 0) { throw "Failed: $f" }
}
Write-Host "All SQL files completed."
