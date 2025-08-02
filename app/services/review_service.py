"""AI-powered product review service."""

import asyncio
import logging

import openai
from openai import AsyncOpenAI

from ..config import settings
from ..models import ReviewDecision, ReviewResponse
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for AI-powered product approval reviews."""

    def __init__(self):
        """Initialize the review service."""
        self.client = None
        if settings.openai_api_key and not settings.use_mock_ai:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def review_product(self, product_name: str, sales_page: str) -> ReviewResponse:
        """
        Review a product and return approval decision.

        Args:
            product_name: Name of the product
            sales_page: Sales page content to analyze

        Returns:
            ReviewResponse with decision and explanation

        Raises:
            Exception: If review fails
        """
        if settings.use_mock_ai or not self.client:
            return await self._mock_review(product_name, sales_page)

        try:
            # Create the review prompt
            prompt = self._create_review_prompt(product_name, sales_page)

            # Use OpenAI Responses API with structured output
            response = await asyncio.wait_for(
                self.client.responses.parse(
                    model=settings.openai_model,
                    input=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    text_format=ReviewResponse,
                ),
                timeout=settings.openai_timeout
            )

            # Return the parsed response directly
            return response.output_parsed

        except TimeoutError as e:
            logger.error("OpenAI API timeout")
            raise Exception("Review service timeout - please try again") from e
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception("AI service temporarily unavailable") from e
        except Exception as e:
            logger.error(f"Unexpected error in review service: {e}")
            raise Exception("Review service error - please try again") from e

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI model."""
        return SYSTEM_PROMPT

    def _create_review_prompt(self, product_name: str, sales_page: str) -> str:
        """Create the review prompt for the specific product."""
        return USER_PROMPT_TEMPLATE.format(
            product_name=product_name,
            sales_page=sales_page
        )

    async def _mock_review(self, product_name: str, sales_page: str) -> ReviewResponse:
        """Mock review service for testing when OpenAI is not available."""
        # Simple keyword-based mock logic
        content_lower = f"{product_name} {sales_page}".lower()

        # Check for obvious rejection patterns
        reject_keywords = [
            "guaranteed", "overnight", "100% guaranteed", "no risk",
            "lose 15kg", "turn €100 into €10,000", "miracle",
            "get rich quick", "secret formula", "doctors hate"
        ]

        for keyword in reject_keywords:
            if keyword in content_lower:
                return ReviewResponse(
                    decision=ReviewDecision.REJECT,
                    explanation=f"Product contains suspicious claims: '{keyword}' - requires manual review."
                )

        # Check for approval patterns
        approve_keywords = [
            "evidence-based", "research", "psychology", "behavioral science",
            "course", "education", "strategy", "methodology"
        ]

        for keyword in approve_keywords:
            if keyword in content_lower:
                return ReviewResponse(
                    decision=ReviewDecision.APPROVE,
                    explanation="Product appears educational and evidence-based."
                )

        # Default to requiring manual review
        return ReviewResponse(
            decision=ReviewDecision.REJECT,
            explanation="Product requires manual review to ensure compliance and quality standards."
        )
