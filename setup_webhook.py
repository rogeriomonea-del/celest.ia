#!/usr/bin/env python3
"""Configurador de webhook do Telegram"""

import asyncio
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

import httpx
from dotenv import load_dotenv

load_dotenv()

async def set_webhook(bot_token: str, webhook_url: str):
    """Configura o webhook do bot."""
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"url": webhook_url})
        return response.json()

async def delete_webhook(bot_token: str):
    """Remove o webhook do bot."""
    url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url)
        return response.json()

async def get_webhook_info(bot_token: str):
    """Obtém informações sobre o webhook."""
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

async def main():
    """Função principal."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN não encontrado no arquivo .env")
        return
    
    print("🤖 Configurador de Webhook - Celes.ia Bot")
    print("=" * 50)
    
    while True:
        print("\n📋 Opções:")
        print("1. Verificar webhook atual")
        print("2. Configurar webhook")
        print("3. Remover webhook")
        print("4. Sair")
        
        choice = input("\nEscolha uma opção (1-4): ").strip()
        
        if choice == "1":
            print("\n🔍 Verificando webhook...")
            info = await get_webhook_info(bot_token)
            if info.get("ok"):
                webhook_info = info.get("result", {})
                if webhook_info.get("url"):
                    print(f"✅ Webhook ativo: {webhook_info['url']}")
                    print(f"📊 Atualizações pendentes: {webhook_info.get('pending_update_count', 0)}")
                    if webhook_info.get("last_error_date"):
                        print(f"❌ Último erro: {webhook_info.get('last_error_message')}")
                else:
                    print("ℹ️  Nenhum webhook configurado")
            else:
                print(f"❌ Erro: {info.get('description')}")
        
        elif choice == "2":
            webhook_url = input("🌐 Digite a URL do webhook: ").strip()
            if not webhook_url:
                print("❌ URL não pode estar vazia")
                continue
            
            print(f"\n⚙️  Configurando webhook para: {webhook_url}")
            result = await set_webhook(bot_token, webhook_url)
            
            if result.get("ok"):
                print("✅ Webhook configurado com sucesso!")
            else:
                print(f"❌ Erro: {result.get('description')}")
        
        elif choice == "3":
            print("\n🗑️  Removendo webhook...")
            result = await delete_webhook(bot_token)
            
            if result.get("ok"):
                print("✅ Webhook removido com sucesso!")
            else:
                print(f"❌ Erro: {result.get('description')}")
        
        elif choice == "4":
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Até logo!")
    except Exception as e:
        print(f"❌ Erro: {e}")
