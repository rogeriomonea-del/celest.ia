# Celest.ia v2 - Architecture Documentation

## System Overview

Celest.ia v2 is a comprehensive AI-powered flight search and analysis platform with the following key components:

- **FastAPI Backend**: RESTful API with async support
- **React Frontend**: Modern web dashboard
- **PostgreSQL Database**: Persistent data storage
- **LLM Integration**: Multi-provider AI analysis
- **Telegram Bot**: Conversational interface
- **Docker Environment**: Containerized deployment

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Telegram Bot   │    │   External APIs │
│   (Port 5173)   │    │   (Webhook)     │    │ (Airlines/LLMs) │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │ HTTP Requests        │ Webhook              │ API Calls
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│                     (Port 8000)                                │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐        │
│  │  API Routes   │ │ Orchestrator  │ │  AI Services  │        │
│  └───────────────┘ └───────────────┘ └───────────────┘        │
└─────────┬───────────────────┬───────────────────┬─────────────┘
          │                   │                   │
          │ Database ORM      │ Background Tasks  │ LLM Requests
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   PostgreSQL    │ │      Redis      │ │   LLM Provider  │
│   (Port 5432)   │ │   (Port 6379)   │ │ (OpenAI/Claude) │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Directory Structure

```
Celest.ia-v2-Alpha/
├── src/                          # Backend source code
│   ├── core/                     # Core application logic
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database setup and session
│   │   └── orchestrator.py      # Main orchestration logic
│   ├── scrapers/                # Web scraping modules
│   │   ├── __init__.py
│   │   ├── base_scraper.py      # Base scraper class
│   │   ├── copa_scraper.py      # Copa Airlines scraper
│   │   ├── skyscanner_scraper.py # Skyscanner scraper
│   │   └── connectmiles_scraper.py # Connect Miles scraper
│   ├── ai/                      # AI and LLM integration
│   │   ├── __init__.py
│   │   ├── llm_client.py        # LLM provider abstraction
│   │   └── price_analyzer.py    # Price analysis logic
│   ├── api/                     # FastAPI routes and endpoints
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── routes/              # API route modules
│   │   └── middleware.py        # Custom middleware
│   ├── bot/                     # Telegram bot functionality
│   │   ├── __init__.py
│   │   ├── handlers.py          # Bot command handlers
│   │   └── commands.py          # Bot command definitions
│   ├── database/                # Database models and repositories
│   │   ├── __init__.py
│   │   ├── models.py            # SQLAlchemy models
│   │   └── repositories.py      # Data access layer
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── validators.py        # Input validation
│       └── formatters.py        # Data formatting
├── frontend/                    # React web application
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── services/            # API client services
│   │   └── styles/              # CSS stylesheets
│   ├── public/                  # Static assets
│   ├── package.json
│   └── vite.config.js
├── tests/                       # Test suites
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
├── docs/                        # Documentation
│   ├── api/                     # API documentation
│   ├── deployment/              # Deployment guides
│   └── architecture/            # Architecture docs
├── scripts/                     # Utility scripts
│   ├── setup.sh                 # Environment setup
│   ├── backup.sh                # Database backup
│   └── deploy.sh                # Deployment script
├── docker-compose.yml           # Docker services
├── Dockerfile                   # Container definition
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # Project overview
```

## Core Components

### 1. FastAPI Backend (`src/api/`)

**Purpose**: RESTful API server providing flight search, analysis, and bot webhook endpoints.

**Key Features**:
- Async request handling
- CORS middleware for frontend integration
- JWT authentication (planned)
- Automatic API documentation with Swagger
- Error handling and logging
- Rate limiting and request validation

**Main Endpoints**:
- `POST /api/v1/flights/search` - Flight search
- `GET /api/v1/flights/trends` - Price trends
- `POST /api/v1/analysis/prices` - AI price analysis
- `POST /api/v1/bot/webhook` - Telegram webhook
- `GET /api/v1/health` - Health check

### 2. Orchestrator (`src/core/orchestrator.py`)

**Purpose**: Central coordination of flight search across multiple sources with AI analysis.

**Key Responsibilities**:
- Manage concurrent scraper execution
- Aggregate and normalize flight data
- Trigger AI analysis of results
- Handle caching and rate limiting
- Coordinate with database storage

**Workflow**:
1. Receive search request with parameters
2. Initialize configured scrapers in parallel
3. Execute searches with timeout handling
4. Normalize and validate results
5. Trigger AI analysis for insights
6. Store results in database
7. Return aggregated response

### 3. Scrapers (`src/scrapers/`)

**Purpose**: Web scraping modules for different flight search sources.

**Base Scraper Pattern**:
```python
class BaseScraper:
    async def __aenter__(self):
        # Setup browser/session
    
    async def __aexit__(self):
        # Cleanup resources
    
    async def search_flights(self, params):
        # Scraping logic
        
    def normalize_results(self, raw_data):
        # Data normalization
```

**Implemented Scrapers**:
- **Copa Airlines**: Direct airline website scraping
- **Skyscanner**: Meta-search engine integration
- **Connect Miles**: Loyalty program analysis

### 4. AI Integration (`src/ai/`)

**Purpose**: Multi-provider LLM integration for flight data analysis and insights.

**LLM Client Features**:
- Provider abstraction (OpenAI, Anthropic)
- Fallback chain for reliability
- Response caching
- Token usage tracking
- Error handling and retries

**Price Analyzer**:
- Trend analysis and predictions
- Deal identification
- Comparative analysis across airlines
- Seasonal pattern recognition
- Recommendation generation

### 5. Database Layer (`src/database/`)

**Purpose**: Data persistence with PostgreSQL using SQLAlchemy ORM.

**Key Models**:
```python
# Core flight data
class Flight(Base):
    id: UUID
    origin: str
    destination: str
    departure_date: datetime
    return_date: Optional[datetime]
    price: Decimal
    airline: str
    search_metadata: dict

# Search history and caching
class SearchRequest(Base):
    id: UUID
    user_id: Optional[UUID]
    parameters: dict
    results_count: int
    created_at: datetime

# AI analysis results
class PriceAnalysis(Base):
    id: UUID
    flight_id: UUID
    analysis_text: str
    confidence_score: float
    created_at: datetime
```

**Repository Pattern**:
- Clean separation of data access logic
- Async database operations
- Transaction management
- Query optimization and caching

### 6. Telegram Bot (`src/bot/`)

**Purpose**: Conversational interface for flight search and notifications.

**Bot Commands**:
- `/search` - Interactive flight search
- `/trends` - Price trend analysis
- `/alerts` - Price alert management
- `/help` - Command documentation

**Natural Language Processing**:
- Intent recognition for search queries
- Entity extraction (airports, dates, passengers)
- Context-aware conversation flow
- Multi-turn dialog management

## Data Flow

### Flight Search Process

1. **Request Initiation**
   - User submits search via frontend or bot
   - Request validation and parameter normalization
   - Rate limiting and authentication checks

2. **Orchestrated Search**
   - Orchestrator initializes configured scrapers
   - Parallel execution with timeout handling
   - Real-time progress tracking

3. **Data Processing**
   - Results normalization and validation
   - Duplicate detection and removal
   - Price comparison and ranking

4. **AI Analysis**
   - LLM analysis of search results
   - Trend analysis and predictions
   - Deal identification and recommendations

5. **Response Delivery**
   - Database storage of results
   - Formatted response to client
   - Background notifications if configured

### Data Storage Strategy

- **Hot Data**: Recent searches and popular routes cached in Redis
- **Warm Data**: Flight results and analysis stored in PostgreSQL
- **Cold Data**: Historical data archived with compression
- **Metadata**: Search patterns and user preferences for personalization

## Security Considerations

### API Security
- CORS configuration for frontend integration
- Rate limiting to prevent abuse
- Input validation and sanitization
- SQL injection prevention with ORM
- Secure environment variable management

### Data Privacy
- No storage of sensitive payment information
- User data anonymization options
- GDPR compliance considerations
- Secure session management
- Audit logging for data access

### External Service Security
- API key rotation and secure storage
- Request/response validation
- Timeout and circuit breaker patterns
- Secure webhook verification for Telegram

## Performance Optimization

### Backend Optimizations
- Async/await for I/O operations
- Connection pooling for database and HTTP clients
- Caching with Redis for frequent queries
- Background task processing with Celery
- Efficient database indexing strategy

### Frontend Optimizations
- Code splitting and lazy loading
- Image optimization and compression
- CSS and JavaScript minification
- Browser caching strategies
- Progressive Web App features

### Scraping Optimizations
- Request rate limiting and backoff
- Browser session reuse
- Headless browser optimization
- Parallel scraping with resource limits
- Smart retry logic with exponential backoff

## Monitoring and Observability

### Logging Strategy
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Request/response logging for API endpoints
- Error tracking with stack traces
- Performance metrics logging

### Metrics Collection
- API response times and throughput
- Scraper success rates and performance
- Database query performance
- LLM usage and costs
- User interaction patterns

### Health Checks
- Service availability endpoints
- Database connectivity checks
- External service dependency checks
- Resource utilization monitoring
- Automated alerting for failures

## Deployment Architecture

### Container Strategy
- Multi-stage Docker builds for optimization
- Separate containers for API, workers, and frontend
- Environment-specific configurations
- Health checks and graceful shutdowns
- Resource limits and scaling policies

### Infrastructure Components
- **Load Balancer**: NGINX for traffic distribution
- **Application Servers**: Gunicorn with multiple workers
- **Database**: PostgreSQL with read replicas
- **Cache**: Redis cluster for high availability
- **Queue**: Redis for background tasks
- **Monitoring**: Prometheus and Grafana

### Scaling Considerations
- Horizontal scaling for API services
- Database read replicas for query optimization
- Redis clustering for cache scaling
- Background worker auto-scaling
- CDN integration for static assets

## Future Enhancements

### Technical Improvements
- GraphQL API for flexible data fetching
- Real-time WebSocket connections
- Advanced caching strategies
- Machine learning price predictions
- Microservices architecture migration

### Feature Additions
- Multi-language support
- Mobile application development
- Advanced filtering and sorting
- Price alert notifications
- User account management
- Loyalty program integration

### Operational Enhancements
- Automated testing pipelines
- Blue-green deployment strategy
- Disaster recovery procedures
- Performance optimization automation
- Security scanning and compliance
