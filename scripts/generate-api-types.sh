#!/bin/bash

# Script to generate TypeScript types from backend OpenAPI spec
# For local development use

set -e

echo "🔍 Checking if backend is running..."

# Check if backend is accessible
if ! curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "❌ Backend is not running!"
    echo "   Run 'docker compose up' in the project root first."
    exit 1
fi

echo "✅ Backend detected!"
echo "📥 Downloading OpenAPI spec..."

# Download OpenAPI spec
cd "$(dirname "$0")/.."
curl -s http://localhost:8000/openapi.json -o openapi.json

if [ ! -f openapi.json ]; then
    echo "❌ Error downloading openapi.json"
    exit 1
fi

echo "✅ OpenAPI spec downloaded successfully!"
echo "🔧 Generating TypeScript types..."

# Enter frontend directory and generate types
cd frontend
npm run generate-api

echo "✅ TypeScript types generated successfully!"
echo "📁 Check the files at: frontend/src/app/api/"
echo ""
echo "💡 Tip: Commit the changes if there are modifications to the types."
