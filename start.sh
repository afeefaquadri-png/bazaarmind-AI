#!/bin/bash
# BazaarMind AI - Quick Start Script
# Run this from the project root

echo "🚀 Starting BazaarMind AI..."
echo ""

# Check if MongoDB is running
if ! pgrep -x mongod > /dev/null; then
  echo "⚠️  MongoDB is not running. Starting..."
  mongod --fork --logpath /tmp/mongod.log || echo "Please start MongoDB manually: mongod"
fi

# Backend
echo "📦 Starting Backend (FastAPI)..."
cd backend
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "⚠️  Created .env from template. Add your API keys."
fi
pip install -r requirements.txt -q
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo "✅ Backend running at http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"

# Frontend
echo ""
echo "🎨 Starting Frontend (React)..."
cd ../frontend
npm install --silent
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend running at http://localhost:3000"

echo ""
echo "🎉 BazaarMind AI is ready!"
echo ""
echo "  Dashboard:  http://localhost:3000"
echo "  API Docs:   http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait and cleanup
trap "kill $BACKEND_PID $FRONTEND_PID; echo 'Stopped.'" INT
wait
