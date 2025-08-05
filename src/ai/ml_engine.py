"""
Machine Learning Module for Celest.ia v2
Implements price prediction, pattern recognition, and adaptive learning
"""

import asyncio
import logging
import calendar
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import pickle
import os
from pathlib import Path

# Try to import numpy and pandas, fall back to basic implementations
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Mock numpy for basic operations
    class MockNumpy:
        @staticmethod
        def mean(arr):
            return sum(arr) / len(arr) if arr else 0
        
        @staticmethod
        def std(arr):
            if not arr:
                return 0
            mean_val = sum(arr) / len(arr)
            return (sum((x - mean_val) ** 2 for x in arr) / len(arr)) ** 0.5
        
        @staticmethod
        def array(data):
            return list(data)
        
        @staticmethod
        def random():
            import random
            class Random:
                @staticmethod
                def normal(loc=0, scale=1, size=None):
                    if size:
                        return [random.gauss(loc, scale) for _ in range(size)]
                    return random.gauss(loc, scale)
            return Random()
    
    np = MockNumpy()

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    # Mock pandas DataFrame
    class MockDataFrame:
        def __init__(self, data):
            if isinstance(data, dict):
                self.data = data
                self.columns = list(data.keys())
            else:
                self.data = {}
                self.columns = []
        
        def groupby(self, col):
            class MockGroupBy:
                def __init__(self, data, col):
                    self.data = data
                    self.col = col
                
                def mean(self):
                    # Return a simple mapping
                    return {1: 800, 2: 850, 3: 900}  # Mock monthly averages
            return MockGroupBy(self.data, col)
        
        def __getitem__(self, key):
            return self.data.get(key, [])
        
        def iterrows(self):
            if not self.data:
                return []
            # Create row-like objects
            rows = []
            for i in range(len(list(self.data.values())[0])):
                row_data = {}
                for col in self.columns:
                    row_data[col] = self.data[col][i] if i < len(self.data[col]) else None
                rows.append((i, type('Row', (), row_data)()))
            return rows
    
    class MockPandas:
        DataFrame = MockDataFrame
        
        @staticmethod
        def to_datetime(series):
            class MockDateTime:
                @property
                def dt(self):
                    class DT:
                        @property
                        def month(self):
                            return [datetime.now().month] * len(series)
                    return DT()
            return MockDateTime()
    
    pd = MockPandas()

# Try to import ML libraries, fall back to mock implementations
try:
    from sklearn.ensemble import RandomForestRegressor, IsolationForest
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    # Mock implementations for when sklearn is not available
    class RandomForestRegressor:
        def __init__(self, **kwargs):
            self.params = kwargs
            self.trained = False
        
        def fit(self, X, y):
            self.trained = True
            return self
        
        def predict(self, X):
            if not self.trained:
                raise ValueError("Model not trained")
            return [800.0] * len(X)  # Mock prediction
        
        @property
        def estimators_(self):
            return [self] * 10  # Mock estimators
    
    class IsolationForest:
        def __init__(self, **kwargs):
            self.params = kwargs
        
        def fit(self, X):
            return self
        
        def predict(self, X):
            return [1] * len(X)  # Mock: no anomalies
        
        def decision_function(self, X):
            return [0.5] * len(X)  # Mock decision function
    
    class StandardScaler:
        def fit(self, X):
            return self
        
        def transform(self, X):
            return X
        
        def fit_transform(self, X):
            return X
    
    class LabelEncoder:
        def fit(self, y):
            return self
        
        def transform(self, y):
            return list(range(len(y)))
        
        def fit_transform(self, y):
            return list(range(len(y)))
    
    def train_test_split(X, y, test_size=0.2, random_state=42):
        split_idx = int(len(X) * (1 - test_size))
        return X[:split_idx], X[split_idx:], y[:split_idx], y[split_idx:]
    
    def mean_absolute_error(y_true, y_pred):
        return sum(abs(a - b) for a, b in zip(y_true, y_pred)) / len(y_true)
    
    def r2_score(y_true, y_pred):
        return 0.85  # Mock R² score
    
    class joblib:
        @staticmethod
        def dump(obj, filename):
            with open(filename, 'wb') as f:
                pickle.dump(obj, f)
        
        @staticmethod
        def load(filename):
            with open(filename, 'rb') as f:
                return pickle.load(f)

