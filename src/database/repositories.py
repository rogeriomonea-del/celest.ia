"""Repository classes for database operations."""
from __future__ import annotations

from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_, or_, func
from loguru import logger

from ..core.database import SessionLocal
from .models import (
    User, FlightSearch, Flight, PriceHistory, 
    UserPreference, LoyaltyAccount, MilesBalanceHistory, 
    AlertRule, AnalysisCache
)


class BaseRepository:
    """Base repository with common operations."""
    
    def __init__(self, model_class):
        """Initialize repository with model class."""
        self.model_class = model_class
    
    def get_db(self) -> Session:
        """Get database session."""
        return SessionLocal()
    
    async def create(self, data: Dict[str, Any]) -> Any:
        """Create new record."""
        with self.get_db() as db:
            try:
                instance = self.model_class(**data)
                db.add(instance)
                db.commit()
                db.refresh(instance)
                return instance
            except Exception as e:
                db.rollback()
                logger.error(f"Create failed: {e}")
                raise
    
    async def get_by_id(self, id: str) -> Optional[Any]:
        """Get record by ID."""
        with self.get_db() as db:
            return db.query(self.model_class).filter(self.model_class.id == id).first()
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Any]:
        """Update record."""
        with self.get_db() as db:
            try:
                instance = db.query(self.model_class).filter(self.model_class.id == id).first()
                if instance:
                    for key, value in data.items():
                        setattr(instance, key, value)
                    db.commit()
                    db.refresh(instance)
                return instance
            except Exception as e:
                db.rollback()
                logger.error(f"Update failed: {e}")
                raise
    
    async def delete(self, id: str) -> bool:
        """Delete record."""
        with self.get_db() as db:
            try:
                instance = db.query(self.model_class).filter(self.model_class.id == id).first()
                if instance:
                    db.delete(instance)
                    db.commit()
                    return True
                return False
            except Exception as e:
                db.rollback()
                logger.error(f"Delete failed: {e}")
                raise


class UserRepository(BaseRepository):
    """User repository."""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_telegram_id(self, telegram_user_id: str) -> Optional[User]:
        """Get user by Telegram user ID."""
        with self.get_db() as db:
            return db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        with self.get_db() as db:
            return db.query(User).filter(User.email == email).first()
    
    async def create_or_update_telegram_user(self, telegram_data: Dict[str, Any]) -> User:
        """Create or update user from Telegram data."""
        with self.get_db() as db:
            telegram_id = str(telegram_data.get('id'))
            
            user = db.query(User).filter(User.telegram_user_id == telegram_id).first()
            
            if user:
                # Update existing user
                user.username = telegram_data.get('username')
                user.first_name = telegram_data.get('first_name')
                user.last_name = telegram_data.get('last_name')
                user.updated_at = datetime.utcnow()
            else:
                # Create new user
                user = User(
                    telegram_user_id=telegram_id,
                    username=telegram_data.get('username'),
                    first_name=telegram_data.get('first_name'),
                    last_name=telegram_data.get('last_name')
                )
                db.add(user)
            
            db.commit()
            db.refresh(user)
            return user


