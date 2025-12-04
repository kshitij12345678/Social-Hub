#!/bin/bash
# Setup local PostgreSQL for development

echo "Setting up local PostgreSQL for development..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check if container already exists
if docker ps -a | grep -q local-postgres; then
    echo "⚠️  Local PostgreSQL container already exists"
    read -p "Remove and recreate? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker stop local-postgres 2>/dev/null
        docker rm local-postgres 2>/dev/null
    else
        echo "Starting existing container..."
        docker start local-postgres
        exit 0
    fi
fi

# Create PostgreSQL container
echo "Creating local PostgreSQL container..."
docker run --name local-postgres \
  -e POSTGRES_PASSWORD=localpass \
  -e POSTGRES_DB=socialhub_db \
  -e POSTGRES_USER=postgres \
  -p 5432:5432 \
  -d postgres:15

echo "Waiting for PostgreSQL to start..."
sleep 5

# Test connection
if docker exec local-postgres psql -U postgres -d socialhub_db -c "SELECT 1" &>/dev/null; then
    echo "✅ Local PostgreSQL is running!"
    echo ""
    echo "Connection details:"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: socialhub_db"
    echo "  User: postgres"
    echo "  Password: localpass"
    echo ""
    echo "Update your .env file:"
    echo "  DATABASE_URL=postgresql+psycopg://postgres:localpass@localhost:5432/socialhub_db"
    echo ""
    echo "To stop: docker stop local-postgres"
    echo "To start: docker start local-postgres"
else
    echo "❌ Failed to start PostgreSQL"
    exit 1
fi
