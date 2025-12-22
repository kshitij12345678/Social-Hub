#!/bin/bash
# Social Hub Backend Setup Script

echo "🔵 Setting up Social Hub Backend on IIT H server..."

# Go to backend directory
cd ~/backend

# Install Python virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create uploads directories
mkdir -p uploads/profile_pictures uploads/chat_images

echo "✅ Setup complete!"
echo ""
echo "To start the backend, run:"
echo "  cd ~/backend"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000"
