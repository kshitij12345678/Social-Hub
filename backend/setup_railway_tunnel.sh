#!/bin/bash
# Railway Tunnel Setup Script
# This script helps set up Railway CLI tunnel for PostgreSQL

echo "=========================================="
echo "Railway CLI Tunnel Setup"
echo "=========================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
    echo "✅ Railway CLI installed"
else
    echo "✅ Railway CLI is installed"
fi

echo ""
echo "Step 1: Login to Railway"
echo "----------------------"
echo "This will open your browser for authentication..."
read -p "Press Enter to continue..."
railway login

echo ""
echo "Step 2: Link to your project"
echo "----------------------------"
echo "Select your project: motivated-spontaneity"
read -p "Press Enter to continue..."
railway link

echo ""
echo "Step 3: Create tunnel to PostgreSQL"
echo "-----------------------------------"
echo "This will create a local tunnel to your Railway PostgreSQL database"
echo "Keep this terminal window open while using the database!"
echo ""
read -p "Press Enter to start the tunnel..."
railway connect postgres


