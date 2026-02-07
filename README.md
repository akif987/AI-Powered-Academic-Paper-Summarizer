# Academic Paper Summarizer

A production-ready RAG (Retrieval-Augmented Generation) web application for summarizing and querying academic papers using AI.

## Features

- 📄 **PDF Upload**: Upload academic papers and automatically extract, chunk, and embed text
- ❓ **Q&A Interface**: Ask natural language questions about your papers
- 📝 **Structured Summaries**: Generate abstract-level, section-level, and key point summaries
- 🔍 **Semantic Search**: Find relevant sections using vector similarity search
- ⚡ **Smart Caching**: Cache generated responses for instant retrieval
- 🔒 **Citation Tracking**: Answers include references to source chunks

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11+ |
| UI | Streamlit |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| PDF Parsing | PyMuPDF |
| Embeddings | Google Gemini (`gemini-embedding-1.0`) |
| Generation | Google Gemini (`gemini-1.5-flash`) |
| Compression | ScaleDown API |

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+
- Google Gemini API key ([Get one here](https://ai.google.dev/))
- ScaleDown API key ([Get one here](https://scaledown.ai/))

## Installation

### 1. Clone and Install Dependencies

```bash
# Clone the repository
cd "RAG Project"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Set Up PostgreSQL

```sql
-- Connect to PostgreSQL and create database
CREATE DATABASE paper_summarizer;
```

### 3. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
```

Required environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `SCALEDOWN_API_KEY`: Your ScaleDown API key
- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:password@localhost/paper_summarizer`)

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Start the Application

```bash
python -m streamlit run app/Home.py
```

The app will be available at `http://localhost:8501`

## Usage

### Upload Papers

1. Navigate to **📄 Upload Papers**
2. Select a PDF file of an academic paper
3. Click **Process Paper** to extract, chunk, and embed the content
4. Wait for processing to complete

### Ask Questions

1. Navigate to **❓ Ask Questions**
2. Select a paper from the dropdown
3. Type your question in the chat input
4. View the AI-generated answer with source citations

### View Summaries

1. Navigate to **📝 View Summaries**
2. Select a paper
3. Choose summary type (Abstract, Section, or Key Points)
4. Click **Generate** to create the summary
5. Summaries are cached for instant future access

## Project Structure

```
RAG Project/
├── app/
│   ├── Home.py                 # Streamlit entry point (Homepage)
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── styles.py               # Custom CSS design system
│   ├── models/                 # SQLAlchemy models
│   │   ├── paper.py
│   │   ├── chunk.py
│   │   ├── summary.py
│   │   └── query_cache.py
│   ├── services/               # Business logic
│   │   ├── pdf_service.py
│   │   ├── chunking_service.py
│   │   ├── embedding_service.py      # Batch processing with rate limiting
│   │   ├── retrieval_service.py
│   │   ├── compression_service.py    # ScaleDown integration
│   │   └── generation_service.py
│   └── pages/                  # Streamlit pages
│       ├── 1_📄_Upload_Papers.py
│       ├── 2_❓_Ask_Questions.py
│       └── 3_📝_View_Summaries.py
├── migrations/                 # Alembic migrations
├── tests/                      # Unit tests
├── .env.example
├── pyproject.toml
├── alembic.ini
├── ARCHITECTURE.md             # Detailed system architecture
└── README.md
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_chunking.py -v
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `CHUNK_SIZE` | 500 | Target tokens per chunk |
| `CHUNK_OVERLAP` | 50 | Overlap tokens between chunks |
| `TOP_K_CHUNKS` | 5 | Chunks to retrieve per query |
| `GEMINI_EMBEDDING_MODEL` | gemini-embedding-1.0 | Embedding model |
| `GEMINI_GENERATION_MODEL` | gemini-1.5-flash | Generation model |
| `EMBEDDING_BATCH_SIZE` | 10 | Chunks per batch (rate limiting) |

## Architecture

For detailed architecture documentation, see **[ARCHITECTURE.md](./ARCHITECTURE.md)**.

### RAG Pipeline

1. **Ingestion**: PDF → Text extraction → Semantic chunking → Gemini embeddings (batched) → PostgreSQL storage
2. **Query**: Question → Embed → Vector similarity search → Retrieve top-k chunks
3. **Compression**: Chunks + Question → ScaleDown API → Compressed context (40-60% reduction)
4. **Generation**: Compressed context + Question → Gemini → Cited answer

### Key Features

- **Batch Embedding**: Processes chunks in batches of 10 with 2-second delays to avoid rate limits
- **Context Compression**: ScaleDown API reduces token usage by 40-60% while preserving semantics
- **Smart Caching**: Summaries and queries cached in database for instant retrieval
- **Error Handling**: Graceful degradation with fallback to uncompressed context

### Anti-Hallucination Measures

- Structured prompts requiring source-based answers
- Explicit instructions to state when information is not found
- Confidence scoring based on response content
- Chunk references for verification

## Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Detailed system architecture, component design, and data flows
- **[.env.example](./.env.example)** - Environment variable template

## Troubleshooting

### Rate Limit Errors (429)
- The embedding service uses batch processing with delays to handle free tier limits
- If you still hit limits, reduce `EMBEDDING_BATCH_SIZE` in config.py

### ScaleDown API Errors
- Ensure your API key is correctly set in `.env`
- The system falls back to uncompressed context if compression fails

### Database Connection Issues
- Verify PostgreSQL is running
- Check `DATABASE_URL` format in `.env`

## License

MIT License
