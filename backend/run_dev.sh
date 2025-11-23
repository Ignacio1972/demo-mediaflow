#!/bin/bash

echo "🚀 Starting MediaFlowDemo Backend (Development Mode)"
echo "=================================================="

# Create storage directories if they don't exist
mkdir -p storage/audio storage/music storage/temp

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Start development server
echo "🎵 Starting FastAPI server on http://localhost:3001"
echo "📝 API Docs: http://localhost:3001/api/docs"
echo "=================================================="

uvicorn app.main:app --reload --host 0.0.0.0 --port 3001
