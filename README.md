# Finance Analysis

A full-stack application for financial document analysis and AI-powered data extraction. Users can upload financial documents (PDF, XLSX, CSV), manage them through a REST API, and run LLM-based label/value extraction via a Streamlit UI.

## Features

- **Document Upload**: Upload financial documents with automatic parameter detection
- **Flexible Upload Modes**:
  - Direct upload with automatic parameters
  - Custom upload with manual parameter editing before saving
- **File Management**: Update, delete, and retrieve uploaded documents
- **SeaweedFS Integration**: Scalable distributed file storage
- **RESTful API**: Complete REST API built with Django REST Framework
- **AI Extraction**: Identify labels and monetary values from any financial document using a local or remote LLM
- **Streamlit UI**: Browser-based interface for uploading documents and triggering AI extraction

## Tech Stack

- **Backend**: Django 6.x + Django REST Framework
- **Frontend**: Streamlit
- **File Storage**: SeaweedFS (distributed key-value store)
- **Database**: PostgreSQL 15
- **Language**: Python 3.13+
- **Containerization**: Docker + Docker Compose
- **AI**: Any OpenAI-compatible remote LLM (OpenAI, Groq, Mistral, etc.) or local LLM via Ollama

## Project Structure

```
finance-analysis/
├── backend/
│   ├── apps/
│   │   ├── values_extraction/          # Core file management app
│   │   │   ├── models.py               # DocumentModel
│   │   │   ├── views.py                # Upload, retrieve, update, delete endpoints
│   │   │   ├── serializers.py
│   │   │   └── migrations/
│   │   ├── values_ai_extraction/       # AI-powered extraction app
│   │   │   ├── llm/
│   │   │   │   ├── base.py             # Abstract LLM interface
│   │   │   │   ├── remote.py           # Generic OpenAI-compatible remote LLM
│   │   │   │   ├── local.py            # Local LLM via Ollama
│   │   │   │   └── factory.py          # Selects LLM based on LLM_PROVIDER env var
│   │   │   ├── views.py                # analyze_document endpoint
│   │   │   └── urls.py
│   │   └── seaweed_service/            # SeaweedFS client
│   ├── configs/                        # Django settings and URL configuration
│   ├── Dockerfile.dev
│   ├── Dockerfile.stag
│   ├── Dockerfile.prod
│   ├── entrypoint.dev.sh
│   ├── entrypoint.stag.sh
│   └── entrypoint.prod.sh
├── frontend/
│   ├── ui/
│   │   └── ui.py                       # Streamlit app
│   ├── helpers/
│   │   └── helpers.py                  # API client helpers
│   ├── Dockerfile.dev
│   ├── Dockerfile.stag
│   └── Dockerfile.prod
├── manage.py
├── requirements.txt
├── docker-compose.dev.yml
├── docker-compose.stag.yml
├── docker-compose.prod.yml
└── Makefile
```

## Installation

### Prerequisites

- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [Make](https://www.gnu.org/software/make/) — pre-installed on macOS/Linux; on Windows use WSL
- [Git](https://git-scm.com/)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finance-analysis
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Start the development environment**
   ```bash
   make up           # Linux
   make MAC=true up  # macOS
   ```

4. **Access the services**
   - Streamlit UI: http://localhost:8501
   - Django API: http://localhost:`DJANGO_APP_PORT`
   - SeaweedFS admin: http://localhost:18080

## API Endpoints

### Document Management (`/values_extraction/`)

#### Upload (Direct)
```http
POST /values_extraction/upload_file/v1/
Content-Type: multipart/form-data

file: <file>
```

```json
{
  "status": "File uploaded successfully",
  "data": {
    "id": 1,
    "file_name": "expenses.pdf",
    "file_type": "pdf",
    "file_size": 15000,
    "created_at": "2026-05-31T10:30:00Z"
  }
}
```

#### Upload (Custom — preview before saving)
```http
POST /values_extraction/upload_file/v1/?custom=true
Content-Type: multipart/form-data

file: <file>
```

#### Confirm Custom Parameters
```http
POST /values_extraction/select_file_params/v1/
Content-Type: multipart/form-data

file_name: "my_custom_name"
file_type: "pdf"
```

#### Retrieve File
```http
GET /values_extraction/get_file/v1/?pk=<id>
```

#### Update File
```http
PUT /values_extraction/update_file/v1/?pk=<id>
Content-Type: multipart/form-data

file: <file>         # optional
file_name: "name"    # optional
file_type: "xlsx"    # optional
```

#### Delete File
```http
DELETE /values_extraction/remove_file/v1/?pk=<id>
```

---

### AI Extraction (`/values_ai_extraction/`)

> **Work in progress** — this module is still under active development and behaviour may change.

#### Analyze Document
Retrieves an already-uploaded document and uses the configured LLM to identify all label-value pairs (e.g. expense names and amounts).

```http
POST /values_ai_extraction/analyze_document/<id>/v1/
```

```json
{
  "extracted_items": [
    { "label": "Uber",    "value": "R$ 20.50" },
    { "label": "iFood",   "value": "R$ 40.30" },
    { "label": "Netflix", "value": "R$ 55.90" }
  ]
}
```

## Configuration

### Environment Variables

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,django
DJANGO_APP_PORT=8081

# Database (individual vars — used by settings.py)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=finance_analysis
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=127.0.0.1   # use "postgres" inside Docker
DB_PORT=5432

# SeaweedFS
SEAWEEDFS_MASTER_URL=http://seaweed-master:9333
SEAWEEDFS_VOLUME_URL=http://seaweed-volume:8080

# Streamlit — override only when running outside Docker
API_BASE=http://localhost:8081

# LLM — set to "local" to use Ollama instead
LLM_PROVIDER=remote

# Remote LLM (any OpenAI-compatible provider)
LLM_REMOTE_URL=https://api.openai.com/v1/chat/completions
LLM_REMOTE_API_KEY=your-api-key
LLM_REMOTE_MODEL=gpt-4o-mini

# Local LLM (Ollama)
LLM_MODEL_URL=http://localhost:11434/api/generate
LLM_MODEL_NAME=llama3.2
```

### Supported Remote LLM Providers

| Provider  | `LLM_REMOTE_URL`                                   | Model example          |
|-----------|----------------------------------------------------|------------------------|
| OpenAI    | `https://api.openai.com/v1/chat/completions`       | `gpt-4o-mini`          |
| Groq      | `https://api.groq.com/openai/v1/chat/completions`  | `llama-3.1-8b-instant` |
| Mistral   | `https://api.mistral.ai/v1/chat/completions`       | `mistral-small-latest` |
| Together  | `https://api.together.xyz/v1/chat/completions`     | `mixtral-8x7b`         |

### Supported File Types

- `pdf` — PDF documents
- `xlsx` — Excel spreadsheets
- `csv` — Comma-separated values

## Makefile Commands

```bash
make up                # Start all services and tail Django logs
make down              # Stop all services
make logs              # Tail Django container logs
make migrate           # Run Django migrations
make bash              # Open a bash shell in the Django container
make shell             # Open Django shell (manage.py shell)
make psql              # Access PostgreSQL
make test              # Run tests
make test-coverage     # Run tests with coverage report
make clean             # Stop containers
make clean-all         # Stop containers and remove volumes + images
make build             # Build Docker images
```

> Append `MAC=true` on macOS: `make MAC=true up`

## Architecture

### File Storage
- `DocumentModel` in PostgreSQL stores metadata and the SeaweedFS file ID
- SeaweedFS stores the actual file bytes
- The document DB ID is used as the SeaweedFS identifier, keeping IDs consistent across updates

### AI Extraction
- `BaseLLMService` defines the interface (`extract(text) -> list[dict]`)
- `RemoteLLMService` calls any OpenAI-compatible HTTP endpoint
- `LocalLLMService` calls a local Ollama server
- `get_llm_service()` (factory) picks which one based on `LLM_PROVIDER`
- The view retrieves the file from SeaweedFS, extracts its text, and passes it to the LLM

### Docker Networking
- All services share `finance-network-dev` (bridge)
- Streamlit reaches Django via `http://django:<DJANGO_APP_PORT>` (internal DNS)
- `PYTHONPATH=/app` is set in the Streamlit container so `frontend.*` imports resolve correctly

## Troubleshooting

### `permission denied` on entrypoint
```bash
chmod +x backend/entrypoint.dev.sh
```

### `SECRET_KEY` must not be empty
Generate one with:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### DB connection error (`no password supplied`)
Ensure all `DB_*` variables are set in `.env`. The app reads individual `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — not a `DATABASE_URL` string.

### SeaweedFS connection error
- Verify `SEAWEEDFS_MASTER_URL` and `SEAWEEDFS_VOLUME_URL` are correct
- Both seaweed containers must be healthy before Django starts (enforced via `depends_on` healthchecks)

### Streamlit cannot reach Django
Inside Docker, use `http://django:<port>` not `http://localhost:<port>`. The compose file sets `API_BASE=http://django:${DJANGO_APP_PORT}` automatically.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
