"""
Market Analysis Engine
Technical analysis and pattern recognition
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Technical Analysis and Market Pattern Recognition"""
    
    def __init__(self):
        self.indicators = {}
        self.patterns = {}
    
    async def analyze(self, symbol: str, data_points: int = 100) -> Dict[str, Any]:
        """Perform comprehensive market analysis"""
        try:
            # Get market data
            data = await self._get_market_data(symbol, data_points)
            
            if not data:
                return await self._mock_analysis(symbol)
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(data)
            
            # Technical indicators
            indicators = await self._calculate_indicators(df)
            
            # Pattern recognition
            patterns = await self._detect_patterns(df)
            
            # Support and resistance levels
            levels = await self._find_support_resistance(df)
            
            # Overall analysis score
            analysis_score = await self._calculate_analysis_score(indicators, patterns)
            
            # Trading recommendation
            recommendation = await self._generate_recommendation(indicators, patterns, analysis_score)
            
            return {
                "symbol": symbol,
                "analysis_timestamp": datetime.now().isoformat(),
                "indicators": indicators,
                "patterns": patterns,
                "support_resistance": levels,
                "score": analysis_score,
                "recommendation": recommendation,
                "timeframe": "1h",
                "data_points": len(data)
            }
            
        except Exception as e:
            logger.error(f"Analysis failed for {symbol}: {e}")
            return await self._mock_analysis(symbol)
    
    async def _get_market_data(self, symbol: str, periods: int) -> List[Dict]:
        """Get historical market data"""
        # Mock data generation
        data = []
        base_price = 1.1000 if "USD" in symbol else 50000.0
        
        for i in range(periods):
            # Generate realistic OHLCV data
            volatility = 0.01  # 1% volatility
            change = np.random.normal(0, volatility)
            
            close = base_price * (1 + change)
            open_price = base_price
            high = max(open_price, close) * (1 + abs(np.random.normal(0, volatility/2)))
            low = min(open_price, close) * (1 - abs(np.random.normal(0, volatility/2)))
            volume = np.random.uniform(1000, 10000)
            
            data.append({
                "timestamp": datetime.now() - timedelta(hours=periods-i),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume
            })
            
            base_price = close
        
        return data
    
    async def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators"""
        indicators = {}
        
        try:
            prices = df['close'].values
            highs = df['high'].values
            lows = df['low'].values
            volumes = df['volume'].values
            
            # Moving Averages
            if len(prices) >= 20:
                indicators['sma_20'] = np.mean(prices[-20:])
                indicators['sma_50'] = np.mean(prices[-50:]) if len(prices) >= 50 else np.mean(prices)
                
                # MA crossover signal
                if len(prices) >= 50:
                    ma_short = np.mean(prices[-20:])
                    ma_long = np.mean(prices[-50:])
                    indicators['ma_signal'] = "bullish" if ma_short > ma_long else "bearish"
                else:
                    indicators['ma_signal'] = "neutral"
            
            # RSI (Relative Strength Index)
            if len(prices) >= 14:
                rsi = await self._calculate_rsi(prices)
                indicators['rsi'] = rsi
                indicators['rsi_signal'] = self._interpret_rsi(rsi)
            
            # MACD (Moving Average Convergence Divergence)
            if len(prices) >= 26:
                macd_data = await self._calculate_macd(prices)
                indicators.update(macd_data)
            
            # Bollinger Bands
            if len(prices) >= 20:
                bb_data = await self._calculate_bollinger_bands(prices)
                indicators.update(bb_data)
            
            # Volume indicators
            indicators['volume_avg'] = np.mean(volumes[-20:]) if len(volumes) >= 20 else np.mean(volumes)
            indicators['volume_signal'] = "high" if volumes[-1] > indicators['volume_avg'] * 1.5 else "normal"
            
            # Volatility
            indicators['volatility'] = np.std(prices[-20:]) / np.mean(prices[-20:]) if len(prices) >= 20 else 0.01
            
        except Exception as e:
            logger.error(f"Indicator calculation failed: {e}")
        
        return indicators
    
    async def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            if len(prices) < period + 1:
                return 50.0  # Neutral RSI
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"RSI calculation failed: {e}")
            return 50.0
    
    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI signal"""
        if rsi > 70:
            return "overbought"
        elif rsi < 30:
            return "oversold"
        else:
            return "neutral"
    
    async def _calculate_macd(self, prices: np.ndarray) -> Dict[str, float]:
        """Calculate MACD indicator"""
        try:
            # Calculate EMAs
            ema_12 = await self._calculate_ema(prices, 12)
            ema_26 = await self._calculate_ema(prices, 26)
            
            macd_line = ema_12 - ema_26
            
            # Signal line (9-period EMA of MACD)
            macd_values = [macd_line]  # Simplified - would need historical MACD values
            signal_line = macd_line  # Simplified
            
            histogram = macd_line - signal_line
            
            return {
                "macd": macd_line,
                "macd_signal": signal_line,
                "macd_histogram": histogram,
                "macd_trend": "bullish" if macd_line > signal_line else "bearish"
            }
            
        except Exception as e:
            logger.error(f"MACD calculation failed: {e}")
            return {"macd": 0, "macd_signal": 0, "macd_histogram": 0, "macd_trend": "neutral"}
    
    async def _calculate_ema(self, prices: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average"""
        try:
            if len(prices) < period:
                return np.mean(prices)
            
            multiplier = 2 / (period + 1)
            ema = prices[0]
            
            for price in prices[1:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))
            
            return ema
            
        except Exception as e:
            logger.error(f"EMA calculation failed: {e}")
            return np.mean(prices) if len(prices) > 0 else 0
    
    async def _calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        try:
            if len(prices) < period:
                sma = np.mean(prices)
                std = np.std(prices)
            else:
                sma = np.mean(prices[-period:])
                std = np.std(prices[-period:])
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            current_price = prices[-1]
            
            # Band position
            if current_price > upper_band:
                position = "above_upper"
            elif current_price < lower_band:
                position = "below_lower"
            else:
                position = "within_bands"
            
            return {
                "bb_upper": upper_band,
                "bb_middle": sma,
                "bb_lower": lower_band,
                "bb_position": position,
                "bb_width": (upper_band - lower_band) / sma
            }
            
        except Exception as e:
            logger.error(f"Bollinger Bands calculation failed: {e}")
            return {"bb_upper": 0, "bb_middle": 0, "bb_lower": 0, "bb_position": "neutral", "bb_width": 0}
    
    async def _detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect chart patterns"""
        patterns = {}
        
        try:
            prices = df['close'].values
            
            # Trend detection
            if len(prices) >= 10:
                recent_trend = await self._detect_trend(prices[-10:])
                overall_trend = await self._detect_trend(prices[-30:]) if len(prices) >= 30 else recent_trend
                
                patterns['recent_trend'] = recent_trend
                patterns['overall_trend'] = overall_trend
                patterns['trend_strength'] = await self._calculate_trend_strength(prices)
            
            # Support/Resistance breaks
            if len(prices) >= 20:
                sr_breaks = await self._detect_breakouts(df)
                patterns.update(sr_breaks)
            
            # Candlestick patterns (simplified)
            if len(df) >= 3:
                candlestick_patterns = await self._detect_candlestick_patterns(df)
                patterns.update(candlestick_patterns)
            
        except Exception as e:
            logger.error(f"Pattern detection failed: {e}")
        
        return patterns
    
    async def _detect_trend(self, prices: np.ndarray) -> str:
        """Detect price trend"""
        try:
            if len(prices) < 3:
                return "neutral"
            
            # Linear regression to detect trend
            x = np.arange(len(prices))
            slope = np.polyfit(x, prices, 1)[0]
            
            # Normalize slope by price level
            normalized_slope = slope / np.mean(prices)
            
            if normalized_slope > 0.001:  # 0.1% threshold
                return "uptrend"
            elif normalized_slope < -0.001:
                return "downtrend"
            else:
                return "sideways"
                
        except Exception as e:
            logger.error(f"Trend detection failed: {e}")
            return "neutral"
    
    async def _calculate_trend_strength(self, prices: np.ndarray) -> float:
        """Calculate trend strength (0-1)"""
        try:
            if len(prices) < 10:
                return 0.5
            
            # Calculate R-squared of linear regression
            x = np.arange(len(prices))
            coeffs = np.polyfit(x, prices, 1)
            y_pred = np.polyval(coeffs, x)
            
            ss_res = np.sum((prices - y_pred) ** 2)
            ss_tot = np.sum((prices - np.mean(prices)) ** 2)
            
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            return max(0, min(1, r_squared))
            
        except Exception as e:
            logger.error(f"Trend strength calculation failed: {e}")
            return 0.5
    
    async def _detect_breakouts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect support/resistance breakouts"""
        try:
            prices = df['close'].values
            volumes = df['volume'].values
            
            if len(prices) < 20:
                return {"breakout": "none"}
            
            # Find recent high/low levels
            recent_high = np.max(prices[-20:-1])  # Exclude current price
            recent_low = np.min(prices[-20:-1])
            current_price = prices[-1]
            current_volume = volumes[-1]
            avg_volume = np.mean(volumes[-20:])
            
            # Check for breakouts with volume confirmation
            if current_price > recent_high and current_volume > avg_volume * 1.2:
                return {"breakout": "resistance_break", "strength": "strong"}
            elif current_price < recent_low and current_volume > avg_volume * 1.2:
                return {"breakout": "support_break", "strength": "strong"}
            elif current_price > recent_high:
                return {"breakout": "resistance_break", "strength": "weak"}
            elif current_price < recent_low:
                return {"breakout": "support_break", "strength": "weak"}
            else:
                return {"breakout": "none"}
                
        except Exception as e:
            logger.error(f"Breakout detection failed: {e}")
            return {"breakout": "none"}
    
    async def _detect_candlestick_patterns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Detect basic candlestick patterns"""
        try:
            if len(df) < 3:
                return {"candlestick_pattern": "none"}
            
            # Get last 3 candles
            recent = df.tail(3)
            
            # Simplified pattern detection
            last_candle = recent.iloc[-1]
            prev_candle = recent.iloc[-2]
            
            # Doji detection
            body_size = abs(last_candle['close'] - last_candle['open'])
            candle_range = last_candle['high'] - last_candle['low']
            
            if body_size < candle_range * 0.1:  # Small body relative to range
                return {"candlestick_pattern": "doji"}
            
            # Hammer/Hanging man
            lower_shadow = min(last_candle['open'], last_candle['close']) - last_candle['low']
            upper_shadow = last_candle['high'] - max(last_candle['open'], last_candle['close'])
            
            if lower_shadow > body_size * 2 and upper_shadow < body_size * 0.5:
                return {"candlestick_pattern": "hammer"}
            
            return {"candlestick_pattern": "none"}
            
        except Exception as e:
            logger.error(f"Candlestick pattern detection failed: {e}")
            return {"candlestick_pattern": "none"}
    
    async def _find_support_resistance(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        """Find support and resistance levels"""
        try:
            if len(df) < 20:
                return {"support_levels": [], "resistance_levels": []}
            
            highs = df['high'].values
            lows = df['low'].values
            
            # Find local maxima and minima
            resistance_levels = []
            support_levels = []
            
            # Simple peak detection
            for i in range(2, len(highs) - 2):
                # Local high (resistance)
                if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
                    highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                    resistance_levels.append(highs[i])
                
                # Local low (support)
                if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
                    lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                    support_levels.append(lows[i])
            
            # Keep only most significant levels
            resistance_levels = sorted(resistance_levels, reverse=True)[:3]
            support_levels = sorted(support_levels)[:3]
            
            return {
                "support_levels": support_levels,
                "resistance_levels": resistance_levels
            }
            
        except Exception as e:
            logger.error(f"Support/Resistance detection failed: {e}")
            return {"support_levels": [], "resistance_levels": []}
    
    async def _calculate_analysis_score(self, indicators: Dict, patterns: Dict) -> float:
        """Calculate overall analysis score (0-1)"""
        try:
            score = 0.5  # Neutral base
            weight_sum = 0
            
            # RSI contribution
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi > 70:  # Overbought
                    score += -0.2
                elif rsi < 30:  # Oversold
                    score += 0.2
                weight_sum += 0.2
            
            # MACD contribution
            if 'macd_trend' in indicators:
                if indicators['macd_trend'] == 'bullish':
                    score += 0.15
                elif indicators['macd_trend'] == 'bearish':
                    score += -0.15
                weight_sum += 0.15
            
            # MA signal contribution
            if 'ma_signal' in indicators:
                if indicators['ma_signal'] == 'bullish':
                    score += 0.1
                elif indicators['ma_signal'] == 'bearish':
                    score += -0.1
                weight_sum += 0.1
            
            # Trend contribution
            if 'overall_trend' in patterns:
                trend = patterns['overall_trend']
                strength = patterns.get('trend_strength', 0.5)
                
                if trend == 'uptrend':
                    score += 0.2 * strength
                elif trend == 'downtrend':
                    score += -0.2 * strength
                weight_sum += 0.2
            
            # Normalize score
            if weight_sum > 0:
                score = max(0, min(1, score))
            
            return score
            
        except Exception as e:
            logger.error(f"Analysis score calculation failed: {e}")
            return 0.5
    
    async def _generate_recommendation(self, indicators: Dict, patterns: Dict, score: float) -> Dict[str, Any]:
        """Generate trading recommendation"""
        try:
            if score > 0.7:
                action = "strong_buy"
                confidence = "high"
            elif score > 0.6:
                action = "buy"
                confidence = "medium"
            elif score < 0.3:
                action = "strong_sell"
                confidence = "high"
            elif score < 0.4:
                action = "sell"
                confidence = "medium"
            else:
                action = "hold"
                confidence = "low"
            
            # Risk assessment
            volatility = indicators.get('volatility', 0.01)
            if volatility > 0.03:
                risk = "high"
            elif volatility > 0.015:
                risk = "medium"
            else:
                risk = "low"
            
            return {
                "action": action,
                "confidence": confidence,
                "risk": risk,
                "score": score,
                "reasoning": self._generate_reasoning(indicators, patterns, score)
            }
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return {"action": "hold", "confidence": "low", "risk": "unknown", "score": 0.5}
    
    def _generate_reasoning(self, indicators: Dict, patterns: Dict, score: float) -> str:
        """Generate human-readable reasoning"""
        reasons = []
        
        # Add key factors
        if 'rsi_signal' in indicators:
            reasons.append(f"RSI is {indicators['rsi_signal']}")
        
        if 'ma_signal' in indicators:
            reasons.append(f"Moving averages show {indicators['ma_signal']} signal")
        
        if 'overall_trend' in patterns:
            trend = patterns['overall_trend']
            strength = patterns.get('trend_strength', 0.5)
            reasons.append(f"Overall trend is {trend} with {strength:.1%} strength")
        
        if not reasons:
            reasons.append("Analysis based on limited indicators")
        
        return "; ".join(reasons)
    
    async def _mock_analysis(self, symbol: str) -> Dict[str, Any]:
        """Generate mock analysis when data is not available"""
        return {
            "symbol": symbol,
            "analysis_timestamp": datetime.now().isoformat(),
            "indicators": {
                "rsi": 55.0,
                "rsi_signal": "neutral",
                "sma_20": 1.1000,
                "volatility": 0.015
            },
            "patterns": {
                "recent_trend": "sideways",
                "overall_trend": "neutral",
                "trend_strength": 0.5
            },
            "support_resistance": {
                "support_levels": [1.0950],
                "resistance_levels": [1.1050]
            },
            "score": 0.5,
            "recommendation": {
                "action": "hold",
                "confidence": "low",
                "risk": "medium",
                "score": 0.5,
                "reasoning": "Mock analysis - insufficient data"
            },
            "timeframe": "1h",
            "data_points": 0,
            "note": "Mock analysis - market data not available"
        }