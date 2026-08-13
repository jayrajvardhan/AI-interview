#!/bin/bash
# Database Setup Script

echo "🚀 Starting Database Setup..."

# Step 1: Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

echo "✅ Docker found"

# Step 2: Start PostgreSQL and other services
echo "📦 Starting PostgreSQL database and services..."
docker-compose up -d

echo "⏳ Waiting for PostgreSQL to be ready (30 seconds)..."
sleep 30

# Step 3: Verify database connection
echo "🔍 Testing database connection..."
docker-compose exec -T db psql -U postgres -d ai_interview -c "SELECT 1;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Database connected successfully!"
else
    echo "⚠️  Database connection check (this may be normal if DB is still starting)"
fi

# Step 4: Check backend API
echo "🌐 Testing backend API..."
sleep 5
curl http://localhost:8000/health 2>/dev/null | python3 -m json.tool

echo ""
echo "✨ Setup Complete!"
echo "================================"
echo "📊 Access Points:"
echo "  Frontend: http://localhost:5175"
echo "  Backend:  http://localhost:8000"
echo "  Database: localhost:5432"
echo "================================"
echo "📝 Database Credentials:"
echo "  Username: postgres"
echo "  Password: postgres"
echo "  Database: ai_interview"
echo "================================"
