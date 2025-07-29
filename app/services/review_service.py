"""AI-powered product review service."""

import asyncio
import json
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

            # Call OpenAI API with timeout
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,  # Low temperature for consistent decisions
                    max_tokens=150,   # Limit response length
                ),
                timeout=settings.openai_timeout
            )

            # Parse the response
            content = response.choices[0].message.content.strip()
            return self._parse_ai_response(content)

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

    def _parse_ai_response(self, content: str) -> ReviewResponse:
        """Parse AI response into ReviewResponse model."""
        try:
            # Try to parse as JSON first
            if content.startswith("{") and content.endswith("}"):
                data = json.loads(content)
                decision = data.get("decision", "").lower()
                explanation = data.get("explanation", "")
            else:
                # Fallback parsing for non-JSON responses
                lines = content.lower().split('\n')
                decision = "reject"  # Default to reject for safety
                explanation = content

                for line in lines:
                    if "approve" in line and "reject" not in line:
                        decision = "approve"
                        break
                    elif "reject" in line:
                        decision = "reject"
                        break

            # Validate decision
            if decision not in ["approve", "reject"]:
                decision = "reject"
                explanation = "Unable to determine approval status - rejected for safety"

            # Ensure explanation is reasonable length
            if len(explanation) > 500:  # characters
                explanation = explanation[:497] + "..."
            elif len(explanation) < 10:  # characters
                explanation = f"Product {decision}d based on content analysis."

            return ReviewResponse(
                decision=ReviewDecision.APPROVE if decision == "approve" else ReviewDecision.REJECT,
                explanation=explanation
            )

        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return ReviewResponse(
                decision=ReviewDecision.REJECT,
                explanation="Unable to process review - rejected for safety"
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
