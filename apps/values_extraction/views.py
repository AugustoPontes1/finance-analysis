from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet

from decimal import Decimal

from serializers import DocumentSerializer
from models import DocumentModel
from seaweed_service.seaweed_service import SeaweedFSService


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
            file_type=file.name.split('.')[-1].lower(),
            file_size=file.size,
            seaweed_file_id=seaweed_id
        )
        
        serializer = DocumentSerializer(doc)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def analyze_file(self, request):
        ...

    @action(methods=['post'])
    def select_file_params(
        file_name: str, 
        file_type: str, 
        file_size: Decimal, 
        file_content: str
    ):
        ...

    @action(methods=['delete'])
    def remove_file(self, request):
        ...

    @action(methods=['put'])
    def change_file(self, request):
        ...
