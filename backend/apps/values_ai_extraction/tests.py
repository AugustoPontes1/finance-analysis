from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework.test import APIClient

from backend.apps.values_extraction.models import DocumentModel
from backend.apps.values_ai_extraction.llm.local import LocalLLMService, PROMPT


class LocalLLMServiceExtractTest(TestCase):

    def _make_service(self, url="http://localhost:11434/api/generate", model="llama3"):
        with patch.dict("os.environ", {"LLM_MODEL_URL": url, "LLM_MODEL_NAME": model}):
            return LocalLLMService()

    @patch("backend.apps.values_ai_extraction.llm.local.requests.post")
    def test_extract_returns_raw_llm_text(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": "The document contains an hourly rate of $30.00."},
        )
        service = self._make_service()
        result = service.extract("some document text")
        self.assertEqual(result, "The document contains an hourly rate of $30.00.")

    @patch("backend.apps.values_ai_extraction.llm.local.requests.post")
    def test_extract_sends_correct_payload(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": "summary"},
        )
        service = self._make_service(model="llama3")
        service.extract("doc text")
        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]["json"]
        self.assertEqual(payload["model"], "llama3")
        self.assertIn("doc text", payload["prompt"])
        self.assertFalse(payload["stream"])

    @patch("backend.apps.values_ai_extraction.llm.local.requests.post")
    def test_extract_returns_empty_string_on_empty_response(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": "   "},
        )
        service = self._make_service()
        result = service.extract("some text")
        self.assertEqual(result, [])

    @patch("backend.apps.values_ai_extraction.llm.local.requests.post")
    def test_extract_raises_on_http_error(self, mock_post):
        mock_post.return_value = MagicMock(status_code=500)
        mock_post.return_value.raise_for_status.side_effect = Exception("500 Server Error")
        service = self._make_service()
        with self.assertRaises(Exception):
            service.extract("some text")


class AnalyzeDocumentViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.doc = DocumentModel.objects.create(
            file_name="test.pdf",
            file_type="pdf",
            file_size=1000,
            seaweed_file_id="1,abc123",
        )

    @patch("backend.apps.values_ai_extraction.views.get_llm_service")
    @patch("backend.apps.values_ai_extraction.views.seaweed_service_inst.get_file")
    def test_analyze_returns_summary(self, mock_get_file, mock_get_llm):
        mock_get_file.return_value = b"Hourly rate: $30.00. Payment: biweekly."
        mock_llm = MagicMock()
        mock_llm.extract.return_value = "The document shows an hourly rate of $30.00 paid biweekly."
        mock_get_llm.return_value = mock_llm

        response = self.client.post(
            f"/values_ai_extraction/analyze_document/{self.doc.pk}/v1/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"], "The document shows an hourly rate of $30.00 paid biweekly.")

    @patch("backend.apps.values_ai_extraction.views.seaweed_service_inst.get_file")
    def test_analyze_returns_404_for_missing_doc(self, mock_get_file):
        response = self.client.post("/values_ai_extraction/analyze_document/99999/v1/")
        self.assertEqual(response.status_code, 404)

    @patch("backend.apps.values_ai_extraction.views.seaweed_service_inst.get_file")
    def test_analyze_returns_warning_for_empty_text(self, mock_get_file):
        mock_get_file.return_value = b"   "
        response = self.client.post(
            f"/values_ai_extraction/analyze_document/{self.doc.pk}/v1/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("warning", response.data)

    @patch("backend.apps.values_ai_extraction.views.seaweed_service_inst.get_file")
    def test_analyze_returns_500_when_file_not_found_in_seaweed(self, mock_get_file):
        mock_get_file.return_value = None
        response = self.client.post(
            f"/values_ai_extraction/analyze_document/{self.doc.pk}/v1/"
        )
        self.assertEqual(response.status_code, 500)
