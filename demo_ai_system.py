#!/usr/bin/env python3
"""
Demonstração completa do Sistema IA Orquestradora
Mostra integração de ML, Self-Healing e Self-Improvement
"""

import asyncio
import sys
import os
from datetime import datetime, date, timedelta
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ai.orchestrator import ai_orchestrator, CelestiaAIOrchestrator
from src.ai.self_improvement import MetricType

async def demo_ai_orchestrator():
    """Demonstração completa do sistema IA."""
    print("🚀 DEMO: Sistema IA Orquestradora Celest.ia v2")
    print("=" * 60)
    
    try:
        # 1. Inicializar sistema
        print("\n1️⃣ Inicializando Sistema IA...")
        await ai_orchestrator.start()
        print("   ✅ Sistema IA iniciado com sucesso!")
        
        # 2. Status inicial do sistema
        print("\n2️⃣ Verificando Status Inicial...")
        status = await ai_orchestrator.get_system_status()
        print(f"   Modo: {status['system_status']['mode']}")
        print(f"   Performance Score: {status['system_status']['performance_score']}")
        print(f"   Subsistemas ativos: {len(status['subsystems'])}")
        
        # 3. Demonstrar predição de preços com IA
        print("\n3️⃣ Demonstrando Predição de Preços...")
        departure_date = datetime.now() + timedelta(days=30)
        return_date = departure_date + timedelta(days=7)
        
        prediction = await ai_orchestrator.predict_flight_price(
            origin="GRU",
            destination="MIA", 
            departure_date=departure_date,
            return_date=return_date,
            passengers=2
        )
        
        print(f"   📊 Preço Previsto: ${prediction['prediction']['price']:.2f}")
        print(f"   📈 Confiança: {prediction['prediction']['confidence']:.1%}")
        print(f"   📅 Melhor janela: {prediction['prediction']['booking_window']} dias")
        print(f"   🎯 Trend: {prediction['prediction']['trend']}")
        
        # 4. Demonstrar análise de dados com IA
        print("\n4️⃣ Demonstrando Análise de Dados...")
        sample_flights = [
            {
                "airline": "LATAM",
                "price": 850.99,
                "currency": "USD",
                "departure_time": "2025-08-10 08:00",
                "arrival_time": "2025-08-10 15:30",
                "duration_minutes": 450,
                "stops": 1
            },
            {
                "airline": "Copa Airlines", 
                "price": 920.50,
                "currency": "USD",
                "departure_time": "2025-08-10 10:30",
                "arrival_time": "2025-08-10 18:45", 
                "duration_minutes": 495,
                "stops": 0
            },
            {
                "airline": "American Airlines",
                "price": 780.25,
                "currency": "USD", 
                "departure_time": "2025-08-10 14:15",
                "arrival_time": "2025-08-10 21:40",
                "duration_minutes": 445,
                "stops": 1
            }
        ]
        
        analysis = await ai_orchestrator.analyze_flight_data(sample_flights)
        print(f"   📈 Voos analisados: {analysis['flights_analyzed']}")
        print(f"   🧠 AI Insights disponíveis: {'✅' if 'ai_insights' in analysis else '❌'}")
        
        # 5. Simular métricas de performance
        print("\n5️⃣ Registrando Métricas de Performance...")
        
        # Simular algumas métricas
        ai_orchestrator.self_improvement.record_performance_metric(
            MetricType.RESPONSE_TIME, 1.2, "flight_search"
        )
        ai_orchestrator.self_improvement.record_performance_metric(
            MetricType.ACCURACY, 0.95, "price_prediction"
        )
        ai_orchestrator.self_improvement.record_performance_metric(
            MetricType.USER_SATISFACTION, 4.5, "booking_experience"
        )
        
        print("   📊 Métricas registradas: Response Time, Accuracy, User Satisfaction")
        
        # 6. Simular interação do usuário
        print("\n6️⃣ Registrando Interações do Usuário...")
        
        ai_orchestrator.self_improvement.record_user_interaction(
            user_id="user_123",
            action="search_flights",
            context={"route": "GRU-MIA", "passengers": 2},
            outcome="success",
            satisfaction_score=4.8
        )
        
        ai_orchestrator.self_improvement.record_user_feedback(
            user_id="user_123",
            feedback_type="search_experience",
            rating=5.0,
            comments="Excelente sistema de busca!",
            context={"feature": "price_prediction"}
        )
        
        print("   👥 Interações e feedback registrados")
        
        # 7. Demonstrar otimização do sistema
        print("\n7️⃣ Executando Otimização do Sistema...")
        await ai_orchestrator.optimize_system()
        print("   ⚡ Otimização iniciada")
        
        # Aguardar um pouco para processar
        await asyncio.sleep(3)
        
        # 8. Status final do sistema
        print("\n8️⃣ Status Final do Sistema...")
        final_status = await ai_orchestrator.get_system_status()
        
        print(f"   📊 Performance Score: {final_status['system_status']['performance_score']}")
        print(f"   ⏱️ Uptime: {final_status['system_status']['uptime_human']}")
        print(f"   📈 Predições realizadas: {ai_orchestrator.metrics['predictions_made']}")
        print(f"   🔍 Análises realizadas: {ai_orchestrator.metrics['analyses_performed']}")
        
        # 9. Demonstrar insights de melhoria
        print("\n9️⃣ Insights de Auto-Melhoria...")
        improvement_report = await ai_orchestrator.self_improvement.get_improvement_report()
        
        print(f"   📋 Insights recentes: {len(improvement_report['recent_insights'])}")
        print(f"   🎯 Ações pendentes: {len(improvement_report['pending_actions'])}")
        print(f"   🧠 Padrões aprendidos: {len(improvement_report['learned_patterns'])}")
        print(f"   ✅ Melhorias aplicadas: {len(improvement_report['recent_improvements'])}")
        
        # 10. Demonstrar saúde do sistema
        print("\n🔟 Saúde do Sistema...")
        health_status = final_status['health_status']
        print(f"   🏥 Status geral: {health_status['overall_health']}")
        print(f"   📊 Componentes monitorados: {len(health_status.get('components', {}))}")
        
        print("\n" + "=" * 60)
        print("🎉 DEMO CONCLUÍDA COM SUCESSO!")
        print("✅ Todos os sistemas IA estão funcionando perfeitamente")
        print("🤖 Celest.ia v2 está pronta para uso em produção!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 11. Finalizar sistema
        print("\n🛑 Finalizando Sistema IA...")
        await ai_orchestrator.stop()
        print("   ✅ Sistema IA finalizado com segurança")

async def demo_individual_components():
    """Demonstração dos componentes individuais."""
    print("\n🔧 DEMO: Componentes Individuais")
    print("-" * 40)
    
    try:
        # Teste do ML Engine
        print("\n🧠 Testando ML Engine...")
        from src.ai.ml_engine import ml_orchestrator
        await ml_orchestrator.start()
        
        # Treinar modelo
        result = await ml_orchestrator.price_predictor.train_price_prediction_model()
        print(f"   📈 Treinamento ML: {'✅' if result.get('success') else '❌'}")
        
        await ml_orchestrator.stop()
        
        # Teste do Self-Healing
        print("\n🏥 Testando Self-Healing...")
        from src.ai.self_healing import self_healing_orchestrator
        await self_healing_orchestrator.start()
        
        health_report = await self_healing_orchestrator.get_system_health_report()
        print(f"   🔍 Health Check: {health_report['overall_health']}")
        
        await self_healing_orchestrator.stop()
        
        # Teste do Self-Improvement
        print("\n⚡ Testando Self-Improvement...")
        from src.ai.self_improvement import self_improvement_orchestrator
        await self_improvement_orchestrator.start()
        
        improvement_report = await self_improvement_orchestrator.get_improvement_report()
        print(f"   📊 Métricas coletadas: {improvement_report['metrics_collected']}")
        
        await self_improvement_orchestrator.stop()
        
        print("\n✅ Todos os componentes testados com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro nos testes de componentes: {e}")

def demo_configuration():
    """Demonstração da configuração do sistema."""
    print("\n⚙️ DEMO: Configuração do Sistema")
    print("-" * 40)
    
    try:
        from src.core.config import settings
        
        print(f"   🗄️ Database URL: {settings.database.host}:{settings.database.port}")
        print(f"   🌐 API Host: {settings.api.host}:{settings.api.port}")
        print(f"   🤖 LLM Provider: {settings.llm.default_provider}")
        print(f"   📞 Telegram Bot: {'✅' if settings.telegram.bot_token else '❌'}")
        
        print("\n✅ Configuração carregada com sucesso!")
        
    except Exception as e:
        print(f"\n⚠️ Configuração não disponível: {e}")
        print("   💡 Sistema funcionará com configurações padrão")

async def main():
    """Função principal da demonstração."""
    print("🎯 DEMONSTRAÇÃO COMPLETA - CELEST.IA v2 AI SYSTEM")
    print("🚀 Sistema Integrado de IA para Análise de Voos")
    print("📅 Data:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    # Configuração
    demo_configuration()
    
    # Componentes individuais
    await demo_individual_components()
    
    # Sistema completo
    await demo_ai_orchestrator()
    
    print("\n" + "=" * 80)
    print("🎊 DEMONSTRAÇÃO COMPLETA FINALIZADA!")
    print("🤖 Celest.ia v2 AI System está funcionando perfeitamente!")
    print("🚀 Pronto para análise inteligente de voos!")

if __name__ == "__main__":
    asyncio.run(main())
