from rest_framework import serializers
from backend.apps.values_extraction.models import DocumentModel


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentModel
        fields = ['id', 'file_name', 'file_type', 'file_size', 'file_content']
