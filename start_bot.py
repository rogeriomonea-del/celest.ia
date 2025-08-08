#!/usr/bin/env python3
"""Bot do Telegram - Inicializador Celes.ia"""

import asyncio
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
from loguru import logger
from src.core.config import settings
from src.api.main import app
import uvicorn

# Carrega variáveis de ambiente
load_dotenv()

def check_configuration():
    """Verifica se todas as configurações necessárias estão presentes."""
    errors = []
    
    # Verifica token do Telegram
    if not settings.telegram.bot_token:
        errors.append("❌ TELEGRAM_BOT_TOKEN não configurado no arquivo .env")
    
    # Verifica OpenAI API Key (opcional mas recomendado)
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("⚠️  OPENAI_API_KEY não configurado - funcionalidades de IA limitadas")
    
    # Verifica se a pasta de logs existe
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)
        logger.info("📁 Pasta 'logs' criada")
    
    return errors

def setup_logging():
    """Configura o sistema de logging."""
    # Remove handlers padrão
    logger.remove()
    
    # Console output
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Arquivo de log
    logger.add(
        "logs/celestia_bot.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

async def start_bot():
    """Inicia o bot do Telegram."""
    logger.info("🚀 Iniciando Celes.ia Bot...")
    
    # Verifica configurações
    config_errors = check_configuration()
    if config_errors:
        logger.error("❌ Erros de configuração encontrados:")
        for error in config_errors:
            logger.error(f"   {error}")
        logger.error("\n💡 Edite o arquivo .env e adicione as configurações necessárias")
        return False
    
    logger.success("✅ Configurações verificadas")
    
    try:
        # Inicia a API FastAPI
        logger.info("🌐 Iniciando API FastAPI...")
        
        config = uvicorn.Config(
            app,
            host=settings.api.host,
            port=settings.api.port,
            log_level="info" if settings.api.debug else "warning",
            reload=settings.api.debug
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot interrompido pelo usuário")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar bot: {e}")
        return False

def main():
    """Função principal."""
    # Configura logging
    setup_logging()
    
    # Exibe banner
    print("""
🛫 ═══════════════════════════════════════ 🛫
    
     ██████╗███████╗██╗     ███████╗███████╗    ██╗ █████╗ 
    ██╔════╝██╔════╝██║     ██╔════╝██╔════╝    ██║██╔══██╗
    ██║     █████╗  ██║     █████╗  ███████╗    ██║███████║
    ██║     ██╔══╝  ██║     ██╔══╝  ╚════██║    ██║██╔══██║
    ╚██████╗███████╗███████╗███████╗███████║    ██║██║  ██║
     ╚═════╝╚══════╝╚══════╝╚══════╝╚══════╝    ╚═╝╚═╝  ╚═╝
    
                    🤖 Telegram Bot v2.0.0
    
🛫 ═══════════════════════════════════════ 🛫
    """)
    
    logger.info("🚀 Iniciando Celes.ia Bot...")
    
    # Executa o bot
    try:
        success = asyncio.run(start_bot())
        if success:
            logger.success("✅ Bot finalizado com sucesso")
        else:
            logger.error("❌ Bot finalizado com erros")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
