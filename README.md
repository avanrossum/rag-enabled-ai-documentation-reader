# API Documentation Assistant

A RAG-powered API documentation assistant that uses OpenAI embeddings and GPT-4o to answer questions about API documentation.

## Features

- Ingests Markdown API documentation
- Chunks and embeds content using OpenAI text-embedding-3-small
- Stores and queries embeddings using FAISS, running locally
- Provides a FastAPI-based /query endpoint for natural language questions
- Retrieves the most relevant chunks via vector similarity
- Sends those chunks + the question to GPT-4o for answering
- Serves all of this via a Docker container on port 8000
- Includes a simple HTML/JS front-end
- Provides health check and metadata endpoints
- Allows swapping out the embedding model

## Prerequisites

- Docker and Docker Compose
- OpenAI API key

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd api-documentation-assistant
```

2. Create a `.env` file with your OpenAI API key:

```bash
cp .env.example .env
```

Edit the `.env` file and add your OpenAI API key.

## Usage

### Starting the Application

1. Build and start the Docker container:

```bash
docker-compose up --build
```

2. The application will be available at http://localhost:8000

### Automatic Vectorization

The system automatically vectorizes the documentation on first startup. This process:
1. Reads all Markdown files in the documentation directory
2. Chunks the content
3. Generates embeddings for each chunk
4. Stores the embeddings in the FAISS vector store

If you update the documentation and need to re-vectorize, you can run:

```bash
docker-compose exec api python scripts/vectorize_docs.py
```

### Querying the Documentation

You can query the documentation using the web interface at http://localhost:8000 or by making a POST request to the API:

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I use the client API?", "top_k": 5}'
```

## Configuration

The application can be configured using environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `EMBEDDING_MODEL`: The OpenAI embedding model to use (default: text-embedding-3-small)
- `COMPLETION_MODEL`: The OpenAI completion model to use (default: gpt-4o)
- `DOCS_DIR`: The directory containing the documentation, used for both host path and container path (default: ./DOCUMENTATION)
- `VECTOR_DB_PATH`: The directory to store the vector database (default: ./vector_db)
- `API_TITLE`: The title of the API displayed in the web interface (default: PYMPL2 Python3 API)

## API Endpoints

- `GET /`: Web interface
- `POST /api/query`: Query the documentation
- `GET /health`: Health check endpoint
- `GET /metadata`: Metadata endpoint

## License

[MIT License](LICENSE)