import logging
import mimetypes
import base64
from io import BytesIO

from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet

from backend.apps.values_extraction.serializers import DocumentSerializer
from backend.apps.values_extraction.models import DocumentModel
from backend.apps.seaweed_service.seaweed_service import SeaweedFSService

logger = logging.getLogger(__name__)

seaweed_service = SeaweedFSService()


class DocumentExctractionAPIView(ViewSet):
    """ 
    A API class to manipulate file parameters
    """
    parser_classes = (MultiPartParser, FormParser)
    
    @action(detail=False, methods=['post'])
    def upload_file(self, request):
        """
        Upload file: save on the Seaweed and the reference in DB
        """
        file = request.FILES.get('file')

        if not file:
            logger.warning("upload_file called without a file in the request")
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        custom = request.query_params.get('custom', 'false').lower() == 'true'
        file_ext = file.name.split('.')[-1].lower()
        mime_type, _ = mimetypes.guess_type(file.name)
        file_type_map = {
            'application/pdf': 'pdf',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
            'text/csv': 'csv'
        }
        file_type = file_type_map.get(mime_type, file_ext)

        logger.info(f"Upload request — file='{file.name}', size={file.size}, type={file_type}, custom={custom}")

        override_name = request.data.get('file_name', file.name)
        override_type = request.data.get('file_type', file_type)

        logger.debug(f"Upload flow for '{override_name}' (type={override_type})")
        seaweed_id = seaweed_service.upload_file(file, filename=override_name)

        if not seaweed_id:
            logger.error(f"SeaweedFS upload failed for '{override_name}'")
            return Response(
                {"error": "Failed to upload to SeaweedFS"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        doc = DocumentModel.objects.create(
            file_name=override_name,
            file_type=override_type,
            file_size=file.size,
            seaweed_file_id=seaweed_id
        )
        logger.info(f"Document created in DB: id={doc.pk}, seaweed_fid={seaweed_id}")

        serializer = DocumentSerializer(doc)
        return Response(
            {"status": "File uploaded successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def get_file(self, request, pk=None):
        """
        Show the file from Seaweed by the ID
        """
        logger.debug(f"get_file called for pk={pk}")
        try:
            doc = DocumentModel.objects.get(pk=pk)
            logger.debug(f"Document found: id={doc.pk}, seaweed_fid={doc.seaweed_file_id}")

            file_content = seaweed_service.get_file(doc.seaweed_file_id)

            if not file_content:
                logger.error(f"Failed to retrieve file from SeaweedFS for doc id={pk}")
                return Response(
                    {"error": "Failed to retrieve file"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            logger.info(f"File retrieved for doc id={pk}")
            return Response({
                "file_name": doc.file_name,
                "file_type": doc.file_type
            })

        except DocumentModel.DoesNotExist:
            logger.warning(f"get_file: document not found for pk={pk}")
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def select_file_params(self, request):
        """
        Confirm upload with custom params
        - file_name: custom name (optional)
        - file_type: custom type (optional)
        """
        logger.debug(f"select_file_params called, session key present: {'temp_file' in request.session}")
        temp_file_data = request.session.get('temp_file')

        if not temp_file_data:
            logger.warning("select_file_params: no temp_file found in session")
            return Response(
                {"error": "No temporary file found. Send the custom param file first"},
                status=status.HTTP_400_BAD_REQUEST
            )

        custom_file_name = request.data.get('file_name', temp_file_data['name'])
        custom_file_type = request.data.get('file_type', temp_file_data['name'].split('.')[-1].lower())

        valid_types = ['pdf', 'xlsx', 'csv']
        if custom_file_type not in valid_types:
            logger.warning(f"select_file_params: invalid file_type='{custom_file_type}'")
            return Response({"error": f"Invalid file_type. Must be one of: {valid_types}"})

        logger.debug(f"Creating DB record for '{custom_file_name}' ({custom_file_type})")
        doc = DocumentModel.objects.create(
            file_name=custom_file_name,
            file_type=custom_file_type,
            file_size=temp_file_data['size']
        )

        file_obj = BytesIO(base64.b64decode(temp_file_data['content']))
        logger.debug(f"Uploading custom file '{custom_file_name}' to SeaweedFS")
        seaweed_id = seaweed_service.upload_file(file_obj=file_obj, filename=custom_file_name)

        if not seaweed_id:
            logger.error(f"SeaweedFS upload failed for custom file '{custom_file_name}', rolling back doc id={doc.pk}")
            doc.delete()
            return Response(
                {"error": "Failed to upload to SeaweedFS"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        doc.seaweed_file_id = seaweed_id
        doc.save(update_fields=["seaweed_file_id"])
        logger.info(f"Custom upload complete: doc id={doc.pk}, seaweed_fid={seaweed_id}")

        del request.session['temp_file']
        request.session.modified = True

        serializer = DocumentSerializer(doc)
        return Response(
            {"status": "File uploaded successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
        
    @action(detail=True, methods=['delete'])
    def remove_file(self, request, pk=None):
        """
        Remove the file on Seaweed and the docs informations on DB
        """
        logger.debug(f"remove_file called for pk={pk}")
        try:
            doc = DocumentModel.objects.get(pk=pk)
            logger.debug(f"Deleting seaweed file fid={doc.seaweed_file_id} for doc id={pk}")
            seaweed_service.delete_file(doc.seaweed_file_id)
            doc.delete()
            logger.info(f"Document id={pk} deleted successfully")
            return Response(
                {"status": "File deleted successfully"},
                status=status.HTTP_204_NO_CONTENT
            )

        except DocumentModel.DoesNotExist:
            logger.warning(f"remove_file: document not found for pk={pk}")
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['put'])
    def update_file(self, request, pk=None):
        """
        Update the file on the DB and keeping the same ID
        """
        logger.debug(f"update_file called for pk={pk}")
        try:
            doc = DocumentModel.objects.get(pk=pk)

            new_file = request.FILES.get('file')
            new_file_name = request.data.get('file_name')
            new_file_type = request.data.get('file_type')

            if not new_file and not new_file_name and not new_file_type:
                logger.warning(f"update_file pk={pk}: no fields provided")
                return Response(
                    {"error": "Must provide 'file', 'file_name' or 'file_type'"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if new_file:
                logger.debug(f"Updating SeaweedFS file for doc id={pk}")
                seaweed_service.update_file(doc.seaweed_file_id, new_file, new_file_name or new_file.name)
                doc.file_type = new_file_type or new_file.name.split('.')[-1].lower()
                doc.file_size = new_file.size
                doc.file_name = new_file_name or new_file.name

            if new_file_name and not new_file:
                doc.file_name = new_file_name

            if new_file_type and not new_file:
                doc.file_type = new_file_type

            doc.save()
            logger.info(f"Document id={pk} updated successfully")

            serializer = DocumentSerializer(doc)
            return Response(
                {"status": "File updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        except DocumentModel.DoesNotExist:
            logger.warning(f"update_file: document not found for pk={pk}")
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )