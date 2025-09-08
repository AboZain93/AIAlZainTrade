# AIAlZainTrade 🤖📈

An AI-powered trading bot with Telegram integration, designed to provide intelligent trading signals, automated trading capabilities, and comprehensive market analysis.

## 🚀 Features

### Core Trading Features
- **AI-Powered Predictions**: Advanced machine learning models for price prediction
- **Technical Analysis**: Comprehensive technical indicators and pattern recognition
- **Sentiment Analysis**: Market sentiment analysis from news, social media, and forums
- **Automated Trading**: Execute trades automatically based on AI signals
- **Risk Management**: Built-in risk management and position sizing

### Telegram Integration
- **Interactive Bot**: Full-featured Telegram bot for trading commands
- **Real-time Notifications**: Instant alerts for signals, trades, and market events
- **Portfolio Management**: Check balance, positions, and trading history via Telegram
- **Command Interface**: Easy-to-use commands for all trading operations

### API & Integration
- **RESTful API**: Complete FastAPI backend with comprehensive endpoints
- **Multiple Brokers**: Support for various broker APIs (MetaTrader, OANDA, etc.)
- **Market Data**: Integration with multiple data providers (Alpha Vantage, Finnhub)
- **Database**: SQLAlchemy-based database for storing trades, users, and signals

## 🏗️ Architecture

```
AIAlZainTrade/
├── backend/                 # FastAPI backend application
│   ├── main.py             # Main FastAPI app
│   └── routers/            # API route handlers
├── ai_engine/              # AI/ML trading algorithms
│   ├── trading_bot.py      # Main trading bot logic
│   ├── predictor.py        # Price prediction models
│   ├── analyzer.py         # Technical analysis engine
│   └── sentiment.py        # Sentiment analysis
├── telegram/               # Telegram bot integration
│   └── bot_handler.py      # Bot command handlers
├── database/               # Database models and connections
│   ├── models.py           # SQLAlchemy models
│   └── connection.py       # Database connection management
├── integration/            # External service integrations
│   ├── market_data.py      # Market data providers
│   └── broker_api.py       # Broker API integrations
├── config/                 # Configuration management
│   └── settings.py         # Application settings
└── static/                 # Static files and templates
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- SQLite (included) or PostgreSQL (optional)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/AboZain93/AIAlZainTrade.git
cd AIAlZainTrade
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. **Run the application**
```bash
# Option 1: Using uvicorn directly
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Using the main entry point
python main.py

# Option 3: Using Docker
docker build -t aialzaintrade .
docker run -p 8000:8000 aialzaintrade
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Application Settings
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./ai_trade.db

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com

# Trading Settings
TRADING_MODE=demo  # demo or live
DEFAULT_CURRENCY=USD
MAX_POSITION_SIZE=1000.0

# AI/ML APIs
OPENAI_API_KEY=your_openai_api_key_here

# Market Data APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FINNHUB_API_KEY=your_finnhub_key_here

# Security
SECRET_KEY=your_very_secure_secret_key_here
```

### Telegram Bot Setup

1. **Create a bot** via [@BotFather](https://t.me/BotFather)
2. **Get your bot token** and add it to `.env`
3. **Set webhook** (for production):
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.com/api/v1/telegram/webhook"}'
```

## 🎮 Usage

### API Endpoints

The application provides a comprehensive REST API:

- **Trading**: `/api/v1/trading/`
  - `GET /` - Get all trades
  - `POST /execute` - Execute a trade
  - `GET /positions` - Get current positions
  - `GET /balance` - Get account balance
  - `GET /signals` - Get AI trading signals

- **AI Engine**: `/api/v1/ai/`
  - `POST /predict` - Get price predictions
  - `POST /analyze` - Perform market analysis
  - `POST /sentiment` - Analyze market sentiment

- **Telegram**: `/api/v1/telegram/`
  - `POST /webhook` - Telegram webhook endpoint
  - `POST /send-message` - Send message via bot
  - `POST /broadcast` - Broadcast to all users

- **Users**: `/api/v1/users/`
  - `GET /` - List users
  - `POST /` - Create user
  - `GET /{user_id}` - Get user details

