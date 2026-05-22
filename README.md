# Finance Analysis

A Django-based REST API for financial document analysis and data extraction. This project enables users to upload, manage, and analyze financial documents (PDF, XLSX, CSV) with automatic parameter detection and optional customization.

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

## Tech Stack

- **Framework**: Django 4.x
- **API**: Django REST Framework (DRF)
- **File Storage**: SeaweedFS (distributed key-value store)
- **Language**: Python 3.8+
- **Containerization**: Docker (dev, staging, prod environments)

## Project Structure

```
finance-analysis/
├── apps/
│   ├── values_extraction/          # Core file extraction app
│   │   ├── models.py               # DocumentModel
│   │   ├── views.py                # API endpoints
│   │   ├── serializers.py          # Request/response serializers
│   │   └── seaweed_service.py      # SeaweedFS integration
│   └── values_ai_extraction/       # AI-powered extraction app
├── configs/                         # Project configuration
├── manage.py                        # Django CLI
├── requirements.txt                 # Python dependencies
└── docker-compose.*.yml            # Docker Compose files
```

## Installation

### Prerequisites

- Python 3.8+
- Docker & Docker Compose
- SeaweedFS master and volume servers

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finance-analysis
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Document Upload

#### 1. Direct Upload (Automatic Parameters)
```http
POST /api/documents/send_file/
Content-Type: multipart/form-data

file: <file>
```

**Response:**
```json
{
  "status": "File uploaded successfully",
  "data": {
    "id": 1,
    "file_name": "document.xlsx",
    "file_type": "xlsx",
    "file_size": 15000,
    "created_at": "2026-05-22T10:30:00Z"
  }
}
```

#### 2. Custom Upload (With Parameter Preview)
```http
POST /api/documents/send_file/?custom=true
Content-Type: multipart/form-data

file: <file>
```

**Response:** Returns preview with detected parameters for customization

#### 3. Confirm Custom Parameters
```http
POST /api/documents/select_file_params/
Content-Type: multipart/form-data

file_name: "my_custom_name"
file_type: "xlsx"
```

### Document Retrieval & Analysis

#### Analyze Document
```http
GET /api/documents/{id}/analyze_file/
```

**Response:**
```json
{
  "file_name": "document.xlsx",
  "file_type": "xlsx",
  "analysis": "analysis_results"
}
```

### Document Update

#### Update Document
```http
PUT /api/documents/{id}/change_file/
Content-Type: multipart/form-data

file: <file>           # Optional: new file to replace
file_name: "new_name"  # Optional: rename document
file_type: "xlsx"      # Optional: change file type
```

Note: Document ID remains unchanged even when updating the file.

### Document Deletion

#### Delete Document
```http
DELETE /api/documents/{id}/remove_file/
```

Removes both the file from SeaweedFS and the document record from the database.

## Configuration

### SeaweedFS Configuration

Add to `.env`:
```env
SEAWEEDFS_MASTER_URL=http://localhost:9333
SEAWEEDFS_VOLUME_URL=http://localhost:8080
```

### Supported File Types

- `pdf` - PDF documents
- `xlsx` - Excel spreadsheets
- `csv` - Comma-separated values

## Usage Examples

### Python/Requests Example

```python
import requests

BASE_URL = "http://localhost:8000/api/documents"

# Direct upload
with open("document.xlsx", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/send_file/",
        files={"file": f}
    )
    print(response.json())

# Custom upload
with open("document.xlsx", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/send_file/?custom=true",
        files={"file": f}
    )
    print(response.json())

# Confirm with custom parameters
response = requests.post(
    f"{BASE_URL}/select_file_params/",
    data={
        "file_name": "Financial Report Q1",
        "file_type": "xlsx"
    }
)
print(response.json())
```

### cURL Examples

```bash
# Direct upload
curl -X POST http://localhost:8000/api/documents/send_file/ \
  -F "file=@document.xlsx"

# Custom upload
curl -X POST "http://localhost:8000/api/documents/send_file/?custom=true" \
  -F "file=@document.xlsx"

# Update document
curl -X PUT http://localhost:8000/api/documents/1/change_file/ \
  -F "file=@new_document.xlsx" \
  -F "file_name=Updated Report"

# Delete document
curl -X DELETE http://localhost:8000/api/documents/1/remove_file/
```

## Docker Deployment

### Development Environment
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### Staging Environment
```bash
docker-compose -f docker-compose.stag.yml up -d
```

### Production Environment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
This project follows PEP 8 standards. Use black and flake8 for code formatting.

```bash
pip install black flake8
black apps/
flake8 apps/
```

## Database Models

### DocumentModel

```python
class DocumentModel(models.Model):
    id              # Auto-generated primary key (used as SeaweedFS file ID)
    file_name       # Document name (customizable)
    file_type       # File type: pdf, xlsx, csv
    file_size       # File size in bytes
    created_at      # Document creation timestamp
    updated_at      # Last update timestamp
```

## Architecture Notes

### File Storage Strategy

This project uses **Option 2** architecture for SeaweedFS integration:
- Database stores document metadata + SeaweedFS file ID
- SeaweedFS stores actual file content
- Document database ID serves as the SeaweedFS file identifier
- This ensures consistent ID management across updates

## Troubleshooting

### SeaweedFS Connection Error
- Verify SeaweedFS master is running on `SEAWEEDFS_MASTER_URL`
- Verify volume server is accessible at `SEAWEEDFS_VOLUME_URL`
- Check firewall rules allow communication

### File Upload Fails
- Ensure file size doesn't exceed configured limits
- Verify file type is supported (pdf, xlsx, csv)
- Check SeaweedFS volume has sufficient storage

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m "feat: add your feature"`
3. Push to branch: `git push origin feature/your-feature`
4. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on the project repository.

---

**Last Updated**: May 22, 2026
