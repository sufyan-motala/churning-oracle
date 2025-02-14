# churning-oracle

A RAG-based assistant for credit card churning discussions using r/churningcanada data.

# Disclaimer

This project is very alpha. Not all features are available yet and there will be constant breaking changes.

## Quick Start

1. Create a `.env` file by copying the example:

```bash
cp env.example .env
```

2. Configure your `.env` file:
   - Choose your LLM backend (`openai` or `ollama`)
   - Set required credentials based on your chosen backend
   - Configure Reddit API credentials

### Required Configuration

#### For OpenAI Backend:

```env
LLM_BACKEND=openai
OPENAI_API_KEY=your_key_here
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

#### For Ollama Backend:

```env
LLM_BACKEND=ollama
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

3. Start the services based on your LLM choice:

For OpenAI:

```bash
docker compose --profile openai up -d
```

For Ollama:

```bash
docker compose --profile ollama up -d
```

4. Access the web interface at http://localhost:3000

## Configuration Options

### LLM Settings
- `LLM_BACKEND`: Choose between `openai` or `ollama`
- `TEMPERATURE`: Response creativity (0.0-1.0, default: 0.7)

### OpenAI Configuration
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL_NAME`: Model to use (default: gpt-4o-mini)

### Ollama Configuration
- `OLLAMA_HOST`: Ollama service URL (default: http://ollama:11434)
- `OLLAMA_MODEL_NAME`: Model to use (default: mistral)

### ChromaDB Configuration
- `CHROMA_SERVER_HOST`: ChromaDB host (default: localhost)
- `CHROMA_SERVER_HTTP_PORT`: ChromaDB port (default: 8000)

### API Configuration
- `API_PORT`: Application API port (default: 3000)

## Development

For development with hot-reload:

```bash
docker compose -f docker-compose.dev.yml --profile openai up --build
```

Or for Ollama:

```bash
docker compose -f docker-compose.dev.yml --profile ollama up --build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request
