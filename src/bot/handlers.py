"""Telegram bot handlers."""
from __future__ import annotations

import json
from typing import Dict, Any, List, Optional
from datetime import date, datetime
from loguru import logger

from ..core.config import settings
from ..core.orchestrator import CelestiaOrchestrator
from .commands import BotCommands


class TelegramBotHandler:
    """Main Telegram bot handler."""
    
    def __init__(self):
        """Initialize bot handler."""
        self.token = settings.telegram.bot_token
        self.orchestrator = CelestiaOrchestrator()
        self.commands = BotCommands(self.orchestrator)
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        if not self.token:
            logger.warning("Telegram bot token not configured")
    
    async def handle_update(self, update: Dict[str, Any]) -> None:
        """Handle incoming Telegram update."""
        logger.info(f"Processing update: {update.get('update_id')}")
        
        try:
            if "message" in update:
                await self._handle_message(update["message"])
            elif "callback_query" in update:
                await self._handle_callback_query(update["callback_query"])
            else:
                logger.warning(f"Unhandled update type: {update}")
                
        except Exception as e:
            logger.error(f"Error handling update: {e}")
    
    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handle text message."""
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user_id = message["from"]["id"]
        
        logger.info(f"Message from {user_id} in chat {chat_id}: {text}")
        
        if text.startswith("/"):
            await self._handle_command(chat_id, user_id, text)
        else:
            await self._handle_text(chat_id, user_id, text)
    
    async def _handle_command(self, chat_id: int, user_id: int, command: str) -> None:
        """Handle bot command."""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        try:
            if cmd == "/start":
                response = await self.commands.start_command(user_id)
            elif cmd == "/help":
                response = await self.commands.help_command()
            elif cmd == "/search":
                response = await self.commands.search_command(args)
            elif cmd == "/trends":
                response = await self.commands.trends_command(args)
            elif cmd == "/miles":
                response = await self.commands.miles_command(args)
            elif cmd == "/settings":
                response = await self.commands.settings_command(user_id)
            else:
                response = "Unknown command. Type /help for available commands."
            
            await self.send_message(chat_id, response)
            
        except Exception as e:
            logger.error(f"Command handling error: {e}")
            await self.send_message(chat_id, f"Sorry, an error occurred: {str(e)}")
    
    async def _handle_text(self, chat_id: int, user_id: int, text: str) -> None:
        """Handle regular text message."""
        # Try to interpret as natural language flight search
        response = await self.commands.natural_language_search(text)
        await self.send_message(chat_id, response)
    
    async def _handle_callback_query(self, callback_query: Dict[str, Any]) -> None:
        """Handle callback query from inline keyboard."""
        query_id = callback_query["id"]
        chat_id = callback_query["message"]["chat"]["id"]
        data = callback_query.get("data", "")
        
        logger.info(f"Callback query: {data}")
        
        try:
            response = await self.commands.handle_callback(data)
            await self.send_message(chat_id, response)
            await self.answer_callback_query(query_id)
            
        except Exception as e:
            logger.error(f"Callback query error: {e}")
            await self.answer_callback_query(query_id, "Error processing request")
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send message to Telegram chat."""
        if not self.token:
            logger.warning("Telegram bot not configured")
            return {"error": "Bot not configured"}
        
        try:
            import httpx
            
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    data=data
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Send message error: {e}")
            return {"error": str(e)}
    
    async def answer_callback_query(
        self,
        query_id: str,
        text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Answer callback query."""
        if not self.token:
            return {"error": "Bot not configured"}
        
        try:
            import httpx
            
            data = {"callback_query_id": query_id}
            if text:
                data["text"] = text
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/answerCallbackQuery",
                    data=data
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Answer callback query error: {e}")
            return {"error": str(e)}
    
    async def set_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """Set webhook URL."""
        if not self.token:
            return {"error": "Bot not configured"}
        
        try:
            import httpx
            
            data = {"url": webhook_url}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/setWebhook",
                    data=data
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Set webhook error: {e}")
            return {"error": str(e)}
    
    async def delete_webhook(self) -> Dict[str, Any]:
        """Delete webhook."""
        if not self.token:
            return {"error": "Bot not configured"}
        
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/deleteWebhook")
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Delete webhook error: {e}")
            return {"error": str(e)}
    
    async def get_bot_info(self) -> Dict[str, Any]:
        """Get bot information."""
        if not self.token:
            return {"error": "Bot not configured"}
        
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/getMe")
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Get bot info error: {e}")
            return {"error": str(e)}
    
    async def broadcast_message(
        self,
        message: str,
        chat_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """Broadcast message to multiple chats."""
        results = []
        
        for chat_id in chat_ids:
            try:
                result = await self.send_message(chat_id, message)
                results.append({"chat_id": chat_id, "success": True, "result": result})
            except Exception as e:
                results.append({"chat_id": chat_id, "success": False, "error": str(e)})
        
        return results
