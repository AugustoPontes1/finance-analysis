import requests
import os

API_BASE = os.getenv("API_BASE")


class FileHelper:
    """
    
    """
    
    def upload_file(file, custom: bool = False) -> dict:
        params = {"custom": "true"} if custom else {}
        resp = requests.post(
            f"{API_BASE}/upload_file/v1/",
            files={"file": (file.name, file, file.type)},
            params=params,
        )
        resp.raise_for_status()
        return resp.json()
    
    def confirm_custom_upload(file_name: str, file_type: str) -> dict:
        resp = requests.post(
            f"{API_BASE}/select_file_params/v1/",
            data={"file_name": file_name, "file_type": file_type},
        )
        resp.raise_for_status()
        return resp.json()
    
    def analyze_document(doc_id: int) -> dict:
        resp = requests.post(f"{API_BASE}/analyze_document/{doc_id}/v1/")
        resp.raise_for_status()
        return resp.json()
    
    def delete_document(doc_id: int) -> dict:
        resp = requests.delete(f"{API_BASE}/remove_file/v1/?pk={doc_id}")
        resp.raise_for_status()
        return resp.json()
