"""
Tests for OCR pipeline: ocr_service and ai_parser.

Uses mocks for Tesseract and DeepSeek API calls.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import date

from app.services.ocr_service import ocr_image
from app.services.ai_parser import parse_debt_from_text


def _reset_ai_parser_client():
    import app.services.ai_parser as ap
    ap._http_client = None


class TestOcrService:
    """Tests for ocr_service.ocr_image."""

    @patch("app.services.ocr_service.pytesseract")
    @patch("app.services.ocr_service.Image")
    async def test_ocr_image_returns_text(self, mock_image, mock_pytesseract):
        mock_pytesseract.image_to_string.return_value = "Rincian Pinjaman\nRp500,000\n"
        result = await ocr_image("/fake/path.jpg")
        assert "Rincian Pinjaman" in result
        assert "Rp500,000" in result

    @patch("app.services.ocr_service.pytesseract")
    @patch("app.services.ocr_service.Image")
    async def test_ocr_image_returns_empty(self, mock_image, mock_pytesseract):
        mock_pytesseract.image_to_string.return_value = ""
        result = await ocr_image("/fake/path.jpg")
        assert result == ""

    @patch("app.services.ocr_service.pytesseract")
    @patch("app.services.ocr_service.Image")
    async def test_ocr_image_strips_whitespace(self, mock_image, mock_pytesseract):
        mock_pytesseract.image_to_string.return_value = "  text with spaces  \n"
        result = await ocr_image("/fake/path.jpg")
        assert result == "text with spaces"
        assert result == result.strip()


class TestAiParser:
    """Tests for ai_parser.parse_debt_from_text.

    Mocks the HTTPX call to DeepSeek API.
    """

    def setup_method(self):
        _reset_ai_parser_client()

    async def _mock_deepseek_response(self, content: str):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": content}}]
        }
        return mock_response

    @patch("app.services.ai_parser.httpx.AsyncClient")
    async def test_parse_valid_text(self, mock_client_class):
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.post.return_value = await self._mock_deepseek_response(
            '{"platform": "Kredivo", "amount": 350000, "due_date": "2026-07-15", "installment_current": 3, "installment_total": 12, "interest_rate": 2.5, "interest_type": "monthly", "category": "paylater", "notes": null}'
        )

        result = await parse_debt_from_text("some text with Kredivo info")
        assert result["platform"] == "Kredivo"
        assert result["amount"] == 350000
        assert result["due_date"] == "2026-07-15"
        assert result["installment_current"] == 3
        assert result["installment_total"] == 12
        assert result["interest_rate"] == 2.5
        assert result["interest_type"] == "monthly"
        assert result["category"] == "paylater"

    @patch("app.services.ai_parser.httpx.AsyncClient")
    async def test_parse_unknown_platform(self, mock_client_class):
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.post.return_value = await self._mock_deepseek_response(
            '{"platform": "Tidak Diketahui", "amount": null, "due_date": null, "installment_current": null, "installment_total": null, "interest_rate": null, "interest_type": null, "category": null, "notes": null}'
        )

        result = await parse_debt_from_text("unrecognizable text")
        assert result["platform"] is None
        assert result["amount"] is None

    @patch("app.services.ai_parser.httpx.AsyncClient")
    async def test_parse_handles_indonesian_format(self, mock_client_class):
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.post.return_value = await self._mock_deepseek_response(
            '{"platform": "Akulaku", "amount": "Rp1.000.000", "due_date": "2026-08-01", "installment_current": null, "installment_total": null, "interest_rate": null, "interest_type": null, "category": null, "notes": null}'
        )

        result = await parse_debt_from_text("Akulaku Rp1.000.000")
        assert result["platform"] == "Akulaku"
        assert result["amount"] == 1000000

    @patch("app.services.ai_parser.httpx.AsyncClient")
    async def test_parse_fallback_due_date(self, mock_client_class):
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.post.return_value = await self._mock_deepseek_response(
            '{"platform": "GoPay Later", "amount": 75000, "due_date": null, "installment_current": null, "installment_total": null, "interest_rate": null, "interest_type": null, "category": null, "notes": null}'
        )

        result = await parse_debt_from_text("GoPay Later 75000")
        assert result["due_date"] == str(date.today())

    @patch("app.services.ai_parser.httpx.AsyncClient")
    async def test_parse_invalid_json_in_codeblock(self, mock_client_class):
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.post.return_value = await self._mock_deepseek_response(
            "```json\n{\"platform\": \"FIF\", \"amount\": 500000, \"due_date\": \"2026-09-01\"}\n```"
        )

        result = await parse_debt_from_text("some fif text")
        assert result["platform"] == "FIF"
        assert result["amount"] == 500000
        assert result["due_date"] == "2026-09-01"