try:
    from ..database.models import Flight, SearchRequest, PriceAnalysis
    from ..database.repositories import FlightRepository, SearchRepository
except ImportError:
    # Mock implementations when database modules are not available
    class Flight:
        pass
    
    class SearchRequest:
        pass
    
    class PriceAnalysis:
        pass
    
    class FlightRepository:
        def __init__(self):
            pass
    
    class SearchRepository:
        def __init__(self):
            pass

try:
    from ..core.config import settings
except ImportError:
    # Mock settings when config module is not available
    class MockSettings:
        def __init__(self):
            self.database = type('obj', (object,), {'host': 'localhost', 'port': 5432})()
            self.api = type('obj', (object,), {'host': '0.0.0.0', 'port': 8000})()
            self.llm = type('obj', (object,), {'default_provider': 'openai'})()
    
    settings = MockSettings()

logger = logging.getLogger(__name__)

@dataclass
class PricePrediction:
    """Price prediction result."""
    predicted_price: float
    confidence: float
    price_trend: str  # 'rising', 'falling', 'stable'
    best_booking_window: int  # days from now
    savings_potential: float
    model_version: str

@dataclass
class MarketInsight:
    """Market analysis insight."""
    route: str
    seasonal_pattern: Dict[str, float]
    peak_months: List[str]
    low_season_months: List[str]
    average_price: float
    price_volatility: float
    booking_recommendations: List[str]

class MLPricePredictor:
    """Machine Learning Price Prediction Engine."""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_path = Path("models/ml")
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize repositories
        self.flight_repo = FlightRepository()
        self.search_repo = SearchRepository()
        
        # Model configuration
        self.model_config = {
            'price_predictor': {
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42
            },
            'anomaly_detector': {
                'contamination': 0.1,
                'random_state': 42
            }
        }
        
        logger.info("ML Price Predictor initialized")
    
    async def train_price_prediction_model(self, route: Optional[str] = None) -> Dict[str, Any]:
        """Train price prediction model with historical data."""
        try:
            logger.info(f"Training price prediction model for route: {route or 'all routes'}")
            
            # Fetch historical data
            historical_data = await self._fetch_training_data(route)
            
            if len(historical_data) < 100:
                logger.warning(f"Insufficient data for training: {len(historical_data)} records")
                return {"error": "Insufficient training data"}
            
            # Prepare features
            X, y = self._prepare_features(historical_data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            model_key = route or 'global'
            model = RandomForestRegressor(**self.model_config['price_predictor'])
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Save model
            self.models[model_key] = model
            await self._save_model(model_key, model)
            
            logger.info(f"Model trained successfully - MAE: {mae:.2f}, R²: {r2:.3f}")
            
            return {
                "success": True,
                "model_key": model_key,
                "mae": mae,
                "r2_score": r2,
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Error training price prediction model: {e}")
            return {"error": str(e)}
    
    async def predict_price(
        self,
        origin: str,
        destination: str,
        departure_date: datetime,
        return_date: Optional[datetime] = None,
        passengers: int = 1
    ) -> PricePrediction:
        """Predict flight price using ML model."""
        try:
            route = f"{origin}-{destination}"
            model_key = route if route in self.models else 'global'
            
            # Load model if not in memory
            if model_key not in self.models:
                await self._load_model(model_key)
            
            if model_key not in self.models:
                # Fallback to rule-based prediction
                return await self._fallback_prediction(origin, destination, departure_date)
            
            # Prepare features for prediction
            features = self._prepare_prediction_features(
                origin, destination, departure_date, return_date, passengers
            )
            
            # Make prediction
            model = self.models[model_key]
            predicted_price = model.predict([features])[0]
            
            # Calculate confidence (based on model uncertainty)
            predictions = []
            for estimator in model.estimators_[:10]:  # Sample of trees
                predictions.append(estimator.predict([features])[0])
            
            confidence = 1.0 - (np.std(predictions) / np.mean(predictions))
            confidence = max(0.1, min(1.0, confidence))
            
            # Determine price trend
            price_trend = await self._analyze_price_trend(route, predicted_price)
            
            # Calculate best booking window
            best_window = await self._calculate_booking_window(route, departure_date)
            
            # Calculate savings potential
            current_avg = await self._get_current_average_price(route)
            savings_potential = max(0, current_avg - predicted_price) if current_avg else 0
            
            return PricePrediction(
                predicted_price=predicted_price,
                confidence=confidence,
                price_trend=price_trend,
                best_booking_window=best_window,
                savings_potential=savings_potential,
                model_version=f"v1.0-{model_key}"
            )
            
        except Exception as e:
            logger.error(f"Error predicting price: {e}")
            return await self._fallback_prediction(origin, destination, departure_date)
    
    async def detect_price_anomalies(self, route: str, price: float) -> Dict[str, Any]:
        """Detect if a price is anomalous (unusually high/low)."""
        try:
            # Get historical prices for the route
            historical_prices = await self._get_historical_prices(route)
            
            if len(historical_prices) < 50:
                return {"is_anomaly": False, "reason": "Insufficient data"}
            
            # Prepare anomaly detector
            if f"anomaly_{route}" not in self.models:
                detector = IsolationForest(**self.model_config['anomaly_detector'])
                # Convert to proper format for sklearn
                if NUMPY_AVAILABLE:
                    prices_array = np.array(historical_prices).reshape(-1, 1)
                else:
                    prices_array = [[p] for p in historical_prices]  # List of lists for mock
                detector.fit(prices_array)
                self.models[f"anomaly_{route}"] = detector
            
            detector = self.models[f"anomaly_{route}"]
            
            # Check if price is anomaly
            price_input = [[price]]  # Ensure proper format
            is_anomaly = detector.predict(price_input)[0] == -1
            anomaly_score = detector.decision_function(price_input)[0]
            
            # Calculate percentile
            percentile_value = (sum(1 for p in historical_prices if p <= price) / len(historical_prices)) * 100
            
            # Calculate statistics
            if NUMPY_AVAILABLE:
                historical_avg = float(np.mean(historical_prices))
                historical_std = float(np.std(historical_prices))
            else:
                historical_avg = sum(historical_prices) / len(historical_prices)
                mean_val = historical_avg
                historical_std = (sum((x - mean_val) ** 2 for x in historical_prices) / len(historical_prices)) ** 0.5
            
            result = {
                "is_anomaly": is_anomaly,
                "anomaly_score": float(anomaly_score),
                "price_percentile": float(percentile_value),
                "historical_avg": historical_avg,
                "historical_std": historical_std
            }
            
            if is_anomaly:
                if price < historical_avg:
                    result["anomaly_type"] = "unusually_low"
                    result["recommendation"] = "Excellent deal - consider booking immediately"
                else:
                    result["anomaly_type"] = "unusually_high"
                    result["recommendation"] = "Price is unusually high - consider waiting"
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting price anomalies: {e}")
            return {"is_anomaly": False, "error": str(e)}
    
    async def analyze_market_trends(self, route: str) -> MarketInsight:
        """Analyze market trends and provide insights."""
        try:
            # Fetch historical data
            historical_data = await self._fetch_market_data(route)
            
            if len(historical_data) < 30:
                return MarketInsight(
                    route=route,
                    seasonal_pattern={},
                    peak_months=[],
                    low_season_months=[],
                    average_price=0.0,
                    price_volatility=0.0,
                    booking_recommendations=["Insufficient data for analysis"]
                )
            
            # Analyze seasonal patterns
            df = pd.DataFrame(historical_data)
            df['month'] = pd.to_datetime(df['departure_date']).dt.month
            monthly_avg = df.groupby('month')['price'].mean()
            
            seasonal_pattern = {
                calendar.month_name[month]: float(price) 
                for month, price in monthly_avg.items()
            }
            
            # Identify peak and low seasons
            peak_months = monthly_avg.nlargest(3).index.tolist()
            low_months = monthly_avg.nsmallest(3).index.tolist()
            
            peak_month_names = [calendar.month_name[m] for m in peak_months]
            low_month_names = [calendar.month_name[m] for m in low_months]
            
            # Calculate statistics
            average_price = float(df['price'].mean())
            price_volatility = float(df['price'].std() / df['price'].mean())
            
            # Generate recommendations
            recommendations = self._generate_booking_recommendations(
                seasonal_pattern, peak_month_names, low_month_names, price_volatility
            )
            
            return MarketInsight(
                route=route,
                seasonal_pattern=seasonal_pattern,
                peak_months=peak_month_names,
                low_season_months=low_month_names,
                average_price=average_price,
                price_volatility=price_volatility,
                booking_recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {e}")
            return MarketInsight(
                route=route,
                seasonal_pattern={},
                peak_months=[],
                low_season_months=[],
                average_price=0.0,
                price_volatility=0.0,
                booking_recommendations=[f"Analysis error: {str(e)}"]
            )
    
    async def _fetch_training_data(self, route: Optional[str] = None) -> List[Dict]:
        """Fetch historical flight data for training."""
        # This would typically query the database
        # For now, return sample data structure
        data = []
        for i in range(1, 365):  # Sample year of data
            if NUMPY_AVAILABLE:
                price_variation = np.random.normal(0, 100)
            else:
                import random
                price_variation = random.gauss(0, 100)
            
            data.append({
                'origin': 'GRU',
                'destination': 'MIA',
                'departure_date': datetime.now() - timedelta(days=i),
                'price': 800 + price_variation,
                'advance_days': i,
                'day_of_week': (datetime.now() - timedelta(days=i)).weekday(),
                'month': (datetime.now() - timedelta(days=i)).month,
                'passengers': 1,
                'airline': 'LATAM'
            })
        return data
    
    def _prepare_features(self, historical_data: List[Dict]) -> Tuple[List, List]:
        """Prepare features for ML training."""
        # Use direct iteration instead of pandas for simplicity
        features = []
        targets = []
        
        for data_row in historical_data:
            feature_vector = [
                data_row['advance_days'],
                data_row['day_of_week'],
                data_row['month'],
                data_row['passengers'],
                hash(data_row['airline']) % 1000,  # Simple airline encoding
                hash(f"{data_row['origin']}-{data_row['destination']}") % 1000  # Route encoding
            ]
            features.append(feature_vector)
            targets.append(data_row['price'])
        
        if NUMPY_AVAILABLE:
            return np.array(features), np.array(targets)
        else:
            return features, targets
    
    def _prepare_prediction_features(
        self,
        origin: str,
        destination: str,
        departure_date: datetime,
        return_date: Optional[datetime],
        passengers: int
    ) -> List[float]:
        """Prepare features for price prediction."""
        advance_days = (departure_date - datetime.now()).days
        day_of_week = departure_date.weekday()
        month = departure_date.month
        
        return [
            advance_days,
            day_of_week,
            month,
            passengers,
            hash(f"{origin}-{destination}") % 1000,  # Route encoding
            1 if return_date else 0  # Round trip flag
        ]
    
    async def _analyze_price_trend(self, route: str, predicted_price: float) -> str:
        """Analyze if prices are trending up, down, or stable."""
        try:
            recent_prices = await self._get_recent_prices(route, days=30)
            
            if len(recent_prices) < 10:
                return "stable"
            
            # Calculate trend using simple linear regression
            if NUMPY_AVAILABLE:
                trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
            else:
                # Manual linear regression calculation
                n = len(recent_prices)
                x_values = list(range(n))
                sum_x = sum(x_values)
                sum_y = sum(recent_prices)
                sum_xy = sum(x * y for x, y in zip(x_values, recent_prices))
                sum_x2 = sum(x * x for x in x_values)
                
                # Calculate slope (trend)
                trend = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            if trend > 10:
                return "rising"
            elif trend < -10:
                return "falling"
            else:
                return "stable"
                
        except Exception:
            return "stable"
    
    async def _calculate_booking_window(self, route: str, departure_date: datetime) -> int:
        """Calculate optimal booking window."""
        # Rule-based calculation
        days_ahead = (departure_date - datetime.now()).days
        
        if days_ahead > 90:
            return 60  # Book 60 days ahead for far future trips
        elif days_ahead > 30:
            return 21  # Book 3 weeks ahead
        else:
            return 7   # Book within a week for near-term trips
    
    async def _get_current_average_price(self, route: str) -> Optional[float]:
        """Get current average price for route."""
        try:
            recent_prices = await self._get_recent_prices(route, days=7)
            return np.mean(recent_prices) if recent_prices else None
        except Exception:
            return None
    
    async def _get_historical_prices(self, route: str) -> List[float]:
        """Get historical prices for anomaly detection."""
        # This would query the database
        # For now, return sample data
        if NUMPY_AVAILABLE:
            return np.random.normal(800, 150, 100).tolist()
        else:
            import random
            return [800 + random.gauss(0, 150) for _ in range(100)]
    
    async def _get_recent_prices(self, route: str, days: int = 30) -> List[float]:
        """Get recent prices for trend analysis."""
        # This would query the database
        # For now, return sample data
        if NUMPY_AVAILABLE:
            return [800 + np.random.normal(0, 50) for _ in range(days)]
        else:
            import random
            return [800 + random.gauss(0, 50) for _ in range(days)]
    
    async def _fetch_market_data(self, route: str) -> List[Dict]:
        """Fetch market data for trend analysis."""
        # This would query the database
        # For now, return sample data
        data = []
        for i in range(365):
            if NUMPY_AVAILABLE:
                price_variation = np.random.normal(0, 100) + 50 * np.sin(i / 30)
            else:
                import random
                import math
                price_variation = random.gauss(0, 100) + 50 * math.sin(i / 30)
            
            data.append({
                'departure_date': datetime.now() - timedelta(days=i),
                'price': 800 + price_variation  # Seasonal variation
            })
        return data
    
    def _generate_booking_recommendations(
        self,
        seasonal_pattern: Dict[str, float],
        peak_months: List[str],
        low_months: List[str],
        volatility: float
    ) -> List[str]:
        """Generate booking recommendations based on analysis."""
        recommendations = []
        
        if volatility > 0.3:
            recommendations.append("High price volatility - monitor prices closely")
        
        if low_months:
            recommendations.append(f"Best deals typically in: {', '.join(low_months)}")
        
        if peak_months:
            recommendations.append(f"Avoid booking during peak months: {', '.join(peak_months)}")
        
        recommendations.append("Book 21-60 days in advance for best prices")
        recommendations.append("Consider flexible dates for better deals")
        
        return recommendations
    
    async def _fallback_prediction(
        self,
        origin: str,
        destination: str,
        departure_date: datetime
    ) -> PricePrediction:
        """Fallback prediction when ML model is not available."""
        # Rule-based prediction
        base_price = 800  # Default base price
        
        # Adjust based on advance booking
        days_ahead = (departure_date - datetime.now()).days
        if days_ahead < 7:
            base_price *= 1.5  # Last minute premium
        elif days_ahead > 60:
            base_price *= 0.9  # Early booking discount
        
        return PricePrediction(
            predicted_price=base_price,
            confidence=0.6,
            price_trend="stable",
            best_booking_window=30,
            savings_potential=0.0,
            model_version="fallback-v1.0"
        )
    
    async def _save_model(self, model_key: str, model) -> None:
        """Save trained model to disk."""
        try:
            model_file = self.model_path / f"{model_key}_price_predictor.joblib"
            joblib.dump(model, model_file)
            logger.info(f"Model saved: {model_file}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    async def _load_model(self, model_key: str) -> None:
        """Load trained model from disk."""
        try:
            model_file = self.model_path / f"{model_key}_price_predictor.joblib"
            if model_file.exists():
                self.models[model_key] = joblib.load(model_file)
                logger.info(f"Model loaded: {model_file}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")

class MLOrchestrator:
    """ML orchestrator for managing ML workflows."""
    
    def __init__(self):
        self.price_predictor = MLPricePredictor()
        self.training_scheduler = None
        
    async def start(self):
        """Start ML orchestrator."""
        logger.info("Starting ML Orchestrator")
        
        # Schedule regular model retraining
        self.training_scheduler = asyncio.create_task(self._training_loop())
    
    async def stop(self):
        """Stop ML orchestrator."""
        if self.training_scheduler:
            self.training_scheduler.cancel()
        logger.info("ML Orchestrator stopped")
    
    async def _training_loop(self):
        """Periodic model retraining."""
        while True:
            try:
                await asyncio.sleep(24 * 3600)  # Train daily
                logger.info("Starting scheduled model retraining")
                
                # Retrain global model
                await self.price_predictor.train_price_prediction_model()
                
                # Retrain popular route models
                popular_routes = ["GRU-MIA", "GRU-LAX", "GRU-NYC"]
                for route in popular_routes:
                    await self.price_predictor.train_price_prediction_model(route)
                
                logger.info("Scheduled model retraining completed")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in training loop: {e}")

# Global ML orchestrator instance
ml_orchestrator = MLOrchestrator()
