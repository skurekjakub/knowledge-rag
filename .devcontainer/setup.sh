#!/bin/bash
set -e

# Add Poetry to PATH
export PATH="/home/vscode/.local/bin:$PATH"

echo "Installing backend dependencies..."
cd /workspace/backend
poetry install

npm install -g npm@11.8.0

echo "Installing frontend dependencies..."
cd /workspace/frontend
npm install

echo "Triggering Ollama Model Pull (llama3)..."
cd /workspace

curl -X POST http://ollama:11434/api/pull -d '{"name": "nomic-embed-text"}'

curl -X POST http://ollama:11434/api/pull -d '{"name": "llama3"}'

echo "Verifying model is active..."

curl -X POST http://ollama:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Say hello!",
  "stream": false
}'

echo "Workspace Ready!"

