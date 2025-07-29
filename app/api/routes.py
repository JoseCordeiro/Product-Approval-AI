"""API route handlers for the Product Approval AI application."""

import logging

from fastapi import APIRouter, HTTPException, Request

from ..config import settings
from ..models import ReviewRequest, ReviewResponse
from ..services.review_service import ReviewService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Product Approval AI",
        "version": "1.0.0",
        "mock_mode": settings.use_mock_ai
    }


@router.post(
    "/review",
    response_model=ReviewResponse,
    responses={
        200: {"description": "Product review completed successfully"},
        400: {"description": "Invalid request data"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
        503: {"description": "Service unavailable"},
        504: {"description": "Service timeout"},
    }
)
async def review_product(request: ReviewRequest, app_request: Request) -> ReviewResponse:
    """
    Review a product for approval.

    Analyzes the product name and sales page content using AI to determine
    if the product should be approved or rejected based on compliance,
    quality, and legal validity criteria.

    Args:
        request: ReviewRequest containing product_name and sales_page
        app_request: FastAPI request object to access app state

    Returns:
        ReviewResponse with decision ("approve" or "reject") and explanation

    Raises:
        HTTPException: If the review service fails
    """
    logger.info(f"Reviewing product: {request.product_name[:50]}...")

    # Additional validation for content length
    if len(request.sales_page) > settings.max_content_length:
        raise HTTPException(
            status_code=400,
            detail=f"Sales page content too long (max {settings.max_content_length} characters)"
        )

    try:
        # Get review service from app state
        review_service: ReviewService = app_request.app.state.review_service

        # Perform the review
        result = await review_service.review_product(
            product_name=request.product_name,
            sales_page=request.sales_page
        )

        logger.info(f"Review completed: {result.decision} - {request.product_name}")
        return result

    except Exception as e:
        logger.error(f"Review service error: {e}")

        # Check if it's a timeout or service unavailable error
        error_msg = str(e).lower()
        if "timeout" in error_msg:
            raise HTTPException(status_code=504, detail=str(e)) from e
        elif "unavailable" in error_msg:
            raise HTTPException(status_code=503, detail=str(e)) from e
        else:
            raise HTTPException(status_code=500, detail="Review service error") from e
