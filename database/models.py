"""
Database Models for AIAlZainTrade
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

from .connection import Base

class UserModel(Base):
    """User model for storing user information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    telegram_id = Column(Integer, unique=True, index=True, nullable=True)
    telegram_username = Column(String(50), nullable=True)
    
    # Account settings
    is_active = Column(Boolean, default=True)
    trading_enabled = Column(Boolean, default=False)
    demo_mode = Column(Boolean, default=True)
    
    # Preferences
    default_currency = Column(String(10), default="USD")
    risk_level = Column(String(20), default="medium")  # low, medium, high
    max_position_size = Column(Float, default=1000.0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    trades = relationship("TradeModel", back_populates="user")
    settings = relationship("SettingsModel", back_populates="user")

class TradeModel(Base):
    """Trade model for storing trading transactions"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Trade details
    trade_id = Column(String(50), unique=True, index=True, nullable=False)
    symbol = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)  # buy, sell
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
    # Order details
    order_type = Column(String(20), default="market")  # market, limit, stop
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    
    # Status and results
    status = Column(String(20), default="pending")  # pending, executed, cancelled, failed
    profit_loss = Column(Float, default=0.0)
    fees = Column(Float, default=0.0)
    
    # Metadata
    strategy_used = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    executed_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="trades")

class SignalModel(Base):
    """AI trading signals model"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Signal details
    symbol = Column(String(20), nullable=False, index=True)
    signal_type = Column(String(10), nullable=False)  # buy, sell, hold
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Price predictions
    current_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=True)
    stop_loss_price = Column(Float, nullable=True)
    
    # Analysis data
    technical_score = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    volume_score = Column(Float, nullable=True)
    
    # Metadata
    timeframe = Column(String(10), default="1h")  # 1m, 5m, 15m, 1h, 4h, 1d
    strategy = Column(String(50), nullable=True)
    model_version = Column(String(20), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_executed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)

class SettingsModel(Base):
    """User settings and preferences"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Trading settings
    auto_trading = Column(Boolean, default=False)
    risk_per_trade = Column(Float, default=0.02)  # 2% of account
    max_daily_trades = Column(Integer, default=10)
    min_confidence_threshold = Column(Float, default=0.7)
    
    # Notification settings
    telegram_notifications = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=False)
    notify_on_signals = Column(Boolean, default=True)
    notify_on_trades = Column(Boolean, default=True)
    
    # API configurations (encrypted in production)
    broker_api_key = Column(Text, nullable=True)
    broker_api_secret = Column(Text, nullable=True)
    broker_name = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("UserModel", back_populates="settings")

class MarketDataModel(Base):
    """Market data cache model"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Data identification
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # OHLCV data
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # Additional metrics
    sma_20 = Column(Float, nullable=True)
    sma_50 = Column(Float, nullable=True)
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    
    # Metadata
    data_source = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())

# Helper functions for models
def create_all_tables():
    """Create all database tables"""
    from .connection import engine
    Base.metadata.create_all(bind=engine)

def drop_all_tables():
    """Drop all database tables (use with caution!)"""
    from .connection import engine
    Base.metadata.drop_all(bind=engine)