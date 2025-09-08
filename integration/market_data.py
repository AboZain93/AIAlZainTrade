"""
Market Data Integration
Connects to external market data providers
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class MarketDataProvider:
    """Base class for market data providers"""
    
    async def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for symbol"""
        raise NotImplementedError
    
    async def get_historical_data(self, symbol: str, timeframe: str, limit: int) -> List[Dict]:
        """Get historical price data"""
        raise NotImplementedError
    
    async def get_market_status(self) -> Dict[str, Any]:
        """Get market status"""
        raise NotImplementedError

class AlphaVantageProvider(MarketDataProvider):
    """Alpha Vantage market data provider"""
    
    def __init__(self):
        self.api_key = settings.alpha_vantage_api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.session = None
    
    async def _get_session(self):
        """Get aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price from Alpha Vantage"""
        try:
            if not self.api_key:
                return await self._mock_current_price(symbol)
            
            session = await self._get_session()
            
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            async with session.get(self.base_url, params=params) as response:
                data = await response.json()
                
                if "Global Quote" in data:
                    quote = data["Global Quote"]
                    return {
                        "symbol": symbol,
                        "price": float(quote.get("05. price", 0)),
                        "change": float(quote.get("09. change", 0)),
                        "change_percent": quote.get("10. change percent", "0%"),
                        "timestamp": datetime.now().isoformat(),
                        "source": "alphavantage"
                    }
                else:
                    logger.warning(f"Unexpected Alpha Vantage response: {data}")
                    return await self._mock_current_price(symbol)
                    
        except Exception as e:
            logger.error(f"Alpha Vantage API error: {e}")
            return await self._mock_current_price(symbol)
    
    async def get_historical_data(self, symbol: str, timeframe: str = "daily", limit: int = 100) -> List[Dict]:
        """Get historical data from Alpha Vantage"""
        try:
            if not self.api_key:
                return await self._mock_historical_data(symbol, limit)
            
            session = await self._get_session()
            
            # Map timeframe to Alpha Vantage function
            function_map = {
                "1min": "TIME_SERIES_INTRADAY",
                "5min": "TIME_SERIES_INTRADAY", 
                "15min": "TIME_SERIES_INTRADAY",
                "30min": "TIME_SERIES_INTRADAY",
                "60min": "TIME_SERIES_INTRADAY",
                "daily": "TIME_SERIES_DAILY",
                "weekly": "TIME_SERIES_WEEKLY",
                "monthly": "TIME_SERIES_MONTHLY"
            }
            
            function = function_map.get(timeframe, "TIME_SERIES_DAILY")
            
            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            # Add interval for intraday data
            if "INTRADAY" in function:
                params["interval"] = timeframe
            
            async with session.get(self.base_url, params=params) as response:
                data = await response.json()
                
                # Extract time series data
                time_series_key = None
                for key in data.keys():
                    if "Time Series" in key:
                        time_series_key = key
                        break
                
                if time_series_key and time_series_key in data:
                    time_series = data[time_series_key]
                    
                    historical_data = []
                    for timestamp, values in list(time_series.items())[:limit]:
                        historical_data.append({
                            "timestamp": timestamp,
                            "open": float(values.get("1. open", 0)),
                            "high": float(values.get("2. high", 0)),
                            "low": float(values.get("3. low", 0)),
                            "close": float(values.get("4. close", 0)),
                            "volume": int(values.get("5. volume", 0))
                        })
                    
                    return historical_data
                else:
                    logger.warning(f"No time series data in Alpha Vantage response")
                    return await self._mock_historical_data(symbol, limit)
                    
        except Exception as e:
            logger.error(f"Alpha Vantage historical data error: {e}")
            return await self._mock_historical_data(symbol, limit)
    
    async def _mock_current_price(self, symbol: str) -> Dict[str, Any]:
        """Mock current price data"""
        base_price = 1.1000 if "USD" in symbol else 50000.0
        return {
            "symbol": symbol,
            "price": base_price,
            "change": 0.01,
            "change_percent": "+0.09%",
            "timestamp": datetime.now().isoformat(),
            "source": "mock"
        }
    
    async def _mock_historical_data(self, symbol: str, limit: int) -> List[Dict]:
        """Mock historical data"""
        data = []
        base_price = 1.1000 if "USD" in symbol else 50000.0
        
        for i in range(limit):
            timestamp = datetime.now() - timedelta(days=i)
            price = base_price * (1 + (i * 0.001))
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "open": price * 0.999,
                "high": price * 1.002,
                "low": price * 0.998,
                "close": price,
                "volume": 100000
            })
        
        return data

