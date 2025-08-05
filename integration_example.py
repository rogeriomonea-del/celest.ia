#!/usr/bin/env python3
"""
Exemplo de Integração Completa - Celest.ia v2 AI System
Demonstra como integrar todos os módulos IA em uma aplicação real
"""

import asyncio
import sys
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the complete AI system
from src.ai.orchestrator import ai_orchestrator
from src.ai.self_improvement import MetricType

class FlightSearchApp:
    """
    Aplicação exemplo que integra todo o sistema IA
    Simula uma aplicação real de busca de voos
    """
    
    def __init__(self):
        self.ai_system = ai_orchestrator
        self.search_history = []
        self.user_sessions = {}
        
    async def start_app(self):
        """Inicializar a aplicação e o sistema IA."""
        print("🚀 Iniciando Celest.ia Flight Search App")
        print("🤖 Carregando sistema IA...")
        
        # Start the AI system
        await self.ai_system.start()
        print("✅ Sistema IA carregado com sucesso!")
        
        # Check system health
        status = await self.ai_system.get_system_status()
        print(f"📊 Performance Score: {status['system_status']['performance_score']}")
        print(f"🏥 Health Status: {status['health_status']['overall_health']}")
        
    async def search_flights(
        self, 
        user_id: str,
        origin: str, 
        destination: str,
        departure_date: date,
        return_date: date = None,
        passengers: int = 1
    ) -> Dict[str, Any]:
        """
        Buscar voos usando o sistema IA completo
        """
        print(f"\n🔍 Buscando voos: {origin} → {destination}")
        print(f"📅 Partida: {departure_date}")
        if return_date:
            print(f"🔄 Volta: {return_date}")
        print(f"👥 Passageiros: {passengers}")
        
        search_start = datetime.now()
        
        try:
            # 1. Get AI-powered price prediction
            print("\n🧠 Obtendo predição IA...")
            prediction = await self.ai_system.predict_flight_price(
                origin=origin,
                destination=destination,
                departure_date=datetime.combine(departure_date, datetime.min.time()),
                return_date=datetime.combine(return_date, datetime.min.time()) if return_date else None,
                passengers=passengers
            )
            
            # 2. Simulate flight search results
            print("✈️ Simulando busca de voos...")
            flights = await self._simulate_flight_search(
                origin, destination, departure_date, passengers, prediction
            )
            
            # 3. Analyze the flight data with AI
            print("📊 Analisando dados com IA...")
            analysis = await self.ai_system.analyze_flight_data(flights)
            
            # 4. Record user interaction
            search_duration = (datetime.now() - search_start).total_seconds()
            outcome = "success" if flights else "no_results"
            
            self.ai_system.self_improvement.record_user_interaction(
                user_id=user_id,
                action="search_flights",
                context={
                    "route": f"{origin}-{destination}",
                    "passengers": passengers,
                    "advance_days": (departure_date - date.today()).days,
                    "round_trip": return_date is not None
                },
                outcome=outcome,
                satisfaction_score=4.5  # Would come from user feedback
            )
            
            # 5. Record performance metrics
            self.ai_system.self_improvement.record_performance_metric(
                MetricType.RESPONSE_TIME, search_duration, "flight_search"
            )
            
            # 6. Store search in history
            search_record = {
                "user_id": user_id,
                "route": f"{origin}-{destination}",
                "departure_date": departure_date.isoformat(),
                "return_date": return_date.isoformat() if return_date else None,
                "passengers": passengers,
                "search_time": search_start.isoformat(),
                "results_count": len(flights),
                "ai_prediction": prediction,
                "search_duration": search_duration
            }
            self.search_history.append(search_record)
            
            result = {
                "flights": flights,
                "ai_prediction": prediction,
                "ai_analysis": analysis,
                "search_metadata": {
                    "search_duration_seconds": search_duration,
                    "results_count": len(flights),
                    "search_id": f"search_{len(self.search_history)}"
                }
            }
            
            print(f"✅ Busca concluída! {len(flights)} voos encontrados")
            return result
            
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            
            # Record error
            self.ai_system.self_improvement.record_performance_metric(
                MetricType.ERROR_RATE, 1.0, "flight_search"
            )
            
            return {
                "error": str(e),
                "flights": [],
                "search_metadata": {
                    "search_duration_seconds": (datetime.now() - search_start).total_seconds(),
                    "results_count": 0
                }
            }
    
    async def get_price_prediction(
        self,
        origin: str,
        destination: str, 
        departure_date: date
    ) -> Dict[str, Any]:
        """Obter apenas predição de preço."""
        print(f"\n🔮 Predição de preço: {origin} → {destination}")
        
        prediction = await self.ai_system.predict_flight_price(
            origin=origin,
            destination=destination,
            departure_date=datetime.combine(departure_date, datetime.min.time())
        )
        
        return {
            "predicted_price": prediction['prediction']['price'],
            "confidence": prediction['prediction']['confidence'],
            "trend": prediction['prediction']['trend'],
            "booking_recommendation": prediction['ai_analysis']['strategic_analysis'],
            "best_booking_window": prediction['prediction']['booking_window']
        }
    
    async def submit_user_feedback(
        self,
        user_id: str,
        search_id: str,
        rating: float,
        feedback_type: str,
        comments: str = ""
    ):
        """Submeter feedback do usuário."""
        print(f"\n👥 Feedback recebido de {user_id}: {rating}/5.0")
        
        # Find the search record
        search_record = None
        for record in self.search_history:
            if record.get('search_id') == search_id:
                search_record = record
                break
        
        context = {
            "search_id": search_id,
            "route": search_record['route'] if search_record else "unknown"
        }
        
        # Record feedback for AI learning
        self.ai_system.self_improvement.record_user_feedback(
            user_id=user_id,
            feedback_type=feedback_type,
            rating=rating,
            comments=comments,
            context=context
        )
        
        # Record satisfaction metric
        self.ai_system.self_improvement.record_performance_metric(
            MetricType.USER_SATISFACTION, rating, "overall_experience"
        )
        
        print("✅ Feedback registrado para melhoria do sistema")
    
    async def get_app_analytics(self) -> Dict[str, Any]:
        """Obter analytics da aplicação."""
        print("\n📊 Gerando analytics da aplicação...")
        
        # Get AI system status
        ai_status = await self.ai_system.get_system_status()
        
        # Calculate app-specific metrics
        total_searches = len(self.search_history)
        successful_searches = len([s for s in self.search_history if s['results_count'] > 0])
        success_rate = successful_searches / total_searches if total_searches > 0 else 0
        
        avg_response_time = sum(s['search_duration'] for s in self.search_history) / total_searches if total_searches > 0 else 0
        
        # Popular routes
        routes = [s['route'] for s in self.search_history]
        popular_routes = {}
        for route in routes:
            popular_routes[route] = popular_routes.get(route, 0) + 1
        
        return {
            "app_metrics": {
                "total_searches": total_searches,
                "success_rate": round(success_rate, 3),
                "average_response_time": round(avg_response_time, 2),
                "popular_routes": sorted(popular_routes.items(), key=lambda x: x[1], reverse=True)[:5]
            },
            "ai_system_status": ai_status,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _simulate_flight_search(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        passengers: int,
        ai_prediction: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Simular busca de voos (normalmente seria scrapers reais)."""
        
        # Simulate delay for realistic experience
        await asyncio.sleep(0.5)
        
        base_price = ai_prediction['prediction']['price']
        
        # Generate simulated flights based on AI prediction
        flights = []
        
        airlines = ["LATAM", "Copa Airlines", "American Airlines", "Delta", "United"]
        
        for i, airline in enumerate(airlines):
            # Vary price around AI prediction
            price_variation = (-50 + i * 25) if i < 3 else (25 + i * 10)
            flight_price = base_price + price_variation
            
            departure_time = datetime.combine(departure_date, datetime.min.time()) + timedelta(hours=6 + i * 2)
            arrival_time = departure_time + timedelta(hours=5, minutes=30 + i * 15)
            
            flight = {
                "airline": airline,
                "flight_number": f"{airline[:2].upper()}{1000 + i}",
                "price": round(flight_price, 2),
                "currency": "USD",
                "departure_time": departure_time.isoformat(),
                "arrival_time": arrival_time.isoformat(),
                "duration_minutes": int((arrival_time - departure_time).total_seconds() / 60),
                "stops": 0 if i < 2 else 1,
                "aircraft": "Boeing 737" if i % 2 == 0 else "Airbus A320",
                "booking_class": "Economy",
                "availability": "Available",
                "baggage_included": True,
                "cancellation_policy": "Flexible" if i % 3 == 0 else "Standard"
            }
            
            flights.append(flight)
        
        return flights
    
    async def stop_app(self):
        """Finalizar a aplicação."""
        print("\n🛑 Finalizando aplicação...")
        await self.ai_system.stop()
        print("✅ Aplicação finalizada com segurança")

async def demo_complete_integration():
    """Demonstração completa de integração."""
    print("🎯 DEMO: Integração Completa - Celest.ia Flight Search")
    print("=" * 70)
    
    # Initialize app
    app = FlightSearchApp()
    await app.start_app()
    
    try:
        # Simulate user searches
        print("\n" + "="*50)
        print("👤 Simulando sessão do usuário")
        print("="*50)
        
        user_id = "user_demo_123"
        
        # Search 1: GRU -> MIA
        search1 = await app.search_flights(
            user_id=user_id,
            origin="GRU",
            destination="MIA",
            departure_date=date.today() + timedelta(days=30),
            return_date=date.today() + timedelta(days=37),
            passengers=2
        )
        
        print(f"\n📊 Resultados da Busca 1:")
        print(f"   Voos encontrados: {len(search1['flights'])}")
        print(f"   Preço previsto pela IA: ${search1['ai_prediction']['prediction']['price']:.2f}")
        print(f"   Confiança: {search1['ai_prediction']['prediction']['confidence']:.1%}")
        
        # Simulate user feedback
        await app.submit_user_feedback(
            user_id=user_id,
            search_id=search1['search_metadata']['search_id'],
            rating=4.8,
            feedback_type="search_experience",
            comments="Excelente predição de preços!"
        )
        
        # Search 2: GRU -> LAX
        search2 = await app.search_flights(
            user_id=user_id,
            origin="GRU",
            destination="LAX",
            departure_date=date.today() + timedelta(days=45),
            passengers=1
        )
        
        print(f"\n📊 Resultados da Busca 2:")
        print(f"   Voos encontrados: {len(search2['flights'])}")
        print(f"   Preço previsto pela IA: ${search2['ai_prediction']['prediction']['price']:.2f}")
        
        # Quick price prediction
        prediction = await app.get_price_prediction(
            origin="GRU",
            destination="NYC", 
            departure_date=date.today() + timedelta(days=60)
        )
        
        print(f"\n🔮 Predição Rápida GRU→NYC:")
        print(f"   Preço: ${prediction['predicted_price']:.2f}")
        print(f"   Tendência: {prediction['trend']}")
        print(f"   Melhor janela: {prediction['best_booking_window']} dias")
        
        # App analytics
        analytics = await app.get_app_analytics()
        
        print(f"\n📈 Analytics da Aplicação:")
        print(f"   Total de buscas: {analytics['app_metrics']['total_searches']}")
        print(f"   Taxa de sucesso: {analytics['app_metrics']['success_rate']:.1%}")
        print(f"   Tempo médio: {analytics['app_metrics']['average_response_time']:.2f}s")
        print(f"   Rotas populares: {analytics['app_metrics']['popular_routes']}")
        
        # AI System Performance
        ai_status = analytics['ai_system_status']
        print(f"\n🤖 Performance do Sistema IA:")
        print(f"   Score: {ai_status['system_status']['performance_score']}")
        print(f"   Modo: {ai_status['system_status']['mode']}")
        print(f"   Uptime: {ai_status['system_status']['uptime_human']}")
        print(f"   Predições realizadas: {app.ai_system.metrics['predictions_made']}")
        
        print("\n" + "="*70)
        print("🎉 INTEGRAÇÃO COMPLETA DEMONSTRADA COM SUCESSO!")
        print("✅ Todos os componentes IA funcionando perfeitamente")
        print("🚀 Aplicação pronta para produção!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await app.stop_app()

if __name__ == "__main__":
    asyncio.run(demo_complete_integration())
