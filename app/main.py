"""Main FastAPI application for Product Approval AI."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .api.routes import router
from .config import settings
from .models import ErrorResponse
from .services.review_service import ReviewService

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Product Approval AI service...")

    # Initialize services
    app.state.review_service = ReviewService()

    # Log configuration
    logger.info(f"Using mock AI: {settings.use_mock_ai}")
    logger.info(f"Debug mode: {settings.debug}")

    yield

    logger.info("Shutting down Product Approval AI service...")


# Create FastAPI app
app = FastAPI(
    title="Product Approval AI",
    description="AI-powered product review service for digital sales platforms",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routes
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation Error",
            detail="; ".join(errors)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred"
        ).model_dump()
    )
