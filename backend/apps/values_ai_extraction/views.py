import io
import pandas as pd
import pypdf

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from backend.apps.values_extraction.models import DocumentModel
from backend.apps.seaweed_service import SeaweedFSService
from backend.apps.values_ai_extraction.llm.factory import get_llm_service

seaweed_service = SeaweedFSService()


def _extract_text(file_bytes: bytes, file_type: str) -> str:
    if file_type == "pdf":
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() for page in reader.pages)
    
    if file_type == "csv":
        return pd.read_csv(io.BytesIO(file_bytes)).to_string(index=False)
    
    if file_type == "xlsx":
        return pd.read_excel(io.BytesIO(file_bytes)).to_string(index=False)

    return file_bytes.decode("utf-8")


class AIExtractionAPIView(ViewSet):

    @action(detail=True, methods=["post"])
    def analyze_document(self, request, pk=None):
        try:
            doc = DocumentModel.objects.get(pk=pk)
        except DocumentModel.DoesNotExist:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        file_bytes = seaweed_service.get_file(doc.seaweed_file_id)

        if not file_bytes:
            return Response({"error": "Failed to retrieve file"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        text = _extract_text(file_bytes, doc.file_type)

        llm = get_llm_service()
        items = llm.extract(text)

        return Response({"extracted_items": items}, status=status.HTTP_200_OK)
