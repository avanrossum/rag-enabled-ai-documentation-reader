#!/bin/bash
set -e

echo "Starting API Documentation Assistant..."

# Create vector_db directory if it doesn't exist
mkdir -p $VECTOR_DB_PATH

# Check if vector database exists
if [ ! -f "$VECTOR_DB_PATH/vector_store.index" ]; then
    echo "Vector database not found. Running vectorization process..."
    python scripts/vectorize_docs.py
    echo "Vectorization complete."
else
    echo "Vector database found. Skipping vectorization."
fi

# Create an empty vector database directory if it doesn't exist
mkdir -p $VECTOR_DB_PATH

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000