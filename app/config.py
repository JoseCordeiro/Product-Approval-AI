"""Configuration settings for the Product Approval API."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key"
    )
    openai_model: str = Field(
        default="gpt-4.1",
        description="OpenAI model to use for reviews"
    )
    openai_timeout: int = Field(
        default=30,
        description="OpenAI API timeout in seconds"
    )

    # Application Configuration
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    max_content_length: int = Field(
        default=10000,
        description="Maximum sales page content length"
    )
    use_mock_ai: bool = Field(
        default=False,
        description="Use mock AI service instead of OpenAI (for testing)"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()
