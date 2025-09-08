"""
Sentiment Analysis Engine
News and social media sentiment analysis for trading
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re

# Mock external API responses
import json

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Market Sentiment Analysis Engine"""
    
    def __init__(self):
        self.sentiment_sources = {
            "twitter": "Twitter API",
            "news": "News API",
            "reddit": "Reddit API",
            "telegram": "Telegram channels"
        }
    
    async def analyze(self, query: str, sources: List[str] = None, timeframe: str = "24h") -> Dict[str, Any]:
        """Analyze market sentiment for given query"""
        try:
            if sources is None:
                sources = ["twitter", "news"]
            
            # Validate sources
            valid_sources = [s for s in sources if s in self.sentiment_sources]
            if not valid_sources:
                valid_sources = ["news"]
            
            # Collect sentiment data from different sources
            sentiment_data = {}
            
            for source in valid_sources:
                data = await self._get_sentiment_from_source(source, query, timeframe)
                sentiment_data[source] = data
            
            # Aggregate sentiment scores
            overall_sentiment = await self._aggregate_sentiment(sentiment_data)
            
            # Generate market impact assessment
            market_impact = await self._assess_market_impact(overall_sentiment, query)
            
            return {
                "query": query,
                "timeframe": timeframe,
                "sources_analyzed": valid_sources,
                "sentiment_data": sentiment_data,
                "overall_sentiment": overall_sentiment,
                "market_impact": market_impact,
                "confidence": overall_sentiment.get("confidence", 0.5),
                "score": overall_sentiment.get("score", 0.0),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed for '{query}': {e}")
            return await self._mock_sentiment(query, sources or ["news"])
    
    async def _get_sentiment_from_source(self, source: str, query: str, timeframe: str) -> Dict[str, Any]:
        """Get sentiment data from specific source"""
        try:
            if source == "twitter":
                return await self._analyze_twitter_sentiment(query, timeframe)
            elif source == "news":
                return await self._analyze_news_sentiment(query, timeframe)
            elif source == "reddit":
                return await self._analyze_reddit_sentiment(query, timeframe)
            elif source == "telegram":
                return await self._analyze_telegram_sentiment(query, timeframe)
            else:
                return await self._mock_source_sentiment(source, query)
                
        except Exception as e:
            logger.error(f"Failed to get sentiment from {source}: {e}")
            return await self._mock_source_sentiment(source, query)
    
    async def _analyze_twitter_sentiment(self, query: str, timeframe: str) -> Dict[str, Any]:
        """Analyze Twitter sentiment (mock implementation)"""
        # In real implementation, this would use Twitter API v2
        
        # Mock tweet data
        tweets = await self._mock_twitter_data(query, timeframe)
        
        # Analyze sentiment of tweets
        sentiments = []
        for tweet in tweets:
            sentiment_score = await self._analyze_text_sentiment(tweet["text"])
            sentiments.append({
                "text": tweet["text"],
                "score": sentiment_score,
                "retweets": tweet.get("retweets", 0),
                "likes": tweet.get("likes", 0),
                "timestamp": tweet.get("timestamp")
            })
        
        # Calculate weighted average (considering engagement)
        total_weight = 0
        weighted_score = 0
        
        for sentiment in sentiments:
            weight = 1 + (sentiment["retweets"] * 0.1) + (sentiment["likes"] * 0.05)
            weighted_score += sentiment["score"] * weight
            total_weight += weight
        
        avg_sentiment = weighted_score / total_weight if total_weight > 0 else 0
        
        return {
            "source": "twitter",
            "total_posts": len(tweets),
            "sentiment_score": avg_sentiment,
            "confidence": min(0.9, len(tweets) / 100),  # Higher confidence with more data
            "engagement_weighted": True,
            "sample_posts": sentiments[:3]  # Top 3 for reference
        }
    
    async def _analyze_news_sentiment(self, query: str, timeframe: str) -> Dict[str, Any]:
        """Analyze news sentiment (mock implementation)"""
        # In real implementation, this would use news APIs like NewsAPI
        
        # Mock news data
        articles = await self._mock_news_data(query, timeframe)
        
        # Analyze sentiment of articles
        sentiments = []
        for article in articles:
            # Analyze title and description
            title_sentiment = await self._analyze_text_sentiment(article["title"])
            desc_sentiment = await self._analyze_text_sentiment(article.get("description", ""))
            
            # Weight title more heavily
            combined_sentiment = (title_sentiment * 0.7) + (desc_sentiment * 0.3)
            
            sentiments.append({
                "title": article["title"],
                "source": article.get("source", "unknown"),
                "score": combined_sentiment,
                "url": article.get("url"),
                "published": article.get("published_at")
            })
        
        # Calculate average sentiment
        avg_sentiment = sum(s["score"] for s in sentiments) / len(sentiments) if sentiments else 0
        
        return {
            "source": "news",
            "total_articles": len(articles),
            "sentiment_score": avg_sentiment,
            "confidence": min(0.85, len(articles) / 50),
            "major_sources": list(set(s.get("source", "unknown") for s in sentiments))[:5],
            "sample_articles": sentiments[:3]
        }
    
    async def _analyze_reddit_sentiment(self, query: str, timeframe: str) -> Dict[str, Any]:
        """Analyze Reddit sentiment (mock implementation)"""
        # Mock Reddit data
        posts = await self._mock_reddit_data(query, timeframe)
        
        sentiments = []
        for post in posts:
            sentiment_score = await self._analyze_text_sentiment(post["title"] + " " + post.get("text", ""))
            sentiments.append({
                "title": post["title"],
                "subreddit": post.get("subreddit"),
                "score": sentiment_score,
                "upvotes": post.get("upvotes", 0),
                "comments": post.get("comments", 0)
            })
        
        # Weight by upvotes and comments
        total_weight = 0
        weighted_score = 0
        
        for sentiment in sentiments:
            weight = 1 + (sentiment["upvotes"] * 0.01) + (sentiment["comments"] * 0.05)
            weighted_score += sentiment["score"] * weight
            total_weight += weight
        
        avg_sentiment = weighted_score / total_weight if total_weight > 0 else 0
        
        return {
            "source": "reddit",
            "total_posts": len(posts),
            "sentiment_score": avg_sentiment,
            "confidence": min(0.8, len(posts) / 75),
            "subreddits": list(set(s.get("subreddit") for s in sentiments)),
            "sample_posts": sentiments[:3]
        }
    
    async def _analyze_telegram_sentiment(self, query: str, timeframe: str) -> Dict[str, Any]:
        """Analyze Telegram sentiment (mock implementation)"""
        # Mock Telegram data
        messages = await self._mock_telegram_data(query, timeframe)
        
        sentiments = []
        for message in messages:
            sentiment_score = await self._analyze_text_sentiment(message["text"])
            sentiments.append({
                "text": message["text"][:100] + "..." if len(message["text"]) > 100 else message["text"],
                "channel": message.get("channel"),
                "score": sentiment_score,
                "views": message.get("views", 0)
            })
        
        avg_sentiment = sum(s["score"] for s in sentiments) / len(sentiments) if sentiments else 0
        
        return {
            "source": "telegram",
            "total_messages": len(messages),
            "sentiment_score": avg_sentiment,
            "confidence": min(0.75, len(messages) / 100),
            "channels": list(set(s.get("channel") for s in sentiments)),
            "sample_messages": sentiments[:3]
        }
    
    async def _analyze_text_sentiment(self, text: str) -> float:
        """Analyze sentiment of text using keyword-based approach"""
        if not text:
            return 0.0
        
        # Simple keyword-based sentiment analysis
        positive_words = [
            "bullish", "buy", "pump", "moon", "profit", "gain", "rise", "up", "bull",
            "positive", "good", "great", "excellent", "strong", "growth", "increase",
            "breakout", "rally", "surge", "boom", "optimistic", "confident"
        ]
        
        negative_words = [
            "bearish", "sell", "dump", "crash", "loss", "drop", "fall", "down", "bear",
            "negative", "bad", "terrible", "weak", "decline", "decrease", "plunge",
            "collapse", "correction", "pessimistic", "worried", "fear", "panic"
        ]
        
        # Convert to lowercase for analysis
        text_lower = text.lower()
        
        # Remove common words and clean text
        cleaned_text = re.sub(r'[^\w\s]', ' ', text_lower)
        words = cleaned_text.split()
        
        # Count sentiment words
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        # Calculate sentiment score (-1 to 1)
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return 0.0  # Neutral
        
        sentiment_score = (positive_count - negative_count) / len(words)
        
        # Normalize to [-1, 1] range
        return max(-1.0, min(1.0, sentiment_score * 10))
    
    async def _aggregate_sentiment(self, sentiment_data: Dict[str, Dict]) -> Dict[str, Any]:
        """Aggregate sentiment from multiple sources"""
        try:
            if not sentiment_data:
                return {"score": 0.0, "confidence": 0.0, "classification": "neutral"}
            
            # Weight different sources
            source_weights = {
                "news": 0.4,
                "twitter": 0.3,
                "reddit": 0.2,
                "telegram": 0.1
            }
            
            total_weight = 0
            weighted_score = 0
            total_confidence = 0
            
            for source, data in sentiment_data.items():
                weight = source_weights.get(source, 0.1)
                score = data.get("sentiment_score", 0.0)
                confidence = data.get("confidence", 0.0)
                
                weighted_score += score * weight * confidence
                total_weight += weight * confidence
                total_confidence += confidence
            
            # Calculate final scores
            final_score = weighted_score / total_weight if total_weight > 0 else 0.0
            final_confidence = total_confidence / len(sentiment_data)
            
            # Classify sentiment
            if final_score > 0.1:
                classification = "bullish"
            elif final_score < -0.1:
                classification = "bearish"
            else:
                classification = "neutral"
            
            return {
                "score": final_score,
                "confidence": final_confidence,
                "classification": classification,
                "sources_count": len(sentiment_data)
            }
            
        except Exception as e:
            logger.error(f"Sentiment aggregation failed: {e}")
            return {"score": 0.0, "confidence": 0.0, "classification": "neutral"}
    
    async def _assess_market_impact(self, sentiment: Dict, query: str) -> Dict[str, Any]:
        """Assess potential market impact of sentiment"""
        try:
            score = sentiment.get("score", 0.0)
            confidence = sentiment.get("confidence", 0.0)
            classification = sentiment.get("classification", "neutral")
            
            # Determine impact strength
            impact_strength = abs(score) * confidence
            
            if impact_strength > 0.6:
                impact_level = "high"
            elif impact_strength > 0.3:
                impact_level = "medium"
            else:
                impact_level = "low"
            
            # Determine direction
            if score > 0.1:
                direction = "positive"
                expected_effect = "price increase"
            elif score < -0.1:
                direction = "negative"
                expected_effect = "price decrease"
            else:
                direction = "neutral"
                expected_effect = "minimal price movement"
            
            return {
                "impact_level": impact_level,
                "direction": direction,
                "expected_effect": expected_effect,
                "strength": impact_strength,
                "recommendation": self._generate_sentiment_recommendation(classification, impact_level)
            }
            
        except Exception as e:
            logger.error(f"Market impact assessment failed: {e}")
            return {
                "impact_level": "unknown",
                "direction": "neutral",
                "expected_effect": "uncertain",
                "strength": 0.0
            }
    
    def _generate_sentiment_recommendation(self, classification: str, impact_level: str) -> str:
        """Generate recommendation based on sentiment"""
        if classification == "bullish" and impact_level == "high":
            return "Strong positive sentiment - consider buying"
        elif classification == "bullish" and impact_level == "medium":
            return "Moderate positive sentiment - cautiously optimistic"
        elif classification == "bearish" and impact_level == "high":
            return "Strong negative sentiment - consider selling or avoiding"
        elif classification == "bearish" and impact_level == "medium":
            return "Moderate negative sentiment - exercise caution"
        else:
            return "Neutral sentiment - no clear directional bias"
    
    # Mock data generators
    async def _mock_twitter_data(self, query: str, timeframe: str) -> List[Dict]:
        """Generate mock Twitter data"""
        tweets = [
            {"text": f"{query} looking bullish! Great fundamentals and strong momentum", "retweets": 45, "likes": 120},
            {"text": f"Sold my {query} position. Market looking uncertain", "retweets": 12, "likes": 34},
            {"text": f"{query} to the moon! 🚀 Best investment this year", "retweets": 78, "likes": 203},
            {"text": f"Technical analysis shows {query} might break resistance soon", "retweets": 23, "likes": 67},
            {"text": f"Bearish on {query} - too much hype, fundamentals don't support price", "retweets": 15, "likes": 43}
        ]
        
        for i, tweet in enumerate(tweets):
            tweet["timestamp"] = datetime.now() - timedelta(hours=i*2)
        
        return tweets
    
    async def _mock_news_data(self, query: str, timeframe: str) -> List[Dict]:
        """Generate mock news data"""
        articles = [
            {
                "title": f"{query} Shows Strong Performance Amid Market Volatility",
                "description": f"Analysts remain optimistic about {query}'s prospects despite broader market concerns",
                "source": "Financial Times",
                "published_at": datetime.now() - timedelta(hours=2)
            },
            {
                "title": f"Breaking: Major Institution Announces Large {query} Investment",
                "description": f"Institutional adoption continues to drive {query} growth",
                "source": "Bloomberg",
                "published_at": datetime.now() - timedelta(hours=6)
            },
            {
                "title": f"Market Analysis: {query} Faces Headwinds in Q4",
                "description": f"Regulatory concerns and market conditions may impact {query} performance",
                "source": "Reuters",
                "published_at": datetime.now() - timedelta(hours=12)
            }
        ]
        
        return articles
    
    async def _mock_reddit_data(self, query: str, timeframe: str) -> List[Dict]:
        """Generate mock Reddit data"""
        posts = [
            {
                "title": f"DD: Why {query} is undervalued right now",
                "text": f"Deep dive analysis of {query} fundamentals...",
                "subreddit": "investing",
                "upvotes": 234,
                "comments": 67
            },
            {
                "title": f"{query} daily discussion thread",
                "text": "What are your thoughts on today's price action?",
                "subreddit": "trading",
                "upvotes": 89,
                "comments": 156
            },
            {
                "title": f"Should I buy {query} at current levels?",
                "text": f"New to investing, looking for advice on {query}",
                "subreddit": "personalfinance",
                "upvotes": 45,
                "comments": 23
            }
        ]
        
        return posts
    
    async def _mock_telegram_data(self, query: str, timeframe: str) -> List[Dict]:
        """Generate mock Telegram data"""
        messages = [
            {
                "text": f"🚨 {query} SIGNAL: Strong buy signal detected on 4H chart",
                "channel": "TradingSignals",
                "views": 1234
            },
            {
                "text": f"{query} breaking major resistance level. Next target: +15%",
                "channel": "CryptoAnalysis", 
                "views": 567
            },
            {
                "text": f"Market update: {query} showing consolidation pattern, expecting breakout soon",
                "channel": "MarketInsights",
                "views": 890
            }
        ]
        
        return messages
    
    async def _mock_source_sentiment(self, source: str, query: str) -> Dict[str, Any]:
        """Generate mock sentiment for unknown source"""
        return {
            "source": source,
            "total_posts": 0,
            "sentiment_score": 0.0,
            "confidence": 0.0,
            "note": f"Mock data for {source}"
        }
    
    async def _mock_sentiment(self, query: str, sources: List[str]) -> Dict[str, Any]:
        """Generate mock sentiment analysis"""
        return {
            "query": query,
            "timeframe": "24h",
            "sources_analyzed": sources,
            "sentiment_data": {
                "news": {
                    "source": "news",
                    "total_articles": 3,
                    "sentiment_score": 0.2,
                    "confidence": 0.7
                }
            },
            "overall_sentiment": {
                "score": 0.2,
                "confidence": 0.7,
                "classification": "bullish",
                "sources_count": 1
            },
            "market_impact": {
                "impact_level": "medium",
                "direction": "positive",
                "expected_effect": "price increase",
                "strength": 0.14
            },
            "confidence": 0.7,
            "score": 0.2,
            "timestamp": datetime.now().isoformat(),
            "note": "Mock sentiment analysis - external APIs not configured"
        }