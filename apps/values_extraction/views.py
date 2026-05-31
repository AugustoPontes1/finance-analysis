from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet
import mimetypes
from io import BytesIO

from apps.values_extraction.serializers import DocumentSerializer
from apps.values_extraction.models import DocumentModel
from apps.seaweed_service.seaweed_service import SeaweedFSService

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
            return Response(
                {"error": "Noe file provided"},
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
        
        # If not custom, make the upload directly to the Seaweed and DB
        if not custom:
            # 1. Upload to Seaweed
            seaweed_id = SeaweedFSService.upload_file(file, file.name)
            
            if not seaweed_id:
                return Response(
                    {"error": "Failed to upload to SeaweedFS"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # 2. Save the document on the DB with the Seaweed reference
            doc = DocumentModel.objects.create(
                file_name=file.name,
                file_type=file_type,
                file_size=file.size,
                seaweed_file_id=seaweed_id
            )
            
            serializer = DocumentSerializer(doc)
            return Response(
                {
                    "status": "File uploaded successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        # If custom is set to true, return the preview of the file informations
        # Keep the file temporarily in the memory
        request.session['temp_file'] = {
            'name': file.name,
            'size': file.size,
            'content': file.read() # Save the content during the session
        }
        request.session.modified = True

        return Response({
            "file_preview": {
                "file_name": file.name,
                "file_type": file_type,
                "file_size": file.size,
                "mime_type": mime_type
            },
            "message": "File stored for customization. Call select_file_params with custom parameters"
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def get_file(self, request, pk=None):
        """
        Show the file from Seaweed by the ID
        """
        try:
            # 1. Search on DB
            doc = DocumentModel.objects.get(pk=pk)

            # 2. Recover the file from Seaweed with seaweed_file_id
            file_content = seaweed_service.get_file(doc.seaweed_file_id)

            if not file_content:
                return Response(
                    {"error": "Failed to retrieve file"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response({
                "file_name": doc.file_content,
                "file_type": doc.file_type
            })
            
        except DocumentModel.DoesNotExist:
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def select_file_params(self, request):
        """ 
        Confirm upload with custom params
        - file: (MultiPart)
        - file_name: custom name (optional)
        - file_type: custom type (opcional)
        """
        # Recover the temporary file from the session
        temp_file_data = request.session.get('temp_file')
        
        if not temp_file_data:
            return Response(
                {"error": "No temporary file found. send the custom param file first"},
                status=status.HTTP_400_BAD_REQUEST
            )

        custom_file_name = request.data.get('file_name', temp_file_data['name'])
        custom_file_type = request.data.get('file_type', temp_file_data['name'].split('.')[-1].lower())
        
        # Validate file_type
        valid_types = ['pdf', 'xlsx', 'csv']
        if custom_file_type not in valid_types:
            return Response(
                {"error": f"Invalid file_type. Must be one of: {valid_types}"}
            )
        
        # Create the file on DB
        doc = DocumentModel.objects.create(
            file_name=custom_file_name,
            file_type=custom_file_type,
            file_size=temp_file_data['size']
        )

        # Upload the file on Seaweed
        file_obj = BytesIO(temp_file_data['content'])
        
        seaweed_id = seaweed_service.upload_file(
            file_obj=file_obj,
            custom_file_name=custom_file_name,
            doc=str(doc.id)
        )
        
        if not seaweed_id:
            doc.delete()
            return Response(
                {"error": "Failed to upload to SeaweedFS"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Clean the temporary file from the session
        del request.session['temp_file']
        request.session.modified = True
        
        serializer = DocumentSerializer(doc)
        return Response(
            {
                "status": "File uploaded sucessfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
        
    @action(detail=True, methods=['delete'])
    def remove_file(self, request, pk=None):
        """ 
        Remove the file on Seaweed and the docs informations on DB
        """
        try:
            doc = DocumentModel.objects.get(pk=pk)
            
            seaweed_service.delete_file(str(doc.id))
            doc.delete()
            
            return Response(
                {"status": "File deleted successfully"},
                status=status.HTTP_204_NO_CONTENT
            )

        except DocumentModel.DoesNotExist:
            return Response(
                {"error": "Document not fiound"}
            )

    @action(detail=True, methods=['put'])
    def update_file(self, request, pk=None):
        """ 
        Update the file on the DB and keeping the same ID
        """
        try:
            doc = DocumentModel.objects.get(pk=pk)
            
            new_file = request.FILES.get('file')
            new_file_name = request.data.get('file_name')
            new_file_type = request.data.get('file_type')
            
            if not new_file and not new_file_name and not new_file_type:
                return Response(
                    {"error": "Must provide 'file', 'file_name' or 'file_type'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if new_file:
                seaweed_service.update_file(
                    str(doc.id),
                    new_file,
                    new_file_name or new_file.name
                )

                doc.file_type = new_file_type or new_file.name.split('.')[-1].lower()
                doc.file_size = new_file.size
                doc.file_name = new_file_name or new_file.name
            
            if new_file_name and not new_file:
                doc.file_name = new_file_name
            
            if new_file_type and not new_file:
                doc.file_type = new_file_type
            
            doc.save()
            
            serializer = DocumentSerializer(doc)
            return Response(
                {"status": "File updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        except DocumentModel.DoesNotExist:
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )