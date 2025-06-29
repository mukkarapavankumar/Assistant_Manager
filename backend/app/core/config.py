"""Configuration management for Assistant Manager."""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Assistant Manager"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///assistant_manager.db"
    
    # LLM Configuration
    ollama_host: str = "http://localhost:11434"
    default_model: str = "llama3.2"
    
    # Email Configuration
    outlook_enabled: bool = True
    email_check_interval: int = 300  # 5 minutes
    
    # GitHub Configuration
    github_token: Optional[str] = None
    github_repo: Optional[str] = None
    github_pages_branch: str = "gh-pages"
    
    # Scheduling
    update_frequency: str = "weekly"  # daily, weekly, biweekly
    reminder_days: int = 2
    max_follow_ups: int = 3
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "assistant_manager.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()