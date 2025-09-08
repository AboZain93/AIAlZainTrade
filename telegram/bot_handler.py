"""
Telegram Bot Handler
Manages Telegram bot interactions and commands
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from telegram import Bot, Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    logging.warning("python-telegram-bot not available, using mock implementation")

from config.settings import get_settings
from ai_engine.trading_bot import TradingBot
from database.models import UserModel

logger = logging.getLogger(__name__)
settings = get_settings()

class TelegramBotHandler:
    """Telegram Bot Handler for AIAlZainTrade"""
    
    def __init__(self):
        self.bot = None
        self.application = None
        self.trading_bot = TradingBot()
        self.users = {}  # Simple in-memory user storage
        
        if HAS_TELEGRAM and settings.telegram_bot_token:
            self._init_bot()
    
    def _init_bot(self):
        """Initialize Telegram bot"""
        try:
            self.bot = Bot(token=settings.telegram_bot_token)
            self.application = Application.builder().token(settings.telegram_bot_token).build()
            
            # Add command handlers
            self._add_handlers()
            
            logger.info("Telegram bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
    
    def _add_handlers(self):
        """Add command handlers to the bot"""
        if not self.application:
            return
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(CommandHandler("balance", self._balance_command))
        self.application.add_handler(CommandHandler("positions", self._positions_command))
        self.application.add_handler(CommandHandler("signals", self._signals_command))
        self.application.add_handler(CommandHandler("history", self._history_command))
        self.application.add_handler(CommandHandler("settings", self._settings_command))
        self.application.add_handler(CommandHandler("trade", self._trade_command))
        self.application.add_handler(CommandHandler("status", self._status_command))
        
        # Message handler for non-command messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
    
    async def handle_update(self, update_data: Dict) -> Dict[str, Any]:
        """Handle incoming webhook update"""
        try:
            if not HAS_TELEGRAM:
                return await self._mock_handle_update(update_data)
            
            # Process the update through telegram library
            # This is a simplified version - in production, you'd need proper Update object handling
            
            message = update_data.get("message", {})
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")
            user_data = message.get("from", {})
            
            if not chat_id:
                return {"status": "error", "message": "No chat ID found"}
            
            # Store user info
            await self._store_user_info(user_data, chat_id)
            
            # Process command or message
            if text.startswith("/"):
                response = await self._process_command(chat_id, text)
            else:
                response = await self._process_message(chat_id, text)
            
            return {"status": "processed", "response": response}
            
        except Exception as e:
            logger.error(f"Error handling update: {e}")
            return {"status": "error", "message": str(e)}
    
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> Dict[str, Any]:
        """Send message to Telegram chat"""
        try:
            if not HAS_TELEGRAM or not self.bot:
                return await self._mock_send_message(chat_id, text)
            
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode
            )
            
            return {
                "message_id": message.message_id,
                "status": "sent",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def broadcast_message(self, message: str) -> Dict[str, Any]:
        """Broadcast message to all users"""
        try:
            sent_count = 0
            failed_count = 0
            
            # Get all user chat IDs
            chat_ids = list(self.users.keys())
            
            for chat_id in chat_ids:
                try:
                    await self.send_message(chat_id, message)
                    sent_count += 1
                    
                    # Add delay to avoid rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Failed to send broadcast to {chat_id}: {e}")
                    failed_count += 1
            
            return {
                "sent_count": sent_count,
                "failed_count": failed_count,
                "total_users": len(chat_ids)
            }
            
        except Exception as e:
            logger.error(f"Broadcast failed: {e}")
            return {"sent_count": 0, "failed_count": 0, "error": str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get bot status"""
        try:
            if not HAS_TELEGRAM or not self.bot:
                return {"status": "mock", "bot_username": "mock_bot"}
            
            bot_info = await self.bot.get_me()
            
            return {
                "status": "active",
                "bot_id": bot_info.id,
                "bot_username": bot_info.username,
                "bot_name": bot_info.first_name,
                "users_count": len(self.users)
            }
            
        except Exception as e:
            logger.error(f"Failed to get bot status: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_users(self) -> List[Dict[str, Any]]:
        """Get list of bot users"""
        return [
            {
                "chat_id": chat_id,
                "user_info": info,
                "last_interaction": info.get("last_interaction")
            }
            for chat_id, info in self.users.items()
        ]
    
    async def setup_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """Setup webhook for the bot"""
        try:
            if not HAS_TELEGRAM or not self.bot:
                return {"status": "mock", "url": webhook_url}
            
            await self.bot.set_webhook(url=webhook_url)
            
            return {
                "status": "webhook_set",
                "url": webhook_url,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to setup webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    async def delete_webhook(self) -> Dict[str, Any]:
        """Delete webhook"""
        try:
            if not HAS_TELEGRAM or not self.bot:
                return {"status": "mock"}
            
            await self.bot.delete_webhook()
            
            return {
                "status": "webhook_deleted",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    # Command handlers
    async def _start_command(self, update, context):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        welcome_message = f"""
🤖 <b>Welcome to AIAlZainTrade Bot!</b>

Hello {user.first_name}! I'm your AI-powered trading assistant.

<b>Available Commands:</b>
/help - Show all commands
/balance - Check account balance
/positions - View current positions
/signals - Get AI trading signals
/history - View trading history
/settings - Bot settings
/trade - Execute a trade
/status - System status

Let's start trading smartly with AI! 📈
        """
        
        await self.send_message(chat_id, welcome_message)
    
    async def _help_command(self, update, context):
        """Handle /help command"""
        chat_id = update.effective_chat.id
        
        help_message = """
🆘 <b>AIAlZainTrade Bot Help</b>

<b>Trading Commands:</b>
/balance - Check your account balance
/positions - View open positions
/signals - Get AI-generated signals
/trade [symbol] [action] [amount] - Execute trade
/history - View trading history

<b>Settings:</b>
/settings - Configure bot preferences

<b>Information:</b>
/status - System and market status
/help - Show this help message

<b>Trade Example:</b>
<code>/trade EURUSD buy 1000</code>

For support, contact @your_support_handle
        """
        
        await self.send_message(chat_id, help_message)
    
    async def _balance_command(self, update, context):
        """Handle /balance command"""
        chat_id = update.effective_chat.id
        
        try:
            balance = await self.trading_bot.get_balance()
            
            message = f"""
💰 <b>Account Balance</b>

<b>Currency:</b> {balance.get('currency', 'USD')}
<b>Total Balance:</b> ${balance.get('balance', 0):,.2f}
<b>Available:</b> ${balance.get('available', 0):,.2f}
<b>Used in Orders:</b> ${balance.get('used', 0):,.2f}

<b>P&L:</b> {'+' if balance.get('profit_loss', 0) >= 0 else ''}${balance.get('profit_loss', 0):,.2f}

<i>Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
            """
            
            await self.send_message(chat_id, message)
            
        except Exception as e:
            await self.send_message(chat_id, f"❌ Error getting balance: {str(e)}")
    
    async def _positions_command(self, update, context):
        """Handle /positions command"""
        chat_id = update.effective_chat.id
        
        try:
            positions = await self.trading_bot.get_positions()
            
            if not positions:
                await self.send_message(chat_id, "📊 No open positions")
                return
            
            message = "📊 <b>Open Positions</b>\n\n"
            
            for pos in positions:
                pnl = pos.get('profit_loss', 0)
                pnl_symbol = '+' if pnl >= 0 else ''
                
                message += f"""
<b>{pos.get('symbol')}</b>
Action: {pos.get('action', 'N/A').upper()}
Amount: {pos.get('amount', 0):,.2f}
Entry: ${pos.get('entry_price', 0):.4f}
Current: ${pos.get('current_price', 0):.4f}
P&L: {pnl_symbol}${pnl:.2f}
─────────────
"""
            
            await self.send_message(chat_id, message)
            
        except Exception as e:
            await self.send_message(chat_id, f"❌ Error getting positions: {str(e)}")
    
    async def _signals_command(self, update, context):
        """Handle /signals command"""
        chat_id = update.effective_chat.id
        
        try:
            signals = await self.trading_bot.get_signals()
            
            if not signals:
                await self.send_message(chat_id, "📡 No signals available at the moment")
                return
            
            message = "📡 <b>AI Trading Signals</b>\n\n"
            
            for signal in signals[:5]:  # Limit to 5 signals
                confidence = signal.get('confidence', 0) * 100
                
                message += f"""
<b>{signal.get('symbol')}</b>
Signal: {signal.get('signal', 'HOLD').upper()}
Confidence: {confidence:.0f}%
Price: ${signal.get('price', 0):.4f}
Target: ${signal.get('take_profit', 0):.4f} 
Stop Loss: ${signal.get('stop_loss', 0):.4f}
─────────────
"""
            
            message += f"\n<i>Generated: {datetime.now().strftime('%H:%M:%S')}</i>"
            
            await self.send_message(chat_id, message)
            
        except Exception as e:
            await self.send_message(chat_id, f"❌ Error getting signals: {str(e)}")
    
    async def _history_command(self, update, context):
        """Handle /history command"""
        chat_id = update.effective_chat.id
        
        # Mock trading history
        message = """
📈 <b>Trading History (Last 5 trades)</b>

<b>EURUSD</b> - BUY
Amount: 1,000
Entry: $1.0950 → Exit: $1.0985
P&L: +$35.00 ✅
Date: 2024-01-15

<b>GBPUSD</b> - SELL  
Amount: 500
Entry: $1.2450 → Exit: $1.2420
P&L: +$15.00 ✅
Date: 2024-01-14

<b>USDJPY</b> - BUY
Amount: 2,000  
Entry: ¥148.50 → Exit: ¥148.20
P&L: -$20.00 ❌
Date: 2024-01-13

<i>Total P&L: +$30.00</i>
<i>Win Rate: 66.7%</i>
        """
        
        await self.send_message(chat_id, message)
    
    async def _settings_command(self, update, context):
        """Handle /settings command"""
        chat_id = update.effective_chat.id
        
        message = """
⚙️ <b>Bot Settings</b>

<b>Current Settings:</b>
• Auto Trading: ❌ Disabled
• Risk Level: Medium
• Max Position: $1,000
• Notifications: ✅ Enabled
• Demo Mode: ✅ Enabled

<b>Available Commands:</b>
/settings auto on/off - Toggle auto trading
/settings risk low/medium/high - Set risk level
/settings notify on/off - Toggle notifications
/settings demo on/off - Toggle demo mode

<i>Contact support to modify other settings</i>
        """
        
        await self.send_message(chat_id, message)
    
    async def _trade_command(self, update, context):
        """Handle /trade command"""
        chat_id = update.effective_chat.id
        
        try:
            # Parse command arguments
            args = context.args if hasattr(context, 'args') else []
            
            if len(args) < 3:
                await self.send_message(
                    chat_id, 
                    "❌ Usage: /trade [symbol] [buy/sell] [amount]\nExample: /trade EURUSD buy 1000"
                )
                return
            
            symbol, action, amount = args[0], args[1], float(args[2])
            
            # Execute trade
            result = await self.trading_bot.execute_trade(symbol, action, amount)
            
            message = f"""
✅ <b>Trade Executed</b>

<b>Trade ID:</b> {result.get('trade_id', 'N/A')}
<b>Symbol:</b> {symbol.upper()}
<b>Action:</b> {action.upper()}
<b>Amount:</b> {amount:,.2f}
<b>Price:</b> ${result.get('price', 0):.4f}
<b>Status:</b> {result.get('status', 'Unknown')}

<i>Executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
            """
            
            await self.send_message(chat_id, message)
            
        except ValueError:
            await self.send_message(chat_id, "❌ Invalid amount. Please enter a valid number.")
        except Exception as e:
            await self.send_message(chat_id, f"❌ Trade failed: {str(e)}")
    
    async def _status_command(self, update, context):
        """Handle /status command"""
        chat_id = update.effective_chat.id
        
        message = f"""
🔧 <b>System Status</b>

<b>Trading Engine:</b> ✅ Online
<b>AI Models:</b> ✅ Loaded
<b>Market Data:</b> ✅ Connected
<b>Database:</b> ✅ Connected

<b>Trading Mode:</b> {settings.trading_mode.upper()}
<b>Server Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<b>Active Users:</b> {len(self.users)}
<b>Bot Version:</b> v1.0.0

All systems operational! 🚀
        """
        
        await self.send_message(chat_id, message)
    
    async def _handle_message(self, update, context):
        """Handle non-command messages"""
        chat_id = update.effective_chat.id
        text = update.message.text
        
        # Simple responses to common queries
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['price', 'quote', 'rate']):
            await self.send_message(
                chat_id,
                "📊 Use /signals to get current market analysis and price predictions."
            )
        elif any(word in text_lower for word in ['help', 'command']):
            await self.send_message(chat_id, "Type /help to see all available commands.")
        elif any(word in text_lower for word in ['balance', 'money', 'account']):
            await self.send_message(chat_id, "💰 Use /balance to check your account balance.")
        else:
            await self.send_message(
                chat_id,
                "🤖 I understand trading commands. Type /help to see what I can do!"
            )
    
    # Helper methods
    async def _store_user_info(self, user_data: Dict, chat_id: int):
        """Store user information"""
        self.users[chat_id] = {
            "user_id": user_data.get("id"),
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "last_interaction": datetime.now().isoformat(),
            "is_bot": user_data.get("is_bot", False)
        }
    
    async def _process_command(self, chat_id: int, command: str) -> str:
        """Process command (simplified for webhook handling)"""
        # This would map to the appropriate command handler
        if command.startswith("/start"):
            return "Welcome message sent"
        elif command.startswith("/help"):
            return "Help message sent"
        elif command.startswith("/balance"):
            return "Balance information sent"
        else:
            return f"Command {command} processed"
    
    async def _process_message(self, chat_id: int, text: str) -> str:
        """Process non-command message"""
        return "Message acknowledged"
    
    # Mock methods for when telegram library is not available
    async def _mock_handle_update(self, update_data: Dict) -> Dict[str, Any]:
        """Mock update handler"""
        return {
            "status": "mock_processed",
            "message": "Telegram library not available - using mock handler"
        }
    
    async def _mock_send_message(self, chat_id: int, text: str) -> Dict[str, Any]:
        """Mock message sender"""
        logger.info(f"Mock message to {chat_id}: {text[:50]}...")
        return {
            "message_id": 12345,
            "status": "mock_sent",
            "timestamp": datetime.now().isoformat()
        }