import io
import logging
import pandas as pd
import pypdf

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from backend.apps.values_extraction.models import DocumentModel
from backend.apps.seaweed_service import seaweed_service
from backend.apps.values_ai_extraction.llm.factory import get_llm_service

logger = logging.getLogger(__name__)

seaweed_service_inst = seaweed_service.SeaweedFSService()


def _extract_text(file_bytes: bytes, file_type: str) -> str:
    logger.debug(f"Extracting text from file_type={file_type}, size={len(file_bytes)} bytes")
    if file_type == "pdf":
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text = "\n".join(page.extract_text() for page in reader.pages)
        logger.debug(f"PDF extracted: {len(reader.pages)} pages, {len(text)} chars")
        return text

    if file_type == "csv":
        text = pd.read_csv(io.BytesIO(file_bytes)).to_string(index=False)
        logger.debug(f"CSV extracted: {len(text)} chars")
        return text

    if file_type == "xlsx":
        text = pd.read_excel(io.BytesIO(file_bytes)).to_string(index=False)
        logger.debug(f"XLSX extracted: {len(text)} chars")
        return text

    text = file_bytes.decode("utf-8")
    logger.debug(f"Plain text extracted: {len(text)} chars")
    return text


class AIExtractionAPIView(ViewSet):

    @action(detail=True, methods=["post"])
    def analyze_document(self, request, pk=None):
        logger.info(f"analyze_document called for doc id={pk}")
        try:
            doc = DocumentModel.objects.get(pk=pk)
            logger.debug(f"Document found: id={doc.pk}, file_type={doc.file_type}, seaweed_fid={doc.seaweed_file_id}")
        except DocumentModel.DoesNotExist:
            logger.warning(f"analyze_document: document not found for pk={pk}")
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        logger.debug(f"Fetching file from SeaweedFS: fid={doc.seaweed_file_id}")
        file_bytes = seaweed_service_inst.get_file(doc.seaweed_file_id)

        if not file_bytes:
            logger.error(f"Failed to retrieve file from SeaweedFS for doc id={pk}")
            return Response({"error": "Failed to retrieve file"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        text = _extract_text(file_bytes, doc.file_type)

        if len(text.strip()) < 20:
            logger.warning(f"Extracted text too short ({len(text)} chars) for doc id={pk} — likely a scanned image PDF")
            return Response(
                {"extracted_items": [], "warning": "Document appears to be a scanned image. No extractable text found."},
                status=status.HTTP_200_OK,
            )

        logger.debug(f"Initializing LLM service for doc id={pk}")
        llm = get_llm_service()
        logger.info(f"Running LLM extraction on doc id={pk} using {llm.__class__.__name__}")
        items = llm.extract(text)
        logger.info(f"LLM extraction complete for doc id={pk}: {len(items)} items extracted")

        return Response({"extracted_items": items}, status=status.HTTP_200_OK)