class FlightRepository(BaseRepository):
    """Flight repository."""
    
    def __init__(self):
        super().__init__(Flight)
    
    async def create_flight(self, flight_data: Dict[str, Any]) -> Flight:
        """Create a new flight record."""
        with self.get_db() as db:
            try:
                # Convert datetime strings to datetime objects
                if 'departure_time' in flight_data and isinstance(flight_data['departure_time'], str):
                    flight_data['departure_time'] = datetime.fromisoformat(flight_data['departure_time'])
                if 'arrival_time' in flight_data and isinstance(flight_data['arrival_time'], str):
                    flight_data['arrival_time'] = datetime.fromisoformat(flight_data['arrival_time'])
                
                flight = Flight(**flight_data)
                db.add(flight)
                db.commit()
                db.refresh(flight)
                return flight
            except Exception as e:
                db.rollback()
                logger.error(f"Create flight failed: {e}")
                raise
    
    async def get_flights_by_route(
        self,
        origin: str,
        destination: str,
        days_back: int = 30
    ) -> List[Flight]:
        """Get flights for a specific route."""
        with self.get_db() as db:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            return db.query(Flight).filter(
                and_(
                    Flight.origin == origin.upper(),
                    Flight.destination == destination.upper(),
                    Flight.created_at >= cutoff_date
                )
            ).order_by(desc(Flight.created_at)).all()
    
    async def get_price_history(
        self,
        origin: str,
        destination: str,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Get price history for trend analysis."""
        flights = await self.get_flights_by_route(origin, destination, days_back)
        
        price_history = []
        for flight in flights:
            price_history.append({
                'price': flight.price,
                'timestamp': flight.created_at,
                'airline': flight.airline,
                'source': flight.source
            })
        
        return price_history
    
    async def get_cheapest_flights(
        self,
        origin: str,
        destination: str,
        limit: int = 10
    ) -> List[Flight]:
        """Get cheapest flights for a route."""
        with self.get_db() as db:
            return db.query(Flight).filter(
                and_(
                    Flight.origin == origin.upper(),
                    Flight.destination == destination.upper()
                )
            ).order_by(asc(Flight.price)).limit(limit).all()


class FlightSearchRepository(BaseRepository):
    """Flight search repository."""
    
    def __init__(self):
        super().__init__(FlightSearch)
    
    async def create_search(self, search_data: Dict[str, Any]) -> FlightSearch:
        """Create a new flight search record."""
        return await self.create(search_data)
    
    async def get_user_searches(self, user_id: str, limit: int = 50) -> List[FlightSearch]:
        """Get user's search history."""
        with self.get_db() as db:
            return db.query(FlightSearch).filter(
                FlightSearch.user_id == user_id
            ).order_by(desc(FlightSearch.search_timestamp)).limit(limit).all()
    
    async def get_popular_routes(self, days_back: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most searched routes."""
        with self.get_db() as db:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            results = db.query(
                FlightSearch.origin,
                FlightSearch.destination,
                func.count(FlightSearch.id).label('search_count')
            ).filter(
                FlightSearch.search_timestamp >= cutoff_date
            ).group_by(
                FlightSearch.origin, FlightSearch.destination
            ).order_by(
                desc('search_count')
            ).limit(limit).all()
            
            return [
                {
                    'origin': r.origin,
                    'destination': r.destination,
                    'search_count': r.search_count
                }
                for r in results
            ]


class PriceHistoryRepository(BaseRepository):
    """Price history repository."""
    
    def __init__(self):
        super().__init__(PriceHistory)
    
    async def add_daily_price_summary(
        self,
        origin: str,
        destination: str,
        flights: List[Flight],
        date: date
    ) -> PriceHistory:
        """Add daily price summary from flight data."""
        if not flights:
            return None
        
        prices = [f.price for f in flights if f.price > 0]
        if not prices:
            return None
        
        price_data = {
            'origin': origin.upper(),
            'destination': destination.upper(),
            'date': date,
            'min_price': min(prices),
            'avg_price': sum(prices) / len(prices),
            'max_price': max(prices),
            'sample_size': len(prices),
            'currency': flights[0].currency,
            'data_source': 'flight_aggregation'
        }
        
        return await self.create(price_data)
    
    async def get_price_trends(
        self,
        origin: str,
        destination: str,
        days_back: int = 30
    ) -> List[PriceHistory]:
        """Get price trends for a route."""
        with self.get_db() as db:
            cutoff_date = date.today() - timedelta(days=days_back)
            
            return db.query(PriceHistory).filter(
                and_(
                    PriceHistory.origin == origin.upper(),
                    PriceHistory.destination == destination.upper(),
                    PriceHistory.date >= cutoff_date
                )
            ).order_by(asc(PriceHistory.date)).all()


class LoyaltyAccountRepository(BaseRepository):
    """Loyalty account repository."""
    
    def __init__(self):
        super().__init__(LoyaltyAccount)
    
    async def get_user_accounts(self, user_id: str) -> List[LoyaltyAccount]:
        """Get user's loyalty accounts."""
        with self.get_db() as db:
            return db.query(LoyaltyAccount).filter(
                and_(
                    LoyaltyAccount.user_id == user_id,
                    LoyaltyAccount.is_active == True
                )
            ).all()
    
    async def update_balance(
        self,
        account_id: str,
        balance_data: Dict[str, Any]
    ) -> LoyaltyAccount:
        """Update account balance."""
        with self.get_db() as db:
            try:
                account = db.query(LoyaltyAccount).filter(LoyaltyAccount.id == account_id).first()
                if account:
                    # Update account
                    account.available_miles = balance_data.get('available_miles')
                    account.expiring_miles = balance_data.get('expiring_miles')
                    account.tier_status = balance_data.get('tier_status')
                    account.last_checked = datetime.utcnow()
                    account.updated_at = datetime.utcnow()
                    
                    # Add to history
                    history = MilesBalanceHistory(
                        account_id=account_id,
                        available_miles=balance_data.get('available_miles'),
                        expiring_miles=balance_data.get('expiring_miles'),
                        tier_status=balance_data.get('tier_status')
                    )
                    db.add(history)
                    
                    db.commit()
                    db.refresh(account)
                
                return account
            except Exception as e:
                db.rollback()
                logger.error(f"Update balance failed: {e}")
                raise


class AnalysisCacheRepository(BaseRepository):
    """Analysis cache repository."""
    
    def __init__(self):
        super().__init__(AnalysisCache)
    
    async def get_cached_analysis(self, cache_key: str) -> Optional[AnalysisCache]:
        """Get cached analysis if not expired."""
        with self.get_db() as db:
            now = datetime.utcnow()
            
            cache = db.query(AnalysisCache).filter(
                and_(
                    AnalysisCache.cache_key == cache_key,
                    or_(
                        AnalysisCache.expires_at.is_(None),
                        AnalysisCache.expires_at > now
                    )
                )
            ).first()
            
            if cache:
                # Increment hit count
                cache.hit_count += 1
                db.commit()
            
            return cache
    
    async def cache_analysis(
        self,
        cache_key: str,
        analysis_type: str,
        results: Dict[str, Any],
        expires_in_hours: int = 24
    ) -> AnalysisCache:
        """Cache analysis results."""
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        cache_data = {
            'cache_key': cache_key,
            'analysis_type': analysis_type,
            'results': results,
            'expires_at': expires_at
        }
        
        return await self.create(cache_data)
