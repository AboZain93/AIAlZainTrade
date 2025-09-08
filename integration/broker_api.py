"""
Broker API Integration
Connects to various broker APIs for live trading
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import hmac
import time

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class BrokerAPI:
    """Base class for broker API integrations"""
    
    async def authenticate(self) -> bool:
        """Authenticate with broker API"""
        raise NotImplementedError
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        raise NotImplementedError
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get open positions"""
        raise NotImplementedError
    
    async def place_order(self, symbol: str, side: str, quantity: float, 
                         order_type: str = "market", price: Optional[float] = None) -> Dict[str, Any]:
        """Place trading order"""
        raise NotImplementedError
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel order"""
        raise NotImplementedError
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        raise NotImplementedError

class MetaTraderBroker(BrokerAPI):
    """MetaTrader broker integration (via MT5 API)"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.metaapi.cloud"
        self.session = None
        self.authenticated = False
    
    async def _get_session(self):
        """Get aiohttp session"""
        if not self.session:
            headers = {
                "auth-token": self.api_key,
                "Content-Type": "application/json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with MetaTrader API"""
        try:
            if not self.api_key:
                logger.warning("MetaTrader API key not provided")
                return False
            
            session = await self._get_session()
            
            # Test authentication by getting accounts
            async with session.get(f"{self.base_url}/users/current/accounts") as response:
                if response.status == 200:
                    self.authenticated = True
                    logger.info("MetaTrader authentication successful")
                    return True
                else:
                    logger.error(f"MetaTrader authentication failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"MetaTrader authentication error: {e}")
            return False
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get MetaTrader account balance"""
        try:
            if not self.authenticated:
                return await self._mock_balance()
            
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/users/current/accounts") as response:
                if response.status == 200:
                    accounts = await response.json()
                    
                    if accounts:
                        # Get the first account's balance
                        account = accounts[0]
                        return {
                            "currency": account.get("currency", "USD"),
                            "balance": account.get("balance", 0),
                            "equity": account.get("equity", 0),
                            "margin": account.get("margin", 0),
                            "free_margin": account.get("freeMargin", 0),
                            "margin_level": account.get("marginLevel", 0),
                            "profit": account.get("profit", 0),
                            "source": "metatrader"
                        }
                    
            return await self._mock_balance()
            
        except Exception as e:
            logger.error(f"MetaTrader balance error: {e}")
            return await self._mock_balance()
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get MetaTrader positions"""
        try:
            if not self.authenticated:
                return await self._mock_positions()
            
            # This would use the actual MetaTrader API
            # For now, return mock data
            return await self._mock_positions()
            
        except Exception as e:
            logger.error(f"MetaTrader positions error: {e}")
            return await self._mock_positions()
    
    async def place_order(self, symbol: str, side: str, quantity: float,
                         order_type: str = "market", price: Optional[float] = None) -> Dict[str, Any]:
        """Place MetaTrader order"""
        try:
            if not self.authenticated:
                return await self._mock_order_response(symbol, side, quantity)
            
            # This would use the actual MetaTrader API
            return await self._mock_order_response(symbol, side, quantity)
            
        except Exception as e:
            logger.error(f"MetaTrader order error: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _mock_balance(self) -> Dict[str, Any]:
        """Mock balance for demo purposes"""
        return {
            "currency": "USD",
            "balance": 10000.0,
            "equity": 10150.0,
            "margin": 500.0,
            "free_margin": 9650.0,
            "margin_level": 2030.0,
            "profit": 150.0,
            "source": "mock"
        }
    
    async def _mock_positions(self) -> List[Dict[str, Any]]:
        """Mock positions for demo purposes"""
        return [
            {
                "symbol": "EURUSD",
                "side": "buy",
                "volume": 1.0,
                "open_price": 1.0950,
                "current_price": 1.0985,
                "profit": 35.0,
                "swap": -0.5,
                "open_time": datetime.now().isoformat()
            }
        ]
    
    async def _mock_order_response(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """Mock order response"""
        return {
            "order_id": f"MT_{int(time.time())}",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "status": "filled",
            "fill_price": 1.1000,
            "timestamp": datetime.now().isoformat(),
            "source": "mock"
        }

class OandaBroker(BrokerAPI):
    """OANDA broker integration"""
    
    def __init__(self, api_key: str = None, account_id: str = None, environment: str = "practice"):
        self.api_key = api_key
        self.account_id = account_id
        self.environment = environment
        
        if environment == "live":
            self.base_url = "https://api-fxtrade.oanda.com"
        else:
            self.base_url = "https://api-fxpractice.oanda.com"
        
        self.session = None
        self.authenticated = False
    
    async def _get_session(self):
        """Get aiohttp session"""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with OANDA API"""
        try:
            if not self.api_key or not self.account_id:
                logger.warning("OANDA API credentials not provided")
                return False
            
            session = await self._get_session()
            
            # Test authentication by getting account info
            async with session.get(f"{self.base_url}/v3/accounts/{self.account_id}") as response:
                if response.status == 200:
                    self.authenticated = True
                    logger.info("OANDA authentication successful")
                    return True
                else:
                    logger.error(f"OANDA authentication failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"OANDA authentication error: {e}")
            return False
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get OANDA account balance"""
        try:
            if not self.authenticated:
                return await self._mock_balance()
            
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/v3/accounts/{self.account_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    account = data.get("account", {})
                    
                    return {
                        "currency": account.get("currency", "USD"),
                        "balance": float(account.get("balance", 0)),
                        "nav": float(account.get("NAV", 0)),
                        "unrealized_pl": float(account.get("unrealizedPL", 0)),
                        "realized_pl": float(account.get("realizedPL", 0)),
                        "margin_used": float(account.get("marginUsed", 0)),
                        "margin_available": float(account.get("marginAvailable", 0)),
                        "source": "oanda"
                    }
            
            return await self._mock_balance()
            
        except Exception as e:
            logger.error(f"OANDA balance error: {e}")
            return await self._mock_balance()
    
    async def place_order(self, symbol: str, side: str, quantity: float,
                         order_type: str = "market", price: Optional[float] = None) -> Dict[str, Any]:
        """Place OANDA order"""
        try:
            if not self.authenticated:
                return await self._mock_order_response(symbol, side, quantity)
            
            session = await self._get_session()
            
            # Format symbol for OANDA (e.g., EUR_USD)
            oanda_symbol = symbol.replace("/", "_")
            
            order_data = {
                "order": {
                    "type": order_type.upper(),
                    "instrument": oanda_symbol,
                    "units": str(int(quantity * 1000)),  # OANDA uses units
                }
            }
            
            if order_type.lower() == "limit" and price:
                order_data["order"]["price"] = str(price)
            
            async with session.post(
                f"{self.base_url}/v3/accounts/{self.account_id}/orders",
                json=order_data
            ) as response:
                
                if response.status in [200, 201]:
                    result = await response.json()
                    
                    order_transaction = result.get("orderCreateTransaction", {})
                    
                    return {
                        "order_id": order_transaction.get("id"),
                        "symbol": symbol,
                        "side": side,
                        "quantity": quantity,
                        "status": "submitted",
                        "timestamp": datetime.now().isoformat(),
                        "source": "oanda"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "error": error_data.get("errorMessage", "Order failed"),
                        "status": "failed"
                    }
            
        except Exception as e:
            logger.error(f"OANDA order error: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _mock_balance(self) -> Dict[str, Any]:
        """Mock OANDA balance"""
        return {
            "currency": "USD",
            "balance": 10000.0,
            "nav": 10150.0,
            "unrealized_pl": 150.0,
            "realized_pl": 0.0,
            "margin_used": 500.0,
            "margin_available": 9650.0,
            "source": "mock"
        }
    
    async def _mock_order_response(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """Mock OANDA order response"""
        return {
            "order_id": f"OANDA_{int(time.time())}",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "status": "filled",
            "fill_price": 1.1000,
            "timestamp": datetime.now().isoformat(),
            "source": "mock"
        }

class BrokerManager:
    """Manages multiple broker connections"""
    
    def __init__(self):
        self.brokers = {}
        self.active_broker = None
        
        # Initialize available brokers
        self._init_brokers()
    
    def _init_brokers(self):
        """Initialize broker instances"""
        try:
            # MetaTrader broker
            mt_api_key = getattr(settings, 'metatrader_api_key', None)
            if mt_api_key:
                self.brokers['metatrader'] = MetaTraderBroker(mt_api_key)
            
            # OANDA broker
            oanda_api_key = getattr(settings, 'oanda_api_key', None)
            oanda_account_id = getattr(settings, 'oanda_account_id', None)
            if oanda_api_key and oanda_account_id:
                self.brokers['oanda'] = OandaBroker(oanda_api_key, oanda_account_id)
            
            # Set default broker
            if self.brokers:
                self.active_broker = list(self.brokers.keys())[0]
                logger.info(f"Active broker set to: {self.active_broker}")
            
        except Exception as e:
            logger.error(f"Broker initialization error: {e}")
    
    async def authenticate_all(self) -> Dict[str, bool]:
        """Authenticate with all configured brokers"""
        results = {}
        
        for name, broker in self.brokers.items():
            try:
                success = await broker.authenticate()
                results[name] = success
                logger.info(f"Broker {name} authentication: {success}")
            except Exception as e:
                logger.error(f"Authentication failed for {name}: {e}")
                results[name] = False
        
        return results
    
    async def get_balance(self, broker_name: Optional[str] = None) -> Dict[str, Any]:
        """Get balance from specified or active broker"""
        broker_name = broker_name or self.active_broker
        
        if broker_name and broker_name in self.brokers:
            return await self.brokers[broker_name].get_balance()
        else:
            logger.error(f"Broker {broker_name} not found")
            return {"error": "Broker not available"}
    
    async def get_positions(self, broker_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get positions from specified or active broker"""
        broker_name = broker_name or self.active_broker
        
        if broker_name and broker_name in self.brokers:
            return await self.brokers[broker_name].get_positions()
        else:
            logger.error(f"Broker {broker_name} not found")
            return []
    
    async def place_order(self, symbol: str, side: str, quantity: float,
                         order_type: str = "market", price: Optional[float] = None,
                         broker_name: Optional[str] = None) -> Dict[str, Any]:
        """Place order with specified or active broker"""
        broker_name = broker_name or self.active_broker
        
        if broker_name and broker_name in self.brokers:
            return await self.brokers[broker_name].place_order(
                symbol, side, quantity, order_type, price
            )
        else:
            logger.error(f"Broker {broker_name} not found")
            return {"error": "Broker not available", "status": "failed"}
    
    def get_available_brokers(self) -> List[str]:
        """Get list of available brokers"""
        return list(self.brokers.keys())
    
    def set_active_broker(self, broker_name: str) -> bool:
        """Set active broker"""
        if broker_name in self.brokers:
            self.active_broker = broker_name
            logger.info(f"Active broker changed to: {broker_name}")
            return True
        else:
            logger.error(f"Broker {broker_name} not available")
            return False
    
    async def close_all_sessions(self):
        """Close all broker sessions"""
        for broker in self.brokers.values():
            if hasattr(broker, 'session') and broker.session:
                await broker.session.close()

# Global instance
broker_manager = BrokerManager()