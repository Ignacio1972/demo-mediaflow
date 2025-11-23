#!/bin/bash

echo "🎨 Starting MediaFlowDemo Frontend (Development Mode)"
echo "=================================================="

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

# Start development server
echo "🚀 Starting Vite dev server on http://localhost:5173"
echo "=================================================="

npm run dev