class FinnhubProvider(MarketDataProvider):
    """Finnhub market data provider"""
    
    def __init__(self):
        self.api_key = settings.finnhub_api_key
        self.base_url = "https://finnhub.io/api/v1"
        self.session = None
    
    async def _get_session(self):
        """Get aiohttp session"""
        if not self.session:
            headers = {"X-Finnhub-Token": self.api_key} if self.api_key else {}
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price from Finnhub"""
        try:
            if not self.api_key:
                return await self._mock_current_price(symbol)
            
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/quote", params={"symbol": symbol}) as response:
                data = await response.json()
                
                return {
                    "symbol": symbol,
                    "price": data.get("c", 0),  # Current price
                    "change": data.get("d", 0),  # Change
                    "change_percent": data.get("dp", 0),  # Change percent
                    "high": data.get("h", 0),  # High price of the day
                    "low": data.get("l", 0),  # Low price of the day
                    "open": data.get("o", 0),  # Open price of the day
                    "previous_close": data.get("pc", 0),  # Previous close price
                    "timestamp": datetime.now().isoformat(),
                    "source": "finnhub"
                }
                
        except Exception as e:
            logger.error(f"Finnhub API error: {e}")
            return await self._mock_current_price(symbol)
    
    async def _mock_current_price(self, symbol: str) -> Dict[str, Any]:
        """Mock current price for Finnhub"""
        return {
            "symbol": symbol,
            "price": 100.0,
            "change": 1.5,
            "change_percent": 1.52,
            "high": 101.0,
            "low": 98.5,
            "open": 99.0,
            "previous_close": 98.5,
            "timestamp": datetime.now().isoformat(),
            "source": "mock"
        }

class MarketDataManager:
    """Manages multiple market data providers"""
    
    def __init__(self):
        self.providers = {
            "alphavantage": AlphaVantageProvider(),
            "finnhub": FinnhubProvider()
        }
        self.primary_provider = "alphavantage"
    
    async def get_current_price(self, symbol: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get current price with fallback providers"""
        provider_name = provider or self.primary_provider
        
        try:
            if provider_name in self.providers:
                return await self.providers[provider_name].get_current_price(symbol)
            else:
                # Fallback to primary provider
                return await self.providers[self.primary_provider].get_current_price(symbol)
                
        except Exception as e:
            logger.error(f"Failed to get price from {provider_name}: {e}")
            
            # Try alternative providers
            for name, provider_instance in self.providers.items():
                if name != provider_name:
                    try:
                        return await provider_instance.get_current_price(symbol)
                    except Exception as fallback_error:
                        logger.error(f"Fallback provider {name} failed: {fallback_error}")
            
            # If all fail, return mock data
            return {
                "symbol": symbol,
                "price": 1.0000,
                "change": 0.0,
                "change_percent": "0%",
                "timestamp": datetime.now().isoformat(),
                "source": "fallback",
                "error": "All providers failed"
            }
    
    async def get_historical_data(self, symbol: str, timeframe: str = "daily", 
                                limit: int = 100, provider: Optional[str] = None) -> List[Dict]:
        """Get historical data with fallback"""
        provider_name = provider or self.primary_provider
        
        try:
            if provider_name in self.providers:
                return await self.providers[provider_name].get_historical_data(symbol, timeframe, limit)
            else:
                return await self.providers[self.primary_provider].get_historical_data(symbol, timeframe, limit)
                
        except Exception as e:
            logger.error(f"Failed to get historical data from {provider_name}: {e}")
            
            # Try alternative providers
            for name, provider_instance in self.providers.items():
                if name != provider_name:
                    try:
                        return await provider_instance.get_historical_data(symbol, timeframe, limit)
                    except Exception:
                        continue
            
            # Return empty list if all fail
            return []
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get prices for multiple symbols"""
        results = {}
        
        # Use asyncio.gather for concurrent requests
        tasks = [self.get_current_price(symbol) for symbol in symbols]
        
        try:
            price_data = await asyncio.gather(*tasks, return_exceptions=True)
            
            for symbol, data in zip(symbols, price_data):
                if isinstance(data, Exception):
                    logger.error(f"Failed to get price for {symbol}: {data}")
                    results[symbol] = {"error": str(data)}
                else:
                    results[symbol] = data
                    
        except Exception as e:
            logger.error(f"Batch price request failed: {e}")
            
        return results
    
    async def close_sessions(self):
        """Close all provider sessions"""
        for provider in self.providers.values():
            if hasattr(provider, 'session') and provider.session:
                await provider.session.close()

# Global instance
market_data = MarketDataManager()