# Maintenance Service (Flask API)

Fleet Management Maintenance Service - Manages vehicle maintenance records, schedules, and tracking.

## Quick Start

### 🚀 **Easiest Way** (One Command Does Everything!)

**All Platforms (Windows Git Bash / Linux / Mac):**
```bash
chmod +x ./setup-and-run.sh
./setup-and-run.sh
```

This automatically:
- Sets up virtual environment
- Installs dependencies
- Starts PostgreSQL (if not running)
- Runs the Flask application

**Perfect for:** Fresh clone, first-time setup, or daily development!

---

### Alternative: Docker Compose

```bash
# Start the service with Docker
docker-compose up -d

# Verify it's running
curl http://localhost:5001/health
```

**Service URL:** http://localhost:5001  
**Swagger UI (API Docs):** http://localhost:5001/docs  
**Database:** PostgreSQL on port 5433

---

## Features

- ✅ RESTful API for maintenance management
- ✅ **Interactive Swagger/OpenAPI documentation**
- ✅ Automatic database initialization & seeding
- ✅ PostgreSQL database with sample data
- ✅ Docker containerization
- ✅ Health check endpoints
- ✅ CORS support
- ✅ Request validation with Marshmallow schemas

---

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)

---

## Running the Service

### With Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
# Activate virtual environment
source ./venv/Scripts/Activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations (Run this after starting the PostgreSQL container)
flask db upgrade

# Run the service
python run.py
```

---

## API Endpoints

### Interactive API Documentation
🚀 **Swagger UI:** http://localhost:5001/docs

Explore and test all API endpoints interactively with the built-in Swagger UI!

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Service info & documentation links |
| GET | `/docs` | **Swagger UI (Interactive API docs)** |
| GET | `/swagger.json` | OpenAPI JSON specification |
| GET | `/api/maintenance/` | List all maintenance items (with pagination & filters) |
| GET | `/api/maintenance/:id` | Get specific item |
| POST | `/api/maintenance/` | Create new item |
| PUT | `/api/maintenance/:id` | Update item (full) |
| PATCH | `/api/maintenance/:id` | Update item (partial) |
| DELETE | `/api/maintenance/:id` | Delete item |
| GET | `/api/maintenance/summary` | Get summary stats |
| GET | `/api/maintenance/vehicle/:vehicle_id/history` | Vehicle maintenance history |
| POST | `/api/maintenance/status/update-bulk` | Bulk status update job |

### Query Parameters (GET /api/maintenance/)
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 10)
- `vehicle` - Filter by vehicle ID
- `status` - Filter by status (multiple allowed)
- `priority` - Filter by priority (multiple allowed)
- `assignedTo` - Filter by assignment

---

## Database

### Communication Details
*   **Database Engine:** PostgreSQL 16
*   **Communication Method:** **SQLAlchemy (ORM)**
    *   Uses Python's SQLAlchemy ORM to map Python classes to database tables.
    *   **Library:** `Flask-SQLAlchemy` wrapper around `SQLAlchemy` and `psycopg2-binary` adapter.
*   **Migration Tool:** **Flask-Migrate (Alembic)**
    *   Handles database schema updates and migrations.

### Connection Info
- **Host (External):** localhost:5433
- **Host (Internal):** postgres-maintenance
- **Database:** maintenance_db
- **User:** postgres
- **Password:** postgres

### Access Database

#### Command Line (psql)
```bash
docker exec -it postgres-maintenance psql -U postgres -d maintenance_db
```

#### Web Interface (pgAdmin)
For a graphical database management interface, see **[PGADMIN_GUIDE.md](./PGADMIN_GUIDE.md)** for detailed setup instructions.

Quick start:
```bash
docker-compose --profile admin up -d
```
Then open: **http://localhost:5051** (login: `admin@admin.com` / `admin123`)

### Sample Data
The database is automatically seeded with 5 maintenance items on first startup:
- M001: Oil Change (Overdue)
- M002: Brake Inspection (In Progress)
- M003: Tire Rotation (Scheduled)
- M004: Annual Inspection (Due Soon)
- M005: Engine Tune-up (Completed)

---

## Configuration

### Environment Variables (`.env`)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/maintenance_db
FLASK_ENV=development
PORT=5001
HOST=0.0.0.0
CORS_ORIGINS=*
```

---

## Docker Services

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| maintenance-service | maintenance-service | 5001 | Flask API |
| postgres-maintenance | postgres-maintenance | 5433 | PostgreSQL 16 |
| pgadmin-maintenance | pgadmin-maintenance | 5051 | DB Admin (optional) |

### Start with pgAdmin
```bash
docker-compose --profile admin up -d
```
Access at: http://localhost:5051
- Email: `admin@admin.com`
- Password: `admin123`

📚 **See [PGADMIN_GUIDE.md](./PGADMIN_GUIDE.md) for complete setup instructions**

---

## Project Structure

```
maintenanceService/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # Database models
│   ├── routes/              # API routes
│   ├── services/            # Business logic
│   ├── schemas/             # Validation schemas
│   └── utils/               # Database seeder & utilities
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image
├── docs/
│   ├── README.md                # This file
│   ├── LOCAL_DEVELOPMENT_GUIDE.md
│   └── PGADMIN_GUIDE.md
├── setup-and-run.sh             # Setup script
├── docker-compose.yml           # Docker services
├── Dockerfile                   # Docker image
├── migrations/                  # Alembic migrations
└── .env                     # Environment variables
```

---

## Development

### Rebuild After Code Changes
```bash
docker-compose up --build
```

### Run Tests
```bash
pytest
pytest --cov=app  # With coverage
```

### Database Migrations
```bash
# Initialize migrations (first time)
flask db init

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

---

## Troubleshooting

### Port Already in Use
Edit `../docker-compose.yml` to use different ports.

### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker ps

# View logs
docker-compose logs postgres-maintenance

# Wait for health check (~10 seconds)
```

### Reset Database
```bash
# Delete volumes and restart
docker-compose down -v
docker-compose up -d
```

---

## Integration

This service works alongside the Vehicle Service:
- **Vehicle Service:** Port 7001, PostgreSQL 7433
- **Maintenance Service:** Port 5001, PostgreSQL 5433

Both services can run simultaneously without conflicts.

---

## Documentation

- **API Documentation (Swagger):** Available at **http://localhost:5001/docs** when running
- **OpenAPI Spec:** http://localhost:5001/swagger.json
- **pgAdmin Setup & Connection Guide:** [PGADMIN_GUIDE.md](./PGADMIN_GUIDE.md)
- **Database Setup:** See `../../DATABASE_SETUP.md`

### Using Swagger UI

1. Start the service: `docker-compose up -d`
2. Open browser: http://localhost:5001/docs
3. You can:
   - View all endpoints and their parameters
   - Test endpoints directly from the browser
   - See request/response schemas
   - View example payloads
   - No authentication required (development mode)

---

## Production Deployment

### Security Checklist
- [ ] Change default PostgreSQL password
- [ ] Configure CORS_ORIGINS to specific domains
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure logging and monitoring

### Environment Variables
```env
FLASK_ENV=production
DATABASE_URL=postgresql://<user>:<pass>@<host>:<port>/maintenance_db
CORS_ORIGINS=https://yourdomain.com
```

---

## License

MIT License
