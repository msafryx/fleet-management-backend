# Centralized pgAdmin Guide

## Overview

This guide explains how to access, configure, and use the centralized pgAdmin instance to manage all Fleet Management PostgreSQL databases.

pgAdmin is a web-based management tool for PostgreSQL. In this infrastructure, a single pgAdmin instance serves as the management interface for all backend service databases.

## 🚀 Quick Start

1.  **Start Infrastructure:**
    ```bash
    cd infrastructure/data
    docker-compose --profile admin up -d
    ```

2.  **Access Web Interface:**
    -   **URL:** http://localhost:5050
    -   **Email:** `admin@admin.com`
    -   **Password:** `admin123`

## 🔌 Connecting to Databases

After logging in, you need to register the database servers you want to manage.

### Port Reference Table

| Service | Container Name (Internal Use) | Internal Port | Host Name (Local Use) | External Port |
|---------|-------------------------------|---------------|-----------------------|---------------|
| **Maintenance** | `postgres-maintenance` | `5432` | `localhost` | `5433` |
| **Driver** | `postgres-driver` | `5432` | `localhost` | `6433` |
| **Vehicle** | `postgres-vehicle` | `5432` | `localhost` | `7433` |
| **Keycloak** | `postgres-keycloak` | `5432` | `localhost` | `8433` |

### Connection Rule of Thumb 💡

- **If pgAdmin is running in Docker (default):**
  - Host name: **Container Name** (e.g., `postgres-maintenance`)
  - Port: **Internal Port** (`5432`)

- **If pgAdmin is running LOCALLY (on your host machine):**
  - Host name: `localhost`
  - Port: **External Port** (e.g., `5433`)

### 1. Maintenance Service Database

-   **Name:** `Maintenance DB`
-   **Host name:** `postgres-maintenance`
-   **Port:** `5432`
-   **Maintenance database:** `maintenance_db`
-   **Username:** `postgres`
-   **Password:** `postgres`

### 2. Driver Service Database

-   **Name:** `Driver DB`
-   **Host name:** `postgres-driver`
-   **Port:** `5432`
-   **Maintenance database:** `driver_db`
-   **Username:** `postgres`
-   **Password:** `postgres`

### 3. Vehicle Service Database

-   **Name:** `Vehicle DB`
-   **Host name:** `postgres-vehicle`
-   **Port:** `5432`
-   **Maintenance database:** `vehicle_db`
-   **Username:** `postgres`
-   **Password:** `postgres`

### 4. Keycloak Identity Database

-   **Name:** `Keycloak DB`
-   **Host name:** `postgres-keycloak`
-   **Port:** `5432`
-   **Maintenance database:** `keycloak`
-   **Username:** `keycloak`
-   **Password:** `keycloak_password`

> **⚠️ Important:** When connecting from pgAdmin running in Docker, always use the **Container Name** (e.g., `postgres-maintenance`) as the Host name, NOT `localhost`. Use the internal port `5432`.

## 📊 Common Operations

### Viewing Data
1.  Expand the server tree: **Servers → [DB Name] → Databases → [db_name] → Schemas → public → Tables**
2.  Right-click on a table name.
3.  Select **View/Edit Data → All Rows**.

### Running SQL Queries
1.  Right-click on the database name.
2.  Select **Query Tool**.
3.  Enter your SQL query and press the **Execute (▶)** button (or F5).

### Backup & Restore
-   **Backup:** Right-click Database → Backup.
-   **Restore:** Right-click Database → Restore.

## 🛠️ Troubleshooting

### "Unable to connect to server"
-   **Check Hostname:** Ensure you are using the container name (e.g., `postgres-driver`), NOT `localhost`.
-   **Check Port:** Ensure you are using the internal port `5432`.
-   **Check Network:** Verify that pgAdmin and the databases are on the same Docker network (`fleet-data-network`).

### "Connection refused"
-   Verify that the target database container is running: `docker ps`.
-   Check database logs: `docker logs postgres-maintenance`.

### pgAdmin not loading at localhost:5050
-   Wait 10-15 seconds for the container to initialize.
-   Check if port 5050 is already in use on your host machine.

## 🛑 Stopping pgAdmin

To stop pgAdmin without stopping the databases:
```bash
docker stop fleet-pgadmin
```

To stop the entire data infrastructure:
```bash
cd infrastructure/data
docker-compose down
```

