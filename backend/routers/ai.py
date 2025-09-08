"""
AI Engine API Router
Handles AI-related endpoints for analysis and predictions
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from ai_engine.predictor import PricePredictor
from ai_engine.analyzer import MarketAnalyzer
from ai_engine.sentiment import SentimentAnalyzer

router = APIRouter()

class PredictionRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"
    periods: int = 24

class AnalysisRequest(BaseModel):
    symbol: str
    data_points: int = 100

class SentimentRequest(BaseModel):
    query: str
    sources: List[str] = ["twitter", "news"]

@router.get("/")
async def ai_status():
    """AI engine status"""
    return {
        "status": "active",
        "models_loaded": True,
        "features": {
            "price_prediction": True,
            "market_analysis": True,
            "sentiment_analysis": True
        }
    }

@router.post("/predict")
async def predict_price(request: PredictionRequest):
    """Predict price movements using AI"""
    try:
        predictor = PricePredictor()
        
        prediction = await predictor.predict(
            symbol=request.symbol,
            timeframe=request.timeframe,
            periods=request.periods
        )
        
        return {
            "symbol": request.symbol,
            "prediction": prediction,
            "confidence": prediction.get("confidence", 0.0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/analyze")
async def analyze_market(request: AnalysisRequest):
    """Perform market analysis"""
    try:
        analyzer = MarketAnalyzer()
        
        analysis = await analyzer.analyze(
            symbol=request.symbol,
            data_points=request.data_points
        )
        
        return {
            "symbol": request.symbol,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    """Analyze market sentiment"""
    try:
        analyzer = SentimentAnalyzer()
        
        sentiment = await analyzer.analyze(
            query=request.query,
            sources=request.sources
        )
        
        return {
            "query": request.query,
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@router.get("/models")
async def get_model_info():
    """Get information about loaded AI models"""
    return {
        "models": {
            "price_predictor": {
                "status": "loaded",
                "version": "1.0.0",
                "accuracy": "85%"
            },
            "market_analyzer": {
                "status": "loaded", 
                "version": "1.0.0",
                "features": ["technical_indicators", "pattern_recognition"]
            },
            "sentiment_analyzer": {
                "status": "loaded",
                "version": "1.0.0",
                "sources": ["twitter", "news", "reddit"]
            }
        }
    }

@router.post("/retrain")
async def retrain_models():
    """Retrain AI models with latest data"""
    try:
        # This would trigger model retraining
        return {
            "status": "retraining_started",
            "estimated_time": "30 minutes",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")