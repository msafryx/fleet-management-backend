#!/bin/bash

# ===============================
# Driver Service - Complete Setup & Run Script (Linux/Mac)
# ===============================
# This script does EVERYTHING:
# 1. Checks Java (JDK 21) and Maven are installed
# 2. Checks if Docker is running
# 3. Checks if PostgreSQL is running, starts it if not
# 4. Builds the project with Maven
# 5. Runs the Spring Boot application AND seeds data
#
# Perfect for: Fresh clone, first-time setup, or daily use
# ===============================

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}🚀 Driver Service - Complete Setup & Run${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# ===============================
# Step 1: Check Java & Maven
# ===============================
echo -e "${BLUE}🔧 Step 1: Checking Java & Maven...${NC}"

# Check Java
if command -v java &> /dev/null; then
    javaVersion=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
    echo -e "${GREEN}✅ Java version: $javaVersion${NC}"
else
    echo -e "${RED}❌ Java is not installed!${NC}"
    echo -e "${YELLOW}   Please install JDK 21.${NC}"
    exit 1
fi

# Check Maven
if command -v mvn &> /dev/null; then
    mvnVersion=$(mvn -version | head -n 1 | awk '{print $3}')
    echo -e "${GREEN}✅ Maven version: $mvnVersion${NC}"
else
    echo -e "${RED}❌ Maven is not installed!${NC}"
    echo -e "${YELLOW}   Please install Maven.${NC}"
    exit 1
fi
echo ""

# ===============================
# Step 2: Check Docker is Running
# ===============================
echo -e "${BLUE}🐳 Step 2: Checking Docker...${NC}"
if ! docker ps >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first!${NC}"
    echo -e "${YELLOW}   After starting Docker, run this script again.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# ===============================
# Step 3: Check & Start PostgreSQL (Infrastructure)
# ===============================
echo -e "${BLUE}🗄️  Step 3: Checking PostgreSQL database...${NC}"
echo -e "${CYAN}   Note: Database is managed by centralized infrastructure${NC}"

# Check if postgres-driver container exists and is running
containerStatus=$(docker ps -a --filter "name=postgres-driver" --format "{{.Status}}" || echo "")
portMapping=$(docker port postgres-driver 5432/tcp 2>/dev/null || echo "")

if [[ $containerStatus == Up* ]] && [[ $portMapping == *"6433"* ]]; then
    echo -e "${GREEN}✅ PostgreSQL is already running on port 6433${NC}"
elif [ -n "$containerStatus" ]; then
    echo -e "${YELLOW}⚠️  PostgreSQL container exists but is not running (or wrong port). Starting infrastructure...${NC}"
    # Start the centralized infrastructure database
    docker-compose -f ../../infrastructure/data/docker-compose.yml up -d postgres-driver
    echo -e "${YELLOW}   Waiting for PostgreSQL to be ready...${NC}"
    sleep 15
    echo -e "${GREEN}✅ PostgreSQL started successfully${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL not found. Starting infrastructure database...${NC}"
    # Start the centralized infrastructure database
    docker-compose -f ../../infrastructure/data/docker-compose.yml up -d postgres-driver
    echo -e "${YELLOW}   Waiting for PostgreSQL to initialize (first-time setup)...${NC}"
    sleep 20
    echo -e "${GREEN}✅ PostgreSQL started successfully${NC}"
fi
echo ""

# ===============================
# Step 4: Verify Database Connection
# ===============================
echo -e "${BLUE}🔍 Step 4: Verifying database connection...${NC}"
maxRetries=5
retryCount=0
connected=false

while [ "$connected" = false ] && [ $retryCount -lt $maxRetries ]; do
    if docker exec postgres-driver pg_isready -U postgres -d driver_db >/dev/null 2>&1; then
        connected=true
        echo -e "${GREEN}✅ Database is ready${NC}"
    else
        retryCount=$((retryCount + 1))
        if [ $retryCount -lt $maxRetries ]; then
            echo -e "${YELLOW}   Waiting for database... (attempt $retryCount/$maxRetries)${NC}"
            sleep 3
        else
            echo -e "${RED}❌ Database is not responding. Please check Docker logs:${NC}"
            echo -e "${YELLOW}   docker logs postgres-driver${NC}"
            exit 1
        fi
    fi
done
echo ""

# ===============================
# Step 5: Build Application
# ===============================
echo -e "${BLUE}🔨 Step 5: Building application with Maven...${NC}"
if mvn clean package -DskipTests; then
    echo -e "${GREEN}✅ Build successful${NC}"
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi
echo ""

# ===============================
# Step 6: Run Application & Seed Data
# ===============================
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}✅ All Setup Complete! Starting Driver Service...${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "${CYAN}📝 Quick Reference:${NC}"
echo -e "${WHITE}   🌐 API:              http://localhost:6001${NC}"
echo -e "${WHITE}   📚 Swagger Docs:     http://localhost:6001/swagger-ui.html (if enabled)${NC}"
echo -e "${WHITE}   💚 Health Check:     http://localhost:6001/actuator/health (if enabled)${NC}"
echo ""
echo -e "${YELLOW}🛑 To stop the server: Press Ctrl+C${NC}"
echo ""
echo -e "${CYAN}============================================================${NC}"
echo ""

# Set environment variables for local run
# Note: DB_PORT 6433 connects to centralized infrastructure database
export SERVER_PORT=6001
export DB_PORT=6433
export DB_HOST=localhost

# Find the jar file
JAR_FILE=$(find target -name "*.jar" | grep -v "original" | head -n 1)

if [ ! -f "$JAR_FILE" ]; then
    echo -e "${RED}❌ Could not find JAR file in target/ directory.${NC}"
    exit 1
fi

# Start the application in the BACKGROUND
echo -e "${BLUE}🚀 Starting Java application in background...${NC}"
java -jar "$JAR_FILE" &
APP_PID=$!

# Wait for the application to be ready
echo -e "${BLUE}⏳ Waiting for application to start (listening on port 6001)...${NC}"
maxAppRetries=30 # 30 seconds max
appRetry=0
appReady=false

while [ "$appReady" = false ] && [ $appRetry -lt $maxAppRetries ]; do
    # Check if port 6001 is open (using netstat or bash tcp)
    # Using bash built-in /dev/tcp check which is common on Linux/Mac
    if (echo > /dev/tcp/localhost/6001) >/dev/null 2>&1; then
        appReady=true
    else
        sleep 1
        appRetry=$((appRetry + 1))
    fi
done

if [ "$appReady" = true ]; then
    echo -e "${GREEN}✅ Application is up! Seeding handled by Spring Boot CommandLineRunner.${NC}"
else
    echo -e "${RED}❌ Application failed to start within 30 seconds.${NC}"
    # Kill the background process if it's still hanging
    kill $APP_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Service is fully operational.${NC}"
echo -e "${YELLOW}   Press Ctrl+C to stop.${NC}"

# Wait for the background process to finish (blocking call)
# This keeps the script running until the user hits Ctrl+C
wait $APP_PID
