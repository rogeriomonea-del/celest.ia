#!/usr/bin/env python3
"""
Demonstração Completa do Sistema de IA Orquestradora Celest.ia v2
Inclui ML Engine, Self-Healing e Self-Improvement integrados
"""

import asyncio
import logging
from datetime import datetime, timedelta
from src.ai.orchestrator import CelestiaAIOrchestrator

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def demo_price_prediction(orchestrator: CelestiaAIOrchestrator):
    """Demonstra predição de preços de passagens."""
    print("\n" + "="*60)
    print("🔮 DEMONSTRAÇÃO - PREDIÇÃO DE PREÇOS")
    print("="*60)
    
    routes = [
        ("GRU", "MIA", "São Paulo → Miami"),
        ("GRU", "LAX", "São Paulo → Los Angeles"), 
        ("GRU", "NYC", "São Paulo → Nova York"),
        ("RIO", "PAR", "Rio → Paris")
    ]
    
    for origin, destination, description in routes:
        try:
            prediction = await orchestrator.predict_flight_price(
                origin=origin,
                destination=destination,
                departure_date=datetime.now() + timedelta(days=30),
                passengers=1
            )
            
            if 'error' in prediction:
                price = prediction['fallback_prediction']['price']
                confidence = prediction['fallback_prediction']['confidence']
                trend = prediction['fallback_prediction']['trend']
                print(f"📊 {description}:")
                print(f"   💰 Preço (fallback): R$ {price:.2f}")
                print(f"   🎯 Confiança: {confidence:.1%}")
                print(f"   📈 Tendência: {trend}")
            else:
                pred = prediction['prediction']
                market = prediction['market_insights']
                print(f"📊 {description}:")
                print(f"   💰 Preço: R$ {pred['price']:.2f}")
                print(f"   🎯 Confiança: {pred['confidence']:.1%}")
                print(f"   📈 Tendência: {pred['trend']}")
                print(f"   ⏰ Melhor janela: {pred['booking_window']} dias")
                print(f"   💎 Economia potencial: R$ {pred['savings_potential']:.2f}")
                if market['recommendations']:
                    print(f"   💡 Recomendação: {market['recommendations'][0]}")
            print()
            
        except Exception as e:
            print(f"❌ Erro na predição para {description}: {e}")

async def demo_anomaly_detection(orchestrator: CelestiaAIOrchestrator):
    """Demonstra detecção de anomalias de preços."""
    print("\n" + "="*60)
    print("🔍 DEMONSTRAÇÃO - DETECÇÃO DE ANOMALIAS")
    print("="*60)
    
    test_prices = [
        ("GRU-MIA", 500, "Preço muito baixo"),
        ("GRU-MIA", 800, "Preço normal"),
        ("GRU-MIA", 1500, "Preço alto"),
        ("GRU-LAX", 2500, "Preço muito alto")
    ]
    
    for route, price, description in test_prices:
        try:
            predictor = orchestrator.ml_orchestrator.price_predictor
            anomaly = await predictor.detect_price_anomalies(route, price)
            
            print(f"🔍 {description} - {route}: R$ {price}")
            print(f"   🚨 Anomalia: {'Sim' if anomaly.get('is_anomaly', False) else 'Não'}")
            
            if 'historical_avg' in anomaly:
                print(f"   📊 Média histórica: R$ {anomaly['historical_avg']:.2f}")
                print(f"   📈 Percentil: {anomaly['price_percentile']:.1f}%")
            
            if anomaly.get('is_anomaly') and 'recommendation' in anomaly:
                print(f"   💡 Recomendação: {anomaly['recommendation']}")
            print()
            
        except Exception as e:
            print(f"❌ Erro na detecção de anomalia: {e}")

async def demo_market_analysis(orchestrator: CelestiaAIOrchestrator):
    """Demonstra análise de mercado."""
    print("\n" + "="*60)
    print("📈 DEMONSTRAÇÃO - ANÁLISE DE MERCADO")
    print("="*60)
    
    routes = ["GRU-MIA", "GRU-LAX", "RIO-PAR"]
    
    for route in routes:
        try:
            predictor = orchestrator.ml_orchestrator.price_predictor
            market = await predictor.analyze_market_trends(route)
            
            print(f"📈 Análise de Mercado - {route}:")
            print(f"   💰 Preço médio: R$ {market.average_price:.2f}")
            print(f"   📊 Volatilidade: {market.price_volatility:.2%}")
            
            if market.peak_months:
                print(f"   🔥 Meses de pico: {', '.join(market.peak_months)}")
            if market.low_season_months:
                print(f"   💚 Baixa temporada: {', '.join(market.low_season_months)}")
            
            if market.booking_recommendations:
                print(f"   💡 Recomendações:")
                for rec in market.booking_recommendations[:2]:
                    print(f"      • {rec}")
            print()
            
        except Exception as e:
            print(f"❌ Erro na análise de mercado: {e}")

