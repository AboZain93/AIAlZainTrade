"""
Application Configuration Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from datetime import datetime
import os
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "AIAlZainTrade"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database
    database_url: str = Field(default="sqlite:///./ai_trade.db", env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Telegram Bot
    telegram_bot_token: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_url: Optional[str] = Field(default=None, env="TELEGRAM_WEBHOOK_URL")
    telegram_webhook_path: str = Field(default="/api/v1/telegram/webhook", env="TELEGRAM_WEBHOOK_PATH")
    
    # Trading
    trading_mode: str = Field(default="demo", env="TRADING_MODE")  # demo, live
    default_currency: str = Field(default="USD", env="DEFAULT_CURRENCY")
    max_position_size: float = Field(default=1000.0, env="MAX_POSITION_SIZE")
    
    # AI/ML
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    model_refresh_interval: int = Field(default=3600, env="MODEL_REFRESH_INTERVAL")  # seconds
    
    # External APIs
    alpha_vantage_api_key: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_API_KEY")
    finnhub_api_key: Optional[str] = Field(default=None, env="FINNHUB_API_KEY")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Redis (for caching)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="ai_trade.log", env="LOG_FILE")
    
    # CORS
    allowed_origins: list = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.debug
    
    def get_database_url(self) -> str:
        """Get formatted database URL"""
        return self.database_url
    
    def get_telegram_webhook_url(self) -> Optional[str]:
        """Get full Telegram webhook URL"""
        if self.telegram_webhook_url:
            return f"{self.telegram_webhook_url.rstrip('/')}{self.telegram_webhook_path}"
        return None

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Environment variables template
ENV_TEMPLATE = """
# AIAlZainTrade Environment Configuration

# Application Settings
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./ai_trade.db
DATABASE_ECHO=false

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com

# Trading Configuration
TRADING_MODE=demo
DEFAULT_CURRENCY=USD
MAX_POSITION_SIZE=1000.0

# AI/ML APIs
OPENAI_API_KEY=your_openai_api_key_here
MODEL_REFRESH_INTERVAL=3600

# External Data APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FINNHUB_API_KEY=your_finnhub_key_here

# Security
SECRET_KEY=your_secret_key_here_change_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Caching
REDIS_URL=redis://localhost:6379

# CORS (comma-separated origins)
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
"""

def create_env_file():
    """Create .env file template if it doesn't exist"""
    env_path = ".env"
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write(ENV_TEMPLATE)
        print(f"Created {env_path} template file. Please update with your actual values.")