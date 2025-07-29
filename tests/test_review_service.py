"""Unit tests for the review service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import settings
from app.models import ReviewDecision
from app.services.review_service import ReviewService


class TestReviewService:
    """Test cases for ReviewService."""

    @pytest.mark.asyncio
    async def test_mock_review_reject_suspicious_claims(self, review_service):
        """Test mock review rejects products with suspicious claims."""
        # Test various suspicious keywords
        test_cases = [
            ("Lose Weight Fast", "Lose 15kg in 21 days! 100% guaranteed results!"),
            ("Crypto Bot", "Turn €100 into €10,000 overnight with no risk!"),
        ]

        for product_name, sales_page in test_cases:
            result = await review_service._mock_review(product_name, sales_page)
            assert result.decision == ReviewDecision.REJECT
            assert "suspicious claims" in result.explanation.lower()

    @pytest.mark.asyncio
    async def test_mock_review_approve_legitimate_products(self, review_service):
        """Test mock review approves legitimate educational products."""
        test_cases = [
            ("Study Course", "Evidence-based strategies backed by psychology research."),
            ("Skills Training", "Educational methodology for behavioral science applications."),
        ]

        for product_name, sales_page in test_cases:
            result = await review_service._mock_review(product_name, sales_page)
            assert result.decision == ReviewDecision.APPROVE
            assert "educational" in result.explanation.lower()

    @pytest.mark.asyncio
    @patch('app.services.review_service.AsyncOpenAI')
    async def test_openai_integration_success(self, mock_openai_class):
        """Test successful OpenAI API integration."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"decision": "approve", "explanation": "Product is educational and well-structured."}'

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        # Test with OpenAI enabled
        with patch.object(settings, 'use_mock_ai', False), \
             patch.object(settings, 'openai_api_key', 'test-key'):
            service = ReviewService()
            service.client = mock_client

            result = await service.review_product(
                "Educational Course",
                "Evidence-based learning strategies for students."
            )

            assert result.decision == ReviewDecision.APPROVE
            assert "educational" in result.explanation.lower()
            mock_client.chat.completions.create.assert_called_once()