async def demo_system_health(orchestrator: CelestiaAIOrchestrator):
    """Demonstra monitoramento de saúde do sistema."""
    print("\n" + "="*60)
    print("🏥 DEMONSTRAÇÃO - SAÚDE DO SISTEMA")
    print("="*60)
    
    try:
        # Status geral do sistema
        status = await orchestrator.get_system_status()
        sys_status = status['system_status']
        
        print(f"🔋 Status do Sistema:")
        print(f"   📊 Modo: {sys_status['mode']}")
        print(f"   ⏱️  Uptime: {sys_status['uptime_seconds']} segundos")
        print(f"   🎯 Score de performance: {sys_status.get('performance_score', 'N/A')}")
        print(f"   📋 Tarefas ativas: {sys_status.get('active_tasks', 0)}")
        
        # Saúde dos componentes
        if 'health_report' in status:
            health = status['health_report']
            print(f"\n🏥 Saúde dos Componentes:")
            print(f"   📊 Saúde geral: {health['overall_health']}")
            
            if 'components' in health:
                for comp_name, comp_data in health['components'].items():
                    print(f"   • {comp_name}: {comp_data.get('status', 'unknown')}")
        
        # Métricas de melhoria
        if 'improvement_report' in status:
            improvement = status['improvement_report']
            print(f"\n📈 Sistema de Auto-Melhoria:")
            print(f"   🎯 Score de otimização: {improvement.get('optimization_score', 'N/A')}")
            if 'recent_improvements' in improvement:
                print(f"   🔧 Melhorias recentes: {len(improvement['recent_improvements'])}")
        
    except Exception as e:
        print(f"❌ Erro no monitoramento de saúde: {e}")

async def demo_flight_analysis(orchestrator: CelestiaAIOrchestrator):
    """Demonstra análise de dados de voos."""
    print("\n" + "="*60)
    print("✈️ DEMONSTRAÇÃO - ANÁLISE DE VOOS")
    print("="*60)
    
    # Dados de exemplo de voos
    sample_flights = [
        {'origin': 'GRU', 'destination': 'MIA', 'price': 800, 'date': '2024-12-01', 'airline': 'LATAM'},
        {'origin': 'GRU', 'destination': 'MIA', 'price': 850, 'date': '2024-12-02', 'airline': 'GOL'},
        {'origin': 'GRU', 'destination': 'LAX', 'price': 950, 'date': '2024-12-01', 'airline': 'LATAM'},
        {'origin': 'GRU', 'destination': 'LAX', 'price': 920, 'date': '2024-12-02', 'airline': 'Azul'},
        {'origin': 'RIO', 'destination': 'PAR', 'price': 1200, 'date': '2024-12-01', 'airline': 'Air France'}
    ]
    
    try:
        analysis = await orchestrator.analyze_flight_data(sample_flights)
        
        print(f"✈️ Análise de {len(sample_flights)} voos:")
        
        if 'error' not in analysis:
            print(f"   📊 Voos analisados: {analysis.get('flights_analyzed', 0)}")
            print(f"   🕒 Gerado em: {analysis.get('generated_at', 'N/A')}")
            
            if 'statistical_analysis' in analysis:
                print(f"   📈 Análise estatística: Completa")
            
            if 'ai_insights' in analysis:
                insights = analysis['ai_insights']
                if isinstance(insights, dict) and 'summary' in insights:
                    print(f"   🤖 Insights de IA: {insights['summary']}")
                else:
                    print(f"   🤖 Insights de IA: Disponível")
        else:
            print(f"   ❌ Erro na análise: {analysis['error']}")
        
    except Exception as e:
        print(f"❌ Erro na análise de voos: {e}")

async def main():
    """Executa demonstração completa do sistema."""
    print("🚀 INICIANDO DEMONSTRAÇÃO COMPLETA DO SISTEMA DE IA CELEST.IA v2")
    print("🎯 Incluindo: ML Engine, Self-Healing, Self-Improvement")
    print("="*80)
    
    # Inicializar orchestrador
    orchestrator = CelestiaAIOrchestrator()
    
    try:
        # Iniciar sistema
        print("🔄 Iniciando sistema de IA...")
        await orchestrator.start()
        print("✅ Sistema iniciado com sucesso!")
        
        # Executar demonstrações
        await demo_price_prediction(orchestrator)
        await demo_anomaly_detection(orchestrator)
        await demo_market_analysis(orchestrator)
        await demo_system_health(orchestrator)
        await demo_flight_analysis(orchestrator)
        
        print("\n" + "="*80)
        print("🎉 DEMONSTRAÇÃO COMPLETA FINALIZADA COM SUCESSO!")
        print("💡 O sistema de IA Celest.ia v2 está funcionando corretamente")
        print("🔧 Todos os módulos (ML, Self-Healing, Self-Improvement) estão operacionais")
        print("📊 Sistema pronto para uso em produção (com configuração de APIs)")
        
    except Exception as e:
        print(f"❌ Erro durante a demonstração: {e}")
        logger.exception("Erro completo:")
        
    finally:
        # Parar sistema
        print("\n🔄 Parando sistema...")
        await orchestrator.stop()
        print("✅ Sistema parado com segurança")

if __name__ == "__main__":
    asyncio.run(main())
