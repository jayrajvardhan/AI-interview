# Database Setup Script for Windows

Write-Host "🚀 Starting Database Setup..." -ForegroundColor Green

# Step 1: Check if Docker is available
try {
    docker --version | Out-Null
    Write-Host "✅ Docker found" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Step 2: Start PostgreSQL and other services
Write-Host "📦 Starting PostgreSQL database and services..." -ForegroundColor Cyan
cd "d:\AI interview\AI interview"

docker-compose down 2>&1 | Out-Null
docker-compose up -d

Write-Host "⏳ Waiting for PostgreSQL to be ready (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 3: Verify database connection
Write-Host "🔍 Testing database connection..." -ForegroundColor Cyan

$testQuery = docker-compose exec -T db psql -U postgres -d ai_interview -c "SELECT 1;" 2>&1
if ($LASTEXITCODE -eq 0 -or $testQuery -like "*1*") {
    Write-Host "✅ Database connected successfully!" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Database connection test (this may be normal if DB is still starting)" -ForegroundColor Yellow
}

# Step 4: Check backend API
Write-Host "🌐 Testing backend API..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

try {
    $healthCheck = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing | ConvertFrom-Json
    Write-Host "Backend Response: " -ForegroundColor Green
    Write-Host ($healthCheck | ConvertTo-Json | Out-String)
}
catch {
    Write-Host "⚠️  Backend API not yet available (may be starting)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✨ Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host "📊 Access Points:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:5175" -ForegroundColor White
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  Database: localhost:5432" -ForegroundColor White
Write-Host "================================" -ForegroundColor Cyan
Write-Host "📝 Database Credentials:" -ForegroundColor Yellow
Write-Host "  Username: postgres" -ForegroundColor White
Write-Host "  Password: postgres" -ForegroundColor White
Write-Host "  Database: ai_interview" -ForegroundColor White
Write-Host "================================" -ForegroundColor Cyan
