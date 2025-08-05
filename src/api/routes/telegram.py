"""Telegram bot API routes."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from loguru import logger

from ...core.database import get_db
from ...bot.handlers import TelegramBotHandler
from ..models.schemas import TelegramWebhookUpdate, SuccessResponse

router = APIRouter()

# Initialize bot handler
bot_handler = TelegramBotHandler()


@router.post("/webhook")
async def telegram_webhook(
    update: TelegramWebhookUpdate,
    db: Session = Depends(get_db)
):
    """Handle Telegram webhook updates."""
    logger.info(f"Telegram webhook update: {update.update_id}")
    
    try:
        await bot_handler.handle_update(update.dict())
        
        return SuccessResponse(
            message="Update processed successfully",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Telegram webhook failed: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


@router.post("/send-message")
async def send_message(
    chat_id: int,
    message: str,
    db: Session = Depends(get_db)
):
    """Send a message to a Telegram chat."""
    logger.info(f"Sending message to chat {chat_id}")
    
    try:
        result = await bot_handler.send_message(chat_id, message)
        
        return {
            "success": True,
            "message_id": result.get("message_id"),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Send message failed: {e}")
        raise HTTPException(status_code=500, detail=f"Message sending failed: {str(e)}")


@router.post("/set-webhook")
async def set_webhook(
    webhook_url: str,
    db: Session = Depends(get_db)
):
    """Set the Telegram webhook URL."""
    logger.info(f"Setting webhook URL: {webhook_url}")
    
    try:
        result = await bot_handler.set_webhook(webhook_url)
        
        return SuccessResponse(
            message=f"Webhook set successfully to {webhook_url}",
            timestamp=datetime.utcnow(),
            data=result
        )
        
    except Exception as e:
        logger.error(f"Set webhook failed: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook setup failed: {str(e)}")


@router.delete("/webhook")
async def delete_webhook(db: Session = Depends(get_db)):
    """Delete the Telegram webhook."""
    logger.info("Deleting webhook")
    
    try:
        result = await bot_handler.delete_webhook()
        
        return SuccessResponse(
            message="Webhook deleted successfully",
            timestamp=datetime.utcnow(),
            data=result
        )
        
    except Exception as e:
        logger.error(f"Delete webhook failed: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook deletion failed: {str(e)}")


@router.get("/bot-info")
async def get_bot_info(db: Session = Depends(get_db)):
    """Get Telegram bot information."""
    logger.info("Getting bot info")
    
    try:
        bot_info = await bot_handler.get_bot_info()
        
        return {
            "bot_info": bot_info,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Get bot info failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bot info retrieval failed: {str(e)}")


@router.post("/broadcast")
async def broadcast_message(
    message: str,
    chat_ids: list[int] = None,
    db: Session = Depends(get_db)
):
    """Broadcast a message to multiple chats."""
    logger.info(f"Broadcasting message to {len(chat_ids) if chat_ids else 'all'} chats")
    
    try:
        if not chat_ids:
            # In a real implementation, get all active chat IDs from database
            chat_ids = []  # Mock empty list
        
        results = await bot_handler.broadcast_message(message, chat_ids)
        
        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful
        
        return {
            "message": message,
            "total_chats": len(chat_ids),
            "successful": successful,
            "failed": failed,
            "results": results,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Broadcast failed: {e}")
        raise HTTPException(status_code=500, detail=f"Broadcast failed: {str(e)}")


@router.get("/commands")
async def get_available_commands():
    """Get list of available bot commands."""
    commands = [
        {"command": "/start", "description": "Start using Celes.ia bot"},
        {"command": "/search", "description": "Search for flights"},
        {"command": "/trends", "description": "Get price trends"},
        {"command": "/miles", "description": "Check miles balance"},
        {"command": "/help", "description": "Get help and usage information"},
        {"command": "/settings", "description": "Manage bot settings"},
    ]
    
    return {
        "commands": commands,
        "timestamp": datetime.utcnow()
    }
