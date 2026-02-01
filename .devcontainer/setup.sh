#!/bin/bash
set -e

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

