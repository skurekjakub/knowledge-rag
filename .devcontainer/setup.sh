#!/bin/bash
set -e

echo "Triggering Ollama Model Pull (llama3)..."

curl -X POST http://ollama:11434/api/pull -d '{"name": "llama3"}' > /dev/null 2>&1

echo "Verifying model is active..."

curl -X POST http://ollama:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Say hello!",
  "stream": false
}'

echo "Workspace Ready! (Ollama is downloading llama3 in the background)"
