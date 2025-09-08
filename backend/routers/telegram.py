"""
Telegram Bot API Router
Handles Telegram integration endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from telegram.bot_handler import TelegramBotHandler
from database.models import UserModel

router = APIRouter()

class WebhookUpdate(BaseModel):
    update_id: int
    message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None

class SendMessageRequest(BaseModel):
    chat_id: int
    text: str
    parse_mode: Optional[str] = "HTML"

@router.get("/")
async def telegram_status():
    """Telegram bot status"""
    try:
        bot_handler = TelegramBotHandler()
        status = await bot_handler.get_status()
        return {
            "status": "active",
            "bot_info": status,
            "webhook_configured": True
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.post("/webhook")
async def telegram_webhook(update: WebhookUpdate):
    """Handle Telegram webhook updates"""
    try:
        bot_handler = TelegramBotHandler()
        await bot_handler.handle_update(update.dict())
        return {"status": "ok"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-message")
async def send_message(request: SendMessageRequest):
    """Send message via Telegram bot"""
    try:
        bot_handler = TelegramBotHandler()
        result = await bot_handler.send_message(
            chat_id=request.chat_id,
            text=request.text,
            parse_mode=request.parse_mode
        )
        return {"status": "sent", "message_id": result.message_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broadcast")
async def broadcast_message(message: str):
    """Broadcast message to all users"""
    try:
        bot_handler = TelegramBotHandler()
        result = await bot_handler.broadcast_message(message)
        return {
            "status": "broadcast_sent",
            "recipients": result["sent_count"],
            "failed": result["failed_count"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def get_telegram_users():
    """Get list of Telegram users"""
    try:
        bot_handler = TelegramBotHandler()
        users = await bot_handler.get_users()
        return {"users": users}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/setup-webhook")
async def setup_webhook(webhook_url: str):
    """Setup Telegram webhook"""
    try:
        bot_handler = TelegramBotHandler()
        result = await bot_handler.setup_webhook(webhook_url)
        return {"status": "webhook_set", "url": webhook_url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/webhook")
async def delete_webhook():
    """Delete Telegram webhook"""
    try:
        bot_handler = TelegramBotHandler()
        await bot_handler.delete_webhook()
        return {"status": "webhook_deleted"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/commands")
async def get_bot_commands():
    """Get available bot commands"""
    return {
        "commands": [
            {"command": "/start", "description": "Start using the bot"},
            {"command": "/help", "description": "Show help message"},
            {"command": "/balance", "description": "Check account balance"},
            {"command": "/positions", "description": "View current positions"},
            {"command": "/signals", "description": "Get trading signals"},
            {"command": "/history", "description": "View trading history"},
            {"command": "/settings", "description": "Bot settings"}
        ]
    }