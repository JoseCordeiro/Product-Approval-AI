"""Pydantic models for the Product Approval API."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ReviewDecision(str, Enum):
    """Possible review decisions."""
    APPROVE = "approve"
    REJECT = "reject"


class ReviewRequest(BaseModel):
    """Request model for product review."""
    product_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the product to review"
    )
    sales_page: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="Sales page content to analyze"
    )

    @field_validator("product_name")
    def validate_product_name(cls, v):  # noqa: N805
        """Validate product name is not just whitespace."""
        if not v.strip():
            raise ValueError("Product name cannot be empty or just whitespace")
        return v.strip()

    @field_validator("sales_page")
    def validate_sales_page(cls, v):  # noqa: N805
        """Validate sales page content is meaningful."""
        if not v.strip():
            raise ValueError("Sales page content cannot be empty or just whitespace")
        return v.strip()


class ReviewResponse(BaseModel):
    """Response model for product review."""
    decision: ReviewDecision = Field(
        ...,
        description="Approval decision: approve or reject"
    )
    explanation: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="1-3 sentence explanation of the decision"
    )


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