### Telegram Bot Commands

- `/start` - Initialize bot and get welcome message
- `/help` - Show all available commands
- `/balance` - Check account balance
- `/positions` - View current trading positions
- `/signals` - Get latest AI trading signals
- `/trade [symbol] [buy/sell] [amount]` - Execute a trade
- `/history` - View trading history
- `/settings` - Configure bot preferences
- `/status` - Check system status

### Example Usage

**Execute a trade via API:**
```python
import requests

response = requests.post("http://localhost:8000/api/v1/trading/execute", 
    json={
        "symbol": "EURUSD",
        "action": "buy",
        "amount": 1000.0,
        "stop_loss": 1.0900,
        "take_profit": 1.1100
    }
)
```

**Get AI signals via API:**
```python
response = requests.get("http://localhost:8000/api/v1/trading/signals")
signals = response.json()["signals"]
```

## 🔬 AI Features

### Price Prediction
- **Machine Learning Models**: Random Forest, Neural Networks
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Multiple Timeframes**: 1m, 5m, 15m, 1h, 4h, 1d
- **Confidence Scoring**: Each prediction includes confidence level

### Market Analysis
- **Pattern Recognition**: Chart patterns, candlestick patterns
- **Support/Resistance**: Automated level detection
- **Trend Analysis**: Multi-timeframe trend identification
- **Volume Analysis**: Volume-based confirmation signals

### Sentiment Analysis
- **News Sources**: Financial news sentiment analysis
- **Social Media**: Twitter, Reddit sentiment tracking
- **Market Impact**: Assess potential price impact from sentiment

## 🔒 Security

- **API Authentication**: JWT-based authentication
- **Environment Variables**: Sensitive data in environment files
- **Input Validation**: Comprehensive input validation and sanitization
- **Rate Limiting**: API rate limiting to prevent abuse
- **HTTPS**: SSL/TLS encryption for all communications

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov=ai_engine --cov=telegram
```

## 📊 Monitoring & Logging

- **Structured Logging**: JSON-formatted logs for easy parsing
- **Health Checks**: `/health` endpoint for monitoring
- **Metrics**: Trading performance and system metrics
- **Error Tracking**: Comprehensive error logging and tracking

## 🚀 Deployment

### Docker Deployment

```bash
# Build image
docker build -t aialzaintrade .

# Run container
docker run -d \
  --name aialzaintrade \
  -p 8000:8000 \
  --env-file .env \
  aialzaintrade
```

### Production Deployment

1. **Set up environment** with production settings
2. **Configure database** (PostgreSQL recommended for production)
3. **Set up reverse proxy** (nginx recommended)
4. **Configure SSL certificates**
5. **Set up monitoring** and logging aggregation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Development Roadmap

- [ ] **Advanced AI Models**: Deep learning price prediction
- [ ] **More Brokers**: Additional broker API integrations
- [ ] **Portfolio Optimization**: AI-driven portfolio allocation
- [ ] **Risk Analytics**: Advanced risk assessment tools
- [ ] **Mobile App**: React Native mobile application
- [ ] **Web Interface**: React.js web dashboard
- [ ] **Backtesting**: Historical strategy testing framework

## 🐛 Known Issues

- Machine learning models require training data for optimal performance
- Some broker APIs may have rate limiting
- Telegram webhook requires HTTPS for production deployment

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**Important**: This software is for educational and research purposes. Trading financial instruments involves substantial risk of loss. The developers are not responsible for any financial losses incurred through the use of this software. Always test thoroughly in demo mode before using real money.

## 📞 Support

- **GitHub Issues**: [Report bugs and feature requests](https://github.com/AboZain93/AIAlZainTrade/issues)
- **Documentation**: Comprehensive API documentation available at `/docs` when running
- **Community**: Join our discussions for support and feature requests

## 🏆 Acknowledgments

- FastAPI for the excellent web framework
- python-telegram-bot for Telegram integration
- scikit-learn and TensorFlow for machine learning capabilities
- SQLAlchemy for database ORM
- All contributors and the open-source community

---

**Made with ❤️ for the trading community**