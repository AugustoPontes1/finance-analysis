# Finance Analysis

A Django-based REST API for financial document analysis and data extraction. This project enables users to upload, manage, and analyze financial documents (PDF, XLSX, CSV) with automatic parameter detection, optional customization, and AI-powered label/value extraction.

## Features

- **Document Upload**: Upload financial documents (PDF, XLSX, CSV) with automatic parameter detection
- **Flexible Upload Modes**:
  - Direct upload with automatic parameters
  - Custom upload with manual parameter editing
- **File Management**: Update, delete, and retrieve uploaded documents
- **SeaweedFS Integration**: Scalable distributed file storage using SeaweedFS
- **RESTful API**: Complete REST API for document operations
- **Parameter Customization**: Customize file name, type, and content before saving
- **Concurrent File Updates**: Replace files while maintaining the same document ID
- **AI Extraction**: Identify labels and monetary values from any financial document using a local or remote LLM

## Tech Stack

- **Framework**: Django 6.x
- **API**: Django REST Framework (DRF)
- **File Storage**: SeaweedFS (distributed key-value store)
- **Language**: Python 3.13+
- **Containerization**: Docker (dev environment)
- **AI**: Any OpenAI-compatible remote LLM (OpenAI, Groq, Mistral, Anthropic, etc.) or local LLM via Ollama

## Project Structure

```
finance-analysis/
├── apps/
│   ├── values_extraction/              # Core file management app
│   │   ├── models.py                   # DocumentModel
│   │   ├── views.py                    # Upload, retrieve, update, delete endpoints
│   │   └── serializers.py             # Request/response serializers
│   ├── values_ai_extraction/           # AI-powered extraction app
│   │   ├── llm/
│   │   │   ├── base.py                 # Abstract LLM interface
│   │   │   ├── remote.py              # Generic OpenAI-compatible remote LLM
│   │   │   ├── local.py               # Local LLM via Ollama
│   │   │   └── factory.py             # Selects LLM based on LLM_PROVIDER env var
│   │   ├── views.py                   # analyze_document endpoint
│   │   └── urls.py
│   └── seaweed_service/               # SeaweedFS client
├── configs/                            # Django settings and URL configuration
├── manage.py
├── requirements.txt
├── Makefile
└── docker-compose.dev.yml
```

## Installation

### Prerequisites

- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [Make](https://www.gnu.org/software/make/) — pre-installed on macOS/Linux; on Windows use WSL
- [Git](https://git-scm.com/)
- Python 3.13+ — only required for local development outside Docker

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finance-analysis
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the development environment**
   ```bash
   make MAC=true up   # macOS
   make up            # Linux
   ```

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

> **Work in progress** — this module is still under development and not yet available.

#### Analyze Document
Retrieves an already-uploaded document and uses the configured LLM to identify all label-value pairs (e.g. expense names and amounts).

```http
POST /values_ai_extraction/analyze_document/<id>/v1/
```

```json
{
  "extracted_items": [
    { "label": "Uber",  "value": "R$ 20.50" },
    { "label": "iFood", "value": "R$ 40.30" },
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
DJANGO_APP_PORT=8000

# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/finance_analysis

# SeaweedFS
SEAWEEDFS_MASTER_URL=http://seaweed-master:9333
SEAWEEDFS_VOLUME_URL=http://seaweed-volume:8080

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

| Provider   | `LLM_REMOTE_URL`                                            | Model example               |
|------------|-------------------------------------------------------------|-----------------------------|
| OpenAI     | `https://api.openai.com/v1/chat/completions`               | `gpt-4o-mini`               |
| Groq       | `https://api.groq.com/openai/v1/chat/completions`          | `llama-3.1-8b-instant`      |
| Mistral    | `https://api.mistral.ai/v1/chat/completions`               | `mistral-small-latest`      |
| Together   | `https://api.together.xyz/v1/chat/completions`             | `mistralai/Mixtral-8x7B-...`|
| Anthropic  | `https://api.anthropic.com/v1/messages`                    | `claude-haiku-4-5-20251001` |

### Supported File Types

- `pdf` — PDF documents
- `xlsx` — Excel spreadsheets
- `csv` — Comma-separated values

## Makefile Commands

```bash
make up             # Start all services and tail Django logs
make down           # Stop all services
make logs           # Tail Django container logs
make migrate        # Run Django migrations
make bash           # Open a bash shell in the Django container
make shell          # Open Django shell (manage.py shell)
make psql           # Access PostgreSQL
make test           # Run tests
make clean          # Stop containers and remove volumes
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

## Troubleshooting

### `permission denied` on entrypoint.sh
The volume mount overrides the container's file permissions. Fix with:
```bash
chmod +x entrypoint.sh
```

### `SECRET_KEY` must not be empty
Ensure `SECRET_KEY` is set in `.env` and is a long random string. Generate one with:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### SeaweedFS connection error
- Verify `SEAWEEDFS_MASTER_URL` and `SEAWEEDFS_VOLUME_URL` are correct
- Ensure both seaweed containers are healthy before the Django container starts

## License

This project is licensed under the MIT License - see the LICENSE file for details.
