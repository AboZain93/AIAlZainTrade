"""
AI Trading Bot Engine
Main trading logic and execution
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

from .predictor import PricePredictor
from .analyzer import MarketAnalyzer
from .sentiment import SentimentAnalyzer
from database.models import TradeModel, SignalModel
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class TradingBot:
    """Main AI Trading Bot class"""
    
    def __init__(self):
        self.predictor = PricePredictor()
        self.analyzer = MarketAnalyzer()
        self.sentiment = SentimentAnalyzer()
        self.is_running = False
        
    async def execute_trade(self, symbol: str, action: str, amount: float, 
                          price: Optional[float] = None, stop_loss: Optional[float] = None,
                          take_profit: Optional[float] = None) -> Dict[str, Any]:
        """Execute a trading order"""
        try:
            trade_id = str(uuid.uuid4())
            
            # Get current market price if not provided
            if price is None:
                market_data = await self._get_market_price(symbol)
                price = market_data.get("current_price", 0.0)
            
            # Validate trade parameters
            if not await self._validate_trade(symbol, action, amount, price):
                raise ValueError("Invalid trade parameters")
            
            # Execute trade (simulation in demo mode)
            if settings.trading_mode == "demo":
                result = await self._simulate_trade(trade_id, symbol, action, amount, price, stop_loss, take_profit)
            else:
                result = await self._execute_live_trade(trade_id, symbol, action, amount, price, stop_loss, take_profit)
            
            logger.info(f"Trade executed: {trade_id} - {action} {amount} {symbol} at {price}")
            return result
            
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            raise
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current open positions"""
        try:
            if settings.trading_mode == "demo":
                return await self._get_demo_positions()
            else:
                return await self._get_live_positions()
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        try:
            if settings.trading_mode == "demo":
                return {
                    "currency": settings.default_currency,
                    "balance": 10000.0,  # Demo balance
                    "available": 9500.0,
                    "used": 500.0,
                    "profit_loss": 150.0
                }
            else:
                return await self._get_live_balance()
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {}
    
    async def get_signals(self) -> List[Dict[str, Any]]:
        """Get AI-generated trading signals"""
        try:
            signals = []
            symbols = ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD"]
            
            for symbol in symbols:
                # Get prediction
                prediction = await self.predictor.predict(symbol)
                
                # Get technical analysis
                analysis = await self.analyzer.analyze(symbol)
                
                # Get sentiment
                sentiment = await self.sentiment.analyze(f"{symbol} trading")
                
                # Combine signals
                signal = await self._generate_signal(symbol, prediction, analysis, sentiment)
                if signal:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Failed to generate signals: {e}")
            return []
    
    async def start_auto_trading(self):
        """Start automatic trading"""
        if self.is_running:
            return {"status": "already_running"}
        
        self.is_running = True
        asyncio.create_task(self._auto_trading_loop())
        logger.info("Auto trading started")
        return {"status": "started"}
    
    async def stop_auto_trading(self):
        """Stop automatic trading"""
        self.is_running = False
        logger.info("Auto trading stopped")
        return {"status": "stopped"}
    
    async def _auto_trading_loop(self):
        """Main auto trading loop"""
        while self.is_running:
            try:
                # Get signals
                signals = await self.get_signals()
                
                # Execute trades based on signals
                for signal in signals:
                    if signal.get("confidence", 0) >= 0.7:  # High confidence threshold
                        await self._execute_signal_trade(signal)
                
                # Wait before next iteration
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in auto trading loop: {e}")
                await asyncio.sleep(10)
    
    async def _simulate_trade(self, trade_id: str, symbol: str, action: str, 
                            amount: float, price: float, stop_loss: Optional[float],
                            take_profit: Optional[float]) -> Dict[str, Any]:
        """Simulate trade execution for demo mode"""
        return {
            "trade_id": trade_id,
            "symbol": symbol,
            "action": action,
            "amount": amount,
            "price": price,
            "status": "executed",
            "timestamp": datetime.now(),
            "fees": amount * 0.001,  # 0.1% fee simulation
            "mode": "demo"
        }
    
    async def _execute_live_trade(self, trade_id: str, symbol: str, action: str,
                                amount: float, price: float, stop_loss: Optional[float],
                                take_profit: Optional[float]) -> Dict[str, Any]:
        """Execute real trade (placeholder for broker integration)"""
        # This would integrate with actual broker API
        raise NotImplementedError("Live trading not implemented yet")
    
    async def _validate_trade(self, symbol: str, action: str, amount: float, price: float) -> bool:
        """Validate trade parameters"""
        if action not in ["buy", "sell"]:
            return False
        if amount <= 0:
            return False
        if price <= 0:
            return False
        if amount > settings.max_position_size:
            return False
        return True
    
    async def _get_market_price(self, symbol: str) -> Dict[str, Any]:
        """Get current market price for symbol"""
        # Placeholder - would integrate with market data provider
        return {
            "symbol": symbol,
            "current_price": 1.1000 if "USD" in symbol else 50000.0,
            "bid": 1.0999,
            "ask": 1.1001,
            "timestamp": datetime.now()
        }
    
    async def _generate_signal(self, symbol: str, prediction: Dict, analysis: Dict, sentiment: Dict) -> Optional[Dict]:
        """Generate trading signal from AI analysis"""
        try:
            # Combine different analysis scores
            pred_score = prediction.get("confidence", 0.0)
            tech_score = analysis.get("score", 0.0)
            sent_score = sentiment.get("score", 0.0)
            
            # Weighted average
            combined_score = (pred_score * 0.4 + tech_score * 0.4 + sent_score * 0.2)
            
            if combined_score >= 0.6:
                signal_type = prediction.get("direction", "hold")
                
                return {
                    "symbol": symbol,
                    "signal": signal_type,
                    "confidence": combined_score,
                    "price": prediction.get("target_price"),
                    "stop_loss": prediction.get("stop_loss"),
                    "take_profit": prediction.get("take_profit"),
                    "timeframe": "1h",
                    "timestamp": datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {e}")
            return None
    
    async def _get_demo_positions(self) -> List[Dict]:
        """Get demo positions"""
        return [
            {
                "symbol": "EURUSD",
                "action": "buy",
                "amount": 1000.0,
                "entry_price": 1.0950,
                "current_price": 1.0985,
                "profit_loss": 35.0,
                "timestamp": datetime.now() - timedelta(hours=2)
            }
        ]
    
    async def _get_live_positions(self) -> List[Dict]:
        """Get live positions from broker"""
        # Would integrate with broker API
        return []
    
    async def _get_live_balance(self) -> Dict:
        """Get live balance from broker"""
        # Would integrate with broker API
        return {}
    
    async def _execute_signal_trade(self, signal: Dict):
        """Execute trade based on signal"""
        try:
            await self.execute_trade(
                symbol=signal["symbol"],
                action=signal["signal"],
                amount=1000.0,  # Default amount
                price=signal.get("price"),
                stop_loss=signal.get("stop_loss"),
                take_profit=signal.get("take_profit")
            )
        except Exception as e:
            logger.error(f"Failed to execute signal trade: {e}")