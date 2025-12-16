# Fleet Management - Data Infrastructure

## Overview

This directory contains the centralized data infrastructure for the Fleet Management System. All PostgreSQL databases and the unified pgAdmin management interface are orchestrated here.

## Architecture

```
Fleet Data Infrastructure
├── postgres-maintenance (port 5433)  → Maintenance Service Database
├── postgres-driver (port 6433)       → Driver Service Database
├── postgres-vehicle (port 7433)      → Vehicle Service Database
├── postgres-keycloak (port 8433)     → Identity Service Database
└── pgAdmin (port 5050)               → Unified Management Interface
```

All databases are connected via the `fleet-data-network` Docker network, allowing services to communicate internally while exposing specific ports to the host for local development.

## Quick Start

### Start All Databases

```bash
cd infrastructure/data
docker-compose up -d
```

### Start with pgAdmin

```bash
docker-compose --profile admin up -d
```

### Stop All Databases

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific database
docker-compose logs -f postgres-maintenance
```

### Check Health Status

```bash
docker-compose ps
```

## Database Connection Details

### Connection Rule of Thumb 💡

- **Internal Communication (Container-to-Container):** Services running inside Docker (pgAdmin, APIs) MUST use the **Container Name** and **Internal Port (5432)**. They share the `fleet-data-network`.
- **External Communication (Host-to-Container):** Tools running on your host machine (local API runs, CLI tools) MUST use `localhost` and the **External Port** (e.g., 5433).

### Maintenance Service Database

**Container Name:** `postgres-maintenance`

**Connection Strings:**
- **Local Development:** `postgresql://postgres:postgres@localhost:5433/maintenance_db`
- **From Docker Container:** `postgresql://postgres:postgres@postgres-maintenance:5432/maintenance_db`

**Credentials:**
- Username: `postgres`
- Password: `postgres`
- Database: `maintenance_db`

### Driver Service Database

**Container Name:** `postgres-driver`

**Connection Strings:**
- **Local Development:** `jdbc:postgresql://localhost:6433/driver_db`
- **From Docker Container:** `jdbc:postgresql://postgres-driver:5432/driver_db`

**Credentials:**
- Username: `postgres`
- Password: `postgres`
- Database: `driver_db`

### Vehicle Service Database

**Container Name:** `postgres-vehicle`

**Connection Strings:**
- **Local Development:** `Host=localhost;Port=7433;Database=vehicle_db;Username=postgres;Password=postgres`
- **From Docker Container:** `Host=postgres-vehicle;Port=5432;Database=vehicle_db;Username=postgres;Password=postgres`

**Credentials:**
- Username: `postgres`
- Password: `postgres`
- Database: `vehicle_db`

### Keycloak Identity Database

**Container Name:** `postgres-keycloak`

**Connection Strings:**
- **Local Development:** `jdbc:postgresql://localhost:8433/keycloak`
- **From Docker Container:** `jdbc:postgresql://postgres-keycloak:5432/keycloak`

**Credentials:**
- Username: `keycloak`
- Password: `keycloak_password`
- Database: `keycloak`

## pgAdmin Management Interface

### Access

- **URL:** http://localhost:5050
- **Email:** admin@admin.com
- **Password:** admin123

### Detailed Guide

For comprehensive instructions on connecting to each database service, running queries, and managing data, please refer to the dedicated guide:

👉 [**Centralized pgAdmin Guide**](./docs/PGADMIN_GUIDE.md)

### Quick Connection Summary

| Service | Host | Port | Database | User |
|---------|------|------|----------|------|
| **Maintenance** | `postgres-maintenance` | 5432 | `maintenance_db` | `postgres` |
| **Driver** | `postgres-driver` | 5432 | `driver_db` | `postgres` |
| **Vehicle** | `postgres-vehicle` | 5432 | `vehicle_db` | `postgres` |
| **Keycloak** | `postgres-keycloak` | 5432 | `keycloak` | `keycloak` |

## Data Persistence

All database data is persisted in Docker volumes:

- `maintenance_pg_data` - Maintenance service data
- `driver_pg_data` - Driver service data
- `vehicle_pg_data` - Vehicle service data
- `keycloak_pg_data` - Keycloak identity data
- `fleet_pgadmin_data` - pgAdmin configuration and settings

### Volume Management

**List all volumes:**
```bash
docker volume ls | grep -E "maintenance|driver|vehicle|keycloak|pgadmin"
```

**Inspect a volume:**
```bash
docker volume inspect maintenance_pg_data
```

**Remove a volume (⚠️ DATA LOSS WARNING):**
```bash
docker volume rm maintenance_pg_data
```

## Backup and Restore

### Backup a Database

```bash
# Maintenance database
docker exec postgres-maintenance pg_dump -U postgres maintenance_db > maintenance_backup.sql

# Driver database
docker exec postgres-driver pg_dump -U postgres driver_db > driver_backup.sql

# Vehicle database
docker exec postgres-vehicle pg_dump -U postgres vehicle_db > vehicle_backup.sql

# Keycloak database
docker exec postgres-keycloak pg_dump -U keycloak keycloak > keycloak_backup.sql
```

### Restore a Database

```bash
# Maintenance database
cat maintenance_backup.sql | docker exec -i postgres-maintenance psql -U postgres -d maintenance_db

# Driver database
cat driver_backup.sql | docker exec -i postgres-driver psql -U postgres -d driver_db

# Vehicle database
cat vehicle_backup.sql | docker exec -i postgres-vehicle psql -U postgres -d vehicle_db

# Keycloak database
cat keycloak_backup.sql | docker exec -i postgres-keycloak psql -U keycloak -d keycloak
```

## Troubleshooting

### Database Not Starting

1. **Check logs:**
   ```bash
   docker logs postgres-maintenance
   ```

2. **Verify port availability:**
   ```bash
   # Windows
   netstat -ano | findstr :5433
   
   # Linux/Mac
   lsof -i :5433
   ```

3. **Remove and recreate (⚠️ DATA LOSS):**
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

### Connection Refused from Service

1. **Verify network connectivity:**
   ```bash
   docker network inspect fleet-data-network
   ```

2. **Ensure service is on the same network:**
   - Check service docker-compose.yml has `fleet-data-network` as external network

3. **Test connection from another container:**
   ```bash
   docker run --rm --network fleet-data-network postgres:16 \
     psql -h postgres-maintenance -U postgres -d maintenance_db -c "SELECT 1"
   ```

### pgAdmin Cannot Connect

1. **Verify pgAdmin is running:**
   ```bash
   docker ps | grep fleet-pgadmin
   ```

2. **Check pgAdmin logs:**
   ```bash
   docker logs fleet-pgadmin
   ```

3. **Use container name (not localhost) for host:**
   - pgAdmin runs inside Docker, so use `postgres-maintenance`, not `localhost`

## Service Integration

### Connecting Services to Infrastructure

Services must join the `fleet-data-network` to communicate with databases:

```yaml
# In service docker-compose.yml
networks:
  fleet-data-network:
    external: true

services:
  your-service:
    networks:
      - fleet-data-network
    environment:
      DATABASE_URL: "postgresql://postgres:postgres@postgres-maintenance:5432/maintenance_db"
```

### Local Development (Non-Docker)

When running services locally (not in Docker), use `localhost` with the exposed port:

```bash
# Maintenance Service
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/maintenance_db

# Driver Service
DB_HOST=localhost
DB_PORT=6433

# Vehicle Service
ConnectionStrings__DefaultConnection="Host=localhost;Port=7433;Database=vehicle_db;Username=postgres;Password=postgres"
```

## Security Considerations

**⚠️ WARNING:** The default credentials in this setup are for **development only**. 

For production deployments:
1. Use strong, unique passwords
2. Store credentials in secrets management (e.g., Docker Secrets, Kubernetes Secrets)
3. Enable SSL/TLS for database connections
4. Restrict network access with firewall rules
5. Use read-only replicas for reporting queries
6. Enable PostgreSQL audit logging

## Performance Tuning

For production workloads, consider these PostgreSQL optimizations:

```yaml
# Add to environment section of postgres service
environment:
  POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
  POSTGRES_MAX_CONNECTIONS: "200"
  POSTGRES_SHARED_BUFFERS: "256MB"
  POSTGRES_EFFECTIVE_CACHE_SIZE: "1GB"
```

Or create a custom `postgresql.conf` and mount it:

```yaml
volumes:
  - ./custom-postgres.conf:/etc/postgresql/postgresql.conf
command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

## Monitoring

### Check Database Size

```bash
docker exec postgres-maintenance psql -U postgres -d maintenance_db -c "\l+"
```

### Active Connections

```bash
docker exec postgres-maintenance psql -U postgres -d maintenance_db -c \
  "SELECT count(*) FROM pg_stat_activity WHERE datname = 'maintenance_db';"
```

### Long-Running Queries

```bash
docker exec postgres-maintenance psql -U postgres -d maintenance_db -c \
  "SELECT pid, now() - query_start as duration, query FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC;"
```

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pgAdmin Documentation](https://www.pgadmin.org/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

