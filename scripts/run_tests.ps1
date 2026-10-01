# PowerShell test execution script for Phase 0
Write-Host "Starting Phase 0 Test Suite..." -ForegroundColor Cyan

& .venv\Scripts\python scripts/run_all_tests.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed!" -ForegroundColor Red
    exit $LASTEXITCODE
} else {
    Write-Host "All tests passed!" -ForegroundColor Green
}
