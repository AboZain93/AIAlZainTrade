"""
AI Price Prediction Engine
Machine learning models for price forecasting
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import asyncio

# ML imports
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, r2_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logging.warning("scikit-learn not available, using mock predictions")

try:
    import tensorflow as tf
    from tensorflow import keras
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    logging.warning("TensorFlow not available, using simplified models")

logger = logging.getLogger(__name__)

class PricePredictor:
    """AI Price Prediction Engine"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        
        # Initialize models if libraries are available
        if HAS_SKLEARN:
            self._init_models()
    
    def _init_models(self):
        """Initialize ML models"""
        try:
            # Random Forest for short-term predictions
            self.models['rf_short'] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Random Forest for long-term predictions
            self.models['rf_long'] = RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                random_state=42
            )
            
            # Scalers for feature normalization
            self.scalers['short'] = StandardScaler()
            self.scalers['long'] = StandardScaler()
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
    
    async def predict(self, symbol: str, timeframe: str = "1h", periods: int = 24) -> Dict[str, Any]:
        """Generate price predictions for given symbol"""
        try:
            # Get historical data
            historical_data = await self._get_historical_data(symbol, periods * 2)
            
            if not historical_data:
                return await self._mock_prediction(symbol, timeframe, periods)
            
            # Prepare features
            features = await self._prepare_features(historical_data)
            
            # Make predictions
            if HAS_SKLEARN and self.is_trained:
                predictions = await self._ml_predict(features, timeframe, periods)
            else:
                predictions = await self._statistical_predict(historical_data, periods)
            
            # Calculate confidence and risk metrics
            confidence = await self._calculate_confidence(historical_data, predictions)
            
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "predictions": predictions,
                "confidence": confidence,
                "direction": self._determine_direction(predictions),
                "target_price": predictions[-1] if predictions else None,
                "stop_loss": self._calculate_stop_loss(predictions, historical_data),
                "take_profit": self._calculate_take_profit(predictions, historical_data),
                "risk_score": await self._calculate_risk_score(historical_data),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction failed for {symbol}: {e}")
            return await self._mock_prediction(symbol, timeframe, periods)
    
    async def train_models(self, symbol: str, data_points: int = 1000):
        """Train ML models with historical data"""
        try:
            if not HAS_SKLEARN:
                logger.warning("Cannot train models - scikit-learn not available")
                return False
            
            # Get training data
            training_data = await self._get_historical_data(symbol, data_points)
            if len(training_data) < 100:
                logger.warning("Insufficient data for training")
                return False
            
            # Prepare features and targets
            features, targets_short, targets_long = await self._prepare_training_data(training_data)
            
            # Split data
            X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
                features, targets_short, test_size=0.2, random_state=42
            )
            X_train_l, X_test_l, y_train_l, y_test_l = train_test_split(
                features, targets_long, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_s_scaled = self.scalers['short'].fit_transform(X_train_s)
            X_test_s_scaled = self.scalers['short'].transform(X_test_s)
            X_train_l_scaled = self.scalers['long'].fit_transform(X_train_l)
            X_test_l_scaled = self.scalers['long'].transform(X_test_l)
            
            # Train models
            self.models['rf_short'].fit(X_train_s_scaled, y_train_s)
            self.models['rf_long'].fit(X_train_l_scaled, y_train_l)
            
            # Evaluate models
            short_score = self.models['rf_short'].score(X_test_s_scaled, y_test_s)
            long_score = self.models['rf_long'].score(X_test_l_scaled, y_test_l)
            
            logger.info(f"Models trained - Short-term R²: {short_score:.4f}, Long-term R²: {long_score:.4f}")
            
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False
    
    async def _get_historical_data(self, symbol: str, periods: int) -> List[Dict]:
        """Get historical price data"""
        # Mock historical data generation
        data = []
        base_price = 1.1000 if "USD" in symbol else 50000.0
        
        for i in range(periods):
            # Generate realistic price movements
            change = np.random.normal(0, 0.01)  # 1% volatility
            price = base_price * (1 + change)
            
            data.append({
                "timestamp": datetime.now() - timedelta(hours=periods-i),
                "open": price * 0.999,
                "high": price * 1.002,
                "low": price * 0.998,
                "close": price,
                "volume": np.random.uniform(1000, 10000)
            })
            
            base_price = price
        
        return data
    
    async def _prepare_features(self, data: List[Dict]) -> np.ndarray:
        """Prepare features from historical data"""
        if not data:
            return np.array([])
        
        df = pd.DataFrame(data)
        
        # Technical indicators
        features = []
        
        # Price-based features
        prices = df['close'].values
        features.extend([
            prices[-1],  # Current price
            np.mean(prices[-5:]),  # 5-period SMA
            np.mean(prices[-20:]),  # 20-period SMA
            np.std(prices[-20:]),  # Volatility
        ])
        
        # Volume features
        volumes = df['volume'].values
        features.extend([
            volumes[-1],  # Current volume
            np.mean(volumes[-5:]),  # Average volume
        ])
        
        # Momentum indicators
        if len(prices) >= 14:
            # RSI calculation (simplified)
            gains = np.diff(prices)
            gains[gains < 0] = 0
            losses = -np.diff(prices)
            losses[losses < 0] = 0
            
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])
            
            if avg_loss != 0:
                rsi = 100 - (100 / (1 + avg_gain / avg_loss))
            else:
                rsi = 100
            
            features.append(rsi)
        else:
            features.append(50)  # Neutral RSI
        
        return np.array(features).reshape(1, -1)
    
    async def _ml_predict(self, features: np.ndarray, timeframe: str, periods: int) -> List[float]:
        """Make predictions using ML models"""
        try:
            # Choose model based on timeframe
            model_key = 'rf_short' if periods <= 24 else 'rf_long'
            scaler_key = 'short' if periods <= 24 else 'long'
            
            # Scale features
            features_scaled = self.scalers[scaler_key].transform(features)
            
            # Make predictions
            predictions = []
            current_features = features_scaled.copy()
            
            for _ in range(periods):
                pred = self.models[model_key].predict(current_features)[0]
                predictions.append(pred)
                
                # Update features for next prediction (simplified)
                current_features[0, 0] = pred  # Update current price
            
            return predictions
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return []
    
    async def _statistical_predict(self, data: List[Dict], periods: int) -> List[float]:
        """Make predictions using statistical methods"""
        try:
            prices = [item['close'] for item in data]
            
            if len(prices) < 5:
                return [prices[-1]] * periods
            
            # Simple trend analysis
            recent_trend = np.mean(np.diff(prices[-5:]))
            volatility = np.std(prices[-20:]) if len(prices) >= 20 else np.std(prices)
            
            predictions = []
            last_price = prices[-1]
            
            for i in range(periods):
                # Add trend with some noise
                noise = np.random.normal(0, volatility * 0.1)
                predicted_price = last_price + (recent_trend * (i + 1)) + noise
                predictions.append(predicted_price)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Statistical prediction failed: {e}")
            return []
    
    async def _prepare_training_data(self, data: List[Dict]):
        """Prepare training data with features and targets"""
        df = pd.DataFrame(data)
        
        features = []
        targets_short = []
        targets_long = []
        
        # Create sliding windows
        window_size = 20
        
        for i in range(window_size, len(df) - 24):
            # Features from current window
            window_data = df.iloc[i-window_size:i]
            feature_row = await self._extract_features_from_window(window_data)
            
            # Short-term target (next hour)
            short_target = df.iloc[i + 1]['close']
            
            # Long-term target (24 hours ahead)
            long_target = df.iloc[i + 24]['close'] if i + 24 < len(df) else df.iloc[-1]['close']
            
            features.append(feature_row)
            targets_short.append(short_target)
            targets_long.append(long_target)
        
        return np.array(features), np.array(targets_short), np.array(targets_long)
    
    async def _extract_features_from_window(self, window_data: pd.DataFrame) -> List[float]:
        """Extract features from a data window"""
        prices = window_data['close'].values
        volumes = window_data['volume'].values
        
        features = [
            prices[-1],  # Current price
            np.mean(prices),  # Average price
            np.std(prices),   # Volatility
            np.mean(volumes), # Average volume
            prices[-1] / prices[0] - 1,  # Return over window
        ]
        
        return features
    
    async def _calculate_confidence(self, historical_data: List[Dict], predictions: List[float]) -> float:
        """Calculate prediction confidence score"""
        try:
            if not historical_data or not predictions:
                return 0.5
            
            # Calculate based on historical volatility and model performance
            prices = [item['close'] for item in historical_data]
            volatility = np.std(prices) / np.mean(prices) if prices else 0.1
            
            # Lower volatility = higher confidence
            base_confidence = max(0.1, 1.0 - volatility * 10)
            
            # Adjust based on prediction consistency
            if len(predictions) > 1:
                pred_volatility = np.std(predictions) / np.mean(predictions)
                consistency_factor = max(0.5, 1.0 - pred_volatility * 5)
                base_confidence *= consistency_factor
            
            return min(0.95, max(0.1, base_confidence))
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5
    
    def _determine_direction(self, predictions: List[float]) -> str:
        """Determine overall price direction"""
        if not predictions or len(predictions) < 2:
            return "hold"
        
        start_price = predictions[0]
        end_price = predictions[-1]
        
        change_pct = (end_price - start_price) / start_price
        
        if change_pct > 0.01:  # 1% threshold
            return "buy"
        elif change_pct < -0.01:
            return "sell"
        else:
            return "hold"
    
    def _calculate_stop_loss(self, predictions: List[float], historical_data: List[Dict]) -> Optional[float]:
        """Calculate stop loss level"""
        if not predictions or not historical_data:
            return None
        
        current_price = predictions[0]
        volatility = np.std([item['close'] for item in historical_data[-20:]])
        
        # 2x volatility for stop loss
        return current_price - (volatility * 2)
    
    def _calculate_take_profit(self, predictions: List[float], historical_data: List[Dict]) -> Optional[float]:
        """Calculate take profit level"""
        if not predictions or not historical_data:
            return None
        
        current_price = predictions[0]
        target_price = predictions[-1]
        
        # 1.5x the predicted move
        move = target_price - current_price
        return current_price + (move * 1.5)
    
    async def _calculate_risk_score(self, historical_data: List[Dict]) -> float:
        """Calculate risk score (0-1, higher = riskier)"""
        try:
            if not historical_data:
                return 0.5
            
            prices = [item['close'] for item in historical_data]
            
            # Calculate volatility-based risk
            volatility = np.std(prices) / np.mean(prices) if prices else 0.1
            
            # Normalize to 0-1 scale
            risk_score = min(1.0, volatility * 20)
            
            return risk_score
            
        except Exception as e:
            logger.error(f"Risk calculation failed: {e}")
            return 0.5
    
    async def _mock_prediction(self, symbol: str, timeframe: str, periods: int) -> Dict[str, Any]:
        """Generate mock prediction when ML is not available"""
        base_price = 1.1000 if "USD" in symbol else 50000.0
        
        predictions = []
        for i in range(periods):
            # Random walk with slight upward bias
            change = np.random.normal(0.001, 0.01)  # 0.1% bias, 1% volatility
            price = base_price * (1 + change)
            predictions.append(price)
            base_price = price
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "predictions": predictions,
            "confidence": 0.6,
            "direction": "buy" if predictions[-1] > predictions[0] else "sell",
            "target_price": predictions[-1],
            "stop_loss": predictions[0] * 0.98,
            "take_profit": predictions[0] * 1.02,
            "risk_score": 0.5,
            "timestamp": datetime.now().isoformat(),
            "note": "Mock prediction - ML models not trained"
        }