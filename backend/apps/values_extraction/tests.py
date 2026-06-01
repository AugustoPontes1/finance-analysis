from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from .models import DocumentModel


class DocumentExtractionAPITest(APITestCase):
    """ 
    Tests for the flow of DocumentExtractionAPIView
    """

    def setUp(self):
        """
        Innitial setup for each test
        """
        self.test_file_content = b"Test file content"
        self.test_file = SimpleUploadedFile(
            name='test_document.xlsx',
            content=self.test_file_content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    def tearDown(self):
        """
        Cleanup after each test
        """
        DocumentModel.objects.all().delete()


    # ========== TESTS: send_file (DIRECT UPLOAD) ==========
    
    @patch('apps.values_extraction.views.seaweed_service.upload_file')
    def test_send_file_direct_upload_success(self, mock_upload):
        """
        Tests direct upload with automatic parameters
        POST /values_extraction/upload_file/v1/
        """
        mock_upload.return_value = "1"  # Simulates file_id return

        with open('test_file.xlsx', 'wb') as f:
            f.write(self.test_file_content)

        with open('test_file.xlsx', 'rb') as f:
            response = self.client.post(
                '/values_extraction/upload_file/v1/',
                {'file': f},
                format='multipart'
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'File uploaded successfully')
        self.assertIn('data', response.data)
        self.assertEqual(DocumentModel.objects.count(), 1)
    
    def test_send_file_no_file_provided(self):
        """
        Tests error when no file is provided
        """
        response = self.client.post(
            '/values_extraction/upload_file/v1/',
            {},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('apps.values_extraction.views.seaweed_service.upload_file')
    def test_send_file_custom_true_returns_preview(self, mock_upload):
        """
        Tests upload with custom=true (returns preview)
        POST /values_extraction/upload_file/v1/?custom=true
        """
        with open('test_file.xlsx', 'rb') as f:
            response = self.client.post(
                '/values_extraction/upload_file/v1/?custom=true',
                {'file': f},
                format='multipart'
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('file_preview', response.data)
        self.assertEqual(response.data['file_preview']['file_name'], 'test_file.xlsx')
        self.assertEqual(response.data['file_preview']['file_type'], 'xlsx')
        self.assertIn('file_size', response.data['file_preview'])
    
    @patch('apps.values_extraction.views.seaweed_service.upload_file')
    def test_send_file_seaweed_upload_fails(self, mock_upload):
        """
        Tests error when SeaweedFS upload fails
        """
        mock_upload.return_value = None  # Simulates failure

        with open('test_file.xlsx', 'rb') as f:
            response = self.client.post(
                '/values_extraction/upload_file/v1/',
                {'file': f},
                format='multipart'
            )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        self.assertEqual(DocumentModel.objects.count(), 0)  # Should not create document

    # ========== TESTS: select_file_params (CONFIRMATION WITH CUSTOMIZATION) ==========
    
    @patch('apps.values_extraction.views.seaweed_service.upload_file')
    def test_select_file_params_with_default_values(self, mock_upload):
        """
        Tests confirmation with default detected parameters
        """
        mock_upload.return_value = "1"

        # First calls send_file with custom=true
        with open('test_file.xlsx', 'rb') as f:
            self.client.post(
                '/values_extraction/upload_file/v1/?custom=true',
                {'file': f},
                format='multipart'
            )

        # Then confirms without changes
        response = self.client.post(
            '/values_extraction/select_file_params/v1/'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DocumentModel.objects.count(), 1)
        doc = DocumentModel.objects.first()
        self.assertEqual(doc.file_type, 'xlsx')
    
    @patch('apps.values_extraction.views.seaweed_service.upload_file')
    def test_select_file_params_with_custom_values(self, mock_upload):
        """
        Tests confirmation with custom parameters
        """
        mock_upload.return_value = "1"

        # First calls send_file with custom=true
        with open('test_file.xlsx', 'rb') as f:
            self.client.post(
                '/values_extraction/upload_file/v1/?custom=true',
                {'file': f},
                format='multipart'
            )

        # Then confirms with custom values
        response = self.client.post(
            '/values_extraction/select_file_params/v1/',
            {
                'file_name': 'Custom Report Q1',
                'file_type': 'xlsx'
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doc = DocumentModel.objects.first()
        self.assertEqual(doc.file_name, 'Custom Report Q1')
        self.assertEqual(doc.file_type, 'xlsx')
    
    def test_select_file_params_no_temporary_file(self):
        """
        Tests error when no temporary file is stored
        """
        response = self.client.post(
            '/values_extraction/select_file_params/v1/',
            {'file_name': 'Report'}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('apps.values_extraction.views.seaweed_service.upload_file')
    def test_select_file_params_invalid_file_type(self, mock_upload):
        """
        Tests error with invalid file_type
        """
        with open('test_file.xlsx', 'rb') as f:
            self.client.post(
                '/values_extraction/upload_file/v1/?custom=true',
                {'file': f},
                format='multipart'
            )

        response = self.client.post(
            '/values_extraction/select_file_params/v1/',
            {'file_type': 'invalid_type'}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid file_type', response.data['error'])

    # ========== TESTS: analyze_file (ANALYSIS) ==========
    
    @patch('apps.values_extraction.views.seaweed_service.get_file')
    def test_analyze_file_success(self, mock_get):
        """
        Tests analysis of existing file
        GET /values_extraction/get_file/v1/{id}/
        """
        mock_get.return_value = self.test_file_content

        # Creates a test document
        doc = DocumentModel.objects.create(
            file_name='test.xlsx',
            file_type='xlsx',
            file_size=100
        )

        response = self.client.get(
            f'/values_extraction/get_file/v1/{doc.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['file_name'], 'test.xlsx')
        self.assertEqual(response.data['file_type'], 'xlsx')
    
    def test_analyze_file_not_found(self):
        """
        Tests error when analyzing non-existent file
        """
        response = self.client.get(
            '/values_extraction/get_file/v1/999/'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('apps.values_extraction.views.seaweed_service.get_file')
    def test_analyze_file_seaweed_error(self, mock_get):
        """
        Tests error when SeaweedFS fails
        """
        mock_get.return_value = None

        doc = DocumentModel.objects.create(
            file_name='test.xlsx',
            file_type='xlsx',
            file_size=100
        )

        response = self.client.get(
            f'/values_extraction/get_file/v1/{doc.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ========== TESTS: change_file (UPDATE) ==========
    
    @patch('apps.values_extraction.views.seaweed_service.update_file')
    def test_change_file_with_new_file(self, mock_update):
        """
        Tests update with new file
        PUT /values_extraction/update_file/v1/{id}/
        """
        mock_update.return_value = "1"

        doc = DocumentModel.objects.create(
            file_name='old.xlsx',
            file_type='xlsx',
            file_size=100
        )

        new_file = SimpleUploadedFile(
            name='new_document.xlsx',
            content=b"New content",
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        response = self.client.put(
            f'/values_extraction/update_file/v1/{doc.id}/',
            {'file': new_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doc.refresh_from_db()
        self.assertEqual(doc.file_name, 'new_document.xlsx')
    
    def test_change_file_rename_only(self):
        """
        Tests update of file name only
        """
        doc = DocumentModel.objects.create(
            file_name='old.xlsx',
            file_type='xlsx',
            file_size=100
        )

        response = self.client.put(
            f'/values_extraction/update_file/v1/{doc.id}/',
            {'file_name': 'renamed.xlsx'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doc.refresh_from_db()
        self.assertEqual(doc.file_name, 'renamed.xlsx')
    
    def test_change_file_no_parameters(self):
        """
        Tests error when no parameters are provided
        """
        doc = DocumentModel.objects.create(
            file_name='test.xlsx',
            file_type='xlsx',
            file_size=100
        )

        response = self.client.put(
            f'/values_extraction/update_file/v1/{doc.id}/',
            {}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_file_not_found(self):
        """
        Tests error when updating non-existent document
        """
        response = self.client.put(
            '/values_extraction/update_file/v1/999/',
            {'file_name': 'new_name.xlsx'}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ========== TESTS: remove_file (DELETION) ==========
    
    @patch('apps.values_extraction.views.seaweed_service.delete_file')
    def test_remove_file_success(self, mock_delete):
        """
        Tests deletion of existing file
        DELETE /values_extraction/remove_file/v1/{id}/
        """
        mock_delete.return_value = True

        doc = DocumentModel.objects.create(
            file_name='test.xlsx',
            file_type='xlsx',
            file_size=100
        )
        doc_id = doc.id

        response = self.client.delete(
            f'/values_extraction/remove_file/v1/{doc_id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DocumentModel.objects.count(), 0)
    
    def test_remove_file_not_found(self):
        """
        Tests error when deleting non-existent file
        """
        response = self.client.delete(
            '/values_extraction/remove_file/v1/999/'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('apps.values_extraction.views.seaweed_service.delete_file')
    def test_remove_file_seaweed_error(self, mock_delete):
        """
        Tests if it removes from DB even if SeaweedFS fails
        """
        mock_delete.return_value = False

        doc = DocumentModel.objects.create(
            file_name='test.xlsx',
            file_type='xlsx',
            file_size=100
        )

        response = self.client.delete(
            f'/values_extraction/remove_file/v1/{doc.id}/'
        )

        # Should still return success and remove from DB
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DocumentModel.objects.count(), 0)
