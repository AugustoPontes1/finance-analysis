import logging
import os
import requests

API_BASE = os.getenv("API_BASE")

logger = logging.getLogger(__name__)


class FileHelper:
    """HTTP client for the Finance Analysis API endpoints."""

    _session = requests.Session()

    def upload_file(file, custom: bool = False) -> dict:
        params = {"custom": "true"} if custom else {}
        logger.info(f"Uploading file '{file.name}' (custom={custom}) to {API_BASE}")
        resp = FileHelper._session.post(
            f"{API_BASE}/values_extraction/upload_file/v1/",
            files={"file": (file.name, file, file.type)},
            params=params,
        )
        logger.debug(f"upload_file response [{resp.status_code}]: {resp.text[:300]}")
        resp.raise_for_status()
        return resp.json()

    def confirm_custom_upload(file, file_name: str, file_type: str) -> dict:
        logger.info(f"Confirming custom upload: file_name='{file_name}', file_type='{file_type}'")
        resp = FileHelper._session.post(
            f"{API_BASE}/values_extraction/upload_file/v1/",
            files={"file": (file_name, file, "application/octet-stream")},
            data={"file_name": file_name, "file_type": file_type},
        )
        logger.debug(f"confirm_custom_upload response [{resp.status_code}]: {resp.text[:300]}")
        resp.raise_for_status()
        return resp.json()

    def analyze_document(doc_id: int) -> dict:
        logger.info(f"Requesting AI analysis for doc_id={doc_id}")
        resp = FileHelper._session.post(f"{API_BASE}/values_ai_extraction/analyze_document/{doc_id}/v1/")
        logger.debug(f"analyze_document response [{resp.status_code}]: {resp.text[:300]}")
        resp.raise_for_status()
        return resp.json()

    def delete_document(doc_id: int) -> dict:
        logger.info(f"Deleting document doc_id={doc_id}")
        resp = FileHelper._session.delete(f"{API_BASE}/values_extraction/remove_file/{doc_id}/v1/")
        logger.debug(f"delete_document response [{resp.status_code}]")
        resp.raise_for_status()
        return resp.json() if resp.content else {}
