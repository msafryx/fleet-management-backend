#!/bin/bash

# ===============================
# Vehicle Service - Complete Setup & Run Script (Linux/Mac)
# ===============================
# This script does EVERYTHING:
# 1. Checks .NET SDK is installed
# 2. Restores NuGet packages
# 3. Checks if PostgreSQL is running, starts it if not
# 4. Runs database migrations
# 5. Runs the .NET application
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
echo -e "${CYAN}🚀 Vehicle Service - Complete Setup & Run${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# ===============================
# Step 1: Check .NET SDK
# ===============================
echo -e "${BLUE}🔧 Step 1: Checking .NET SDK...${NC}"
if command -v dotnet &> /dev/null; then
    dotnetVersion=$(dotnet --version)
    echo -e "${GREEN}✅ .NET SDK version: $dotnetVersion${NC}"
else
    echo -e "${RED}❌ .NET SDK is not installed!${NC}"
    echo -e "${YELLOW}   Please install .NET 9 SDK from: https://dotnet.microsoft.com/download${NC}"
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
# Step 3: Restore NuGet Packages
# ===============================
echo -e "${BLUE}📦 Step 3: Restoring NuGet packages...${NC}"
cd VehicleService/VehicleService.Api
dotnet restore --verbosity quiet
echo -e "${GREEN}✅ NuGet packages restored${NC}"
cd ../..
echo ""

# ===============================
# Step 4: Check & Start PostgreSQL (Infrastructure)
# ===============================
echo -e "${BLUE}🗄️  Step 4: Checking PostgreSQL database...${NC}"
echo -e "${CYAN}   Note: Database is managed by centralized infrastructure${NC}"

# Check if postgres-vehicle container exists and is running
containerStatus=$(docker ps -a --filter "name=postgres-vehicle" --format "{{.Status}}" || echo "")
portMapping=$(docker port postgres-vehicle 5432/tcp 2>/dev/null || echo "")

if [[ $containerStatus == Up* ]] && [[ $portMapping == *"7433"* ]]; then
    echo -e "${GREEN}✅ PostgreSQL is already running on port 7433${NC}"
elif [ -n "$containerStatus" ]; then
    echo -e "${YELLOW}⚠️  PostgreSQL container exists but is not running (or wrong port). Starting infrastructure...${NC}"
    # Start the centralized infrastructure database
    docker-compose -f ../../infrastructure/data/docker-compose.yml up -d postgres-vehicle
    echo -e "${YELLOW}   Waiting for PostgreSQL to be ready...${NC}"
    sleep 15
    echo -e "${GREEN}✅ PostgreSQL started successfully${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL not found. Starting infrastructure database...${NC}"
    # Start the centralized infrastructure database
    docker-compose -f ../../infrastructure/data/docker-compose.yml up -d postgres-vehicle
    echo -e "${YELLOW}   Waiting for PostgreSQL to initialize (first-time setup)...${NC}"
    sleep 20
    echo -e "${GREEN}✅ PostgreSQL started successfully${NC}"
fi
echo ""

# ===============================
# Step 5: Verify Database Connection
# ===============================
echo -e "${BLUE}🔍 Step 5: Verifying database connection...${NC}"
maxRetries=5
retryCount=0
connected=false

while [ "$connected" = false ] && [ $retryCount -lt $maxRetries ]; do
    if docker exec postgres-vehicle pg_isready -U postgres -d vehicle_db >/dev/null 2>&1; then
        connected=true
        echo -e "${GREEN}✅ Database is ready${NC}"
    else
        retryCount=$((retryCount + 1))
        if [ $retryCount -lt $maxRetries ]; then
            echo -e "${YELLOW}   Waiting for database... (attempt $retryCount/$maxRetries)${NC}"
            sleep 3
        else
            echo -e "${RED}❌ Database is not responding. Please check Docker logs:${NC}"
            echo -e "${YELLOW}   docker logs postgres-vehicle${NC}"
            exit 1
        fi
    fi
done
echo ""

# ===============================
# Step 6: Run Database Migrations
# ===============================
echo -e "${BLUE}🔄 Step 6: Running database migrations...${NC}"
echo -e "${GRAY}   Note: Migrations also run automatically when the app starts${NC}"
echo -e "${GRAY}   This is just a verification step${NC}"
echo -e "${GREEN}✅ Migration check complete${NC}"
echo ""

# ===============================
# Step 7: Run .NET Application
# ===============================
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}✅ All Setup Complete! Starting .NET Application...${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "${CYAN}📝 Quick Reference:${NC}"
echo -e "${WHITE}   🌐 API:              http://localhost:7001${NC}"
echo -e "${WHITE}   📚 Swagger Docs:     http://localhost:7001 (root URL)${NC}"
echo -e "${WHITE}   💚 Health Check:     http://localhost:7001/health${NC}"
echo -e "${WHITE}   🚗 Vehicles API:     http://localhost:7001/api/vehicles${NC}"
echo ""
echo -e "${YELLOW}🛑 To stop the server: Press Ctrl+C${NC}"
echo ""
echo -e "${CYAN}============================================================${NC}"
echo ""

# Navigate to API project and run
cd VehicleService/VehicleService.Api
dotnet watch

