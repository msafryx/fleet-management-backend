# Local Development Guide - Maintenance Service

Quick reference for local development tasks, troubleshooting, and advanced configuration.

---

## 🚀 Quick Start

**Just run this ONE command:**

### All Platforms (Windows/Linux/Mac):
```bash
./setup-and-run.sh
```

For Git Bash on Windows or Linux/Mac, you might need to make it executable first:
```bash
chmod +x ./setup-and-run.sh
./setup-and-run.sh
```

The script automatically handles:
- ✅ Virtual environment setup
- ✅ Dependency installation
- ✅ Database startup
- ✅ Flask application

---

## 🛑 Stopping the Service

Press `Ctrl+C` in the terminal running the script.

**Optionally stop the database:**
```powershell
docker-compose down
```

---

## 🔍 Troubleshooting

### ❌ "Port 5001 is already in use"

**Cause:** Another process is using port 5001.

**Solution 1 - Find and kill the process:**
```powershell
# Windows
netstat -ano | findstr :5001
taskkill /PID <PID_NUMBER> /F

# Linux/Mac
lsof -i :5001
kill -9 <PID_NUMBER>
```

**Solution 2 - Use a different port:**
```powershell
# Set environment variable before running
$env:PORT = "5002"  # Windows
export PORT=5002    # Linux/Mac

# Then run the script
./setup-and-run.sh
```

---

### ❌ Script errors with "python not found"

**Cause:** Python not in PATH or wrong Python command.

**Solution:** Edit `../setup-and-run.sh` to check the Python command detection logic.

---

### ❌ "Cannot load PSModule" or "Execution Policy" error

**Cause:** PowerShell script execution is disabled (Windows security).

**Solution:** Use `setup-and-run.sh` in Git Bash instead, or run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### ❌ Script fails but doesn't show clear error

**Solution:** Run commands manually to see detailed errors:

```powershell
# 1. Check Docker
docker ps

# 2. Check if database is responding
docker logs postgres-maintenance

# 3. Try connecting to database
docker exec -it postgres-maintenance psql -U postgres -d maintenance_db

# 4. Activate venv and check Python packages
source venv/bin/activate  # Linux/Mac/Git Bash
# or .\venv\Scripts\activate # Windows Cmd
pip list
```

---

### ❌ Changes to Python code not reflecting

**Cause:** Flask auto-reload might have failed.

**Solution:**
1. Press `Ctrl+C` to stop Flask
2. Run `./setup-and-run.sh` again
3. Check terminal for syntax errors in your code

---

### ❌ Database connection fails after restart

**Cause:** Database container stopped or corrupted.

**Solution:**
```powershell
# Stop and remove containers
docker-compose down

# Remove database volume (WARNING: deletes all data!)
docker-compose down -v

# Start fresh
./setup-and-run.sh
```

---

## 🗄️ Database Access

### Option 1: Command Line (psql)

```powershell
# Connect to PostgreSQL
docker exec -it postgres-maintenance psql -U postgres -d maintenance_db
```

**Useful SQL commands:**
```sql
-- List all tables
\dt

-- View all maintenance items
SELECT * FROM maintenance_items;

-- Count items by status
SELECT status, COUNT(*) FROM maintenance_items GROUP BY status;

-- View recent items
SELECT id, vehicle_id, type, status, due_date 
FROM maintenance_items 
ORDER BY created_at DESC 
LIMIT 10;

-- Delete all data (WARNING!)
TRUNCATE TABLE maintenance_items CASCADE;

-- Exit
\q
```

### Option 2: pgAdmin (Web GUI)

```powershell
# Start pgAdmin container
docker-compose --profile admin up -d

# Access at: http://localhost:5051
# Email: admin@admin.com
# Password: admin123
```

**First-time setup in pgAdmin:**
1. Click "Add New Server"
2. General tab → Name: `Maintenance DB`
3. Connection tab:
   - Host: `postgres-maintenance`
   - Port: `5432`
   - Database: `maintenance_db`
   - Username: `postgres`
   - Password: `postgres`
4. Click "Save"

See `PGADMIN_GUIDE.md` for detailed instructions.

---

## ⚙️ Environment Variables

### View current configuration:
```powershell
# The script creates .env file automatically
cat .env  # Linux/Mac
type .env # Windows
```

### Customize settings:

Edit `.env` file in the maintenance service directory:

**After changing `.env`:**
- Restart the Flask application (Ctrl+C and run script again)

---

## 🔧 Manual Development (Without Script)

If you prefer manual control or the script isn't working:

### Terminal 1: Database
```powershell
cd \path\to\maintenanceService
docker-compose up postgres-maintenance
# Keep running
```

### Terminal 2: Flask App
```bash
cd /path/to/maintenanceService
source venv/bin/activate     # Linux/Mac/Git Bash
# or .\venv\Scripts\activate # Windows Cmd

python run.py
# Keep running
```

---

## 💡 Development Tips

### 1. Auto-Reload is Enabled
Flask runs in debug mode, so:
- Make changes to any `.py` file
- Save it
- Flask automatically reloads

You'll see:
```
 * Detected change in 'app/services/maintainance_service.py', reloading
 * Restarting with stat
```

### 2. Use Swagger UI for API Testing
Visit http://localhost:5001/docs
- Test all endpoints interactively
- See request/response schemas
- No need for Postman!

### 3. View Logs in Real-Time
```powershell
# Flask logs (Terminal 2)
# Shows requests, errors, and debug info

# Database logs (Terminal 1 if running manually)
docker logs -f postgres-maintenance
```

### 4. Quick Database Reset
```powershell
# Stop everything
docker-compose down -v

# Restart (recreates database with sample data)
./setup-and-run.sh
```

### 5. Test API Endpoints
```powershell
# Health check
curl http://localhost:5001/health

# Get all maintenance items
curl http://localhost:5001/api/maintenance/

# Get specific item
curl http://localhost:5001/api/maintenance/M001

# Create new item (use Swagger UI for easier testing!)
```

---

## 📊 Useful Commands

### Docker Commands
```powershell
# Check running containers
docker ps

# View database logs
docker logs postgres-maintenance

# Stop all containers
docker-compose down

# Stop and remove database data
docker-compose down -v

# Restart just the database
docker-compose restart postgres-maintenance
```

### Python Commands
```bash
# Activate virtual environment
source venv/bin/activate     # Linux/Mac/Git Bash
# or .\venv\Scripts\activate # Windows Cmd

# Install new package
pip install package-name
pip freeze > requirements.txt

# Check installed packages
pip list

# Run Python shell with app context
flask shell
```

### Flask Commands
```powershell
# (These are built into run.py, but available via Flask CLI)

# Create database tables
flask init-db

# Seed sample data
flask seed-db

# Start Flask shell
flask shell
```

---

## 🐛 Advanced Debugging

### Enable Verbose Logging
Edit `run.py` line 9:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Use Python Debugger (pdb)
Add breakpoints in your code:
```python
import pdb; pdb.set_trace()
```

When execution hits this line:
- `n` - next line
- `s` - step into function
- `c` - continue execution
- `p variable_name` - print variable
- `q` - quit debugger

### Check Database Connection
```python
# In flask shell
from app import db
db.engine.execute('SELECT 1').scalar()  # Should return 1
```

---

## 📝 Project Structure

```
maintenanceService/
├── docs/                      # Documentation
│   ├── README.md
│   ├── LOCAL_DEVELOPMENT_GUIDE.md
│   └── PGADMIN_GUIDE.md
├── setup-and-run.sh           # Main script (Windows/Linux/Mac)
├── docker-compose.yml         # Docker services
├── Dockerfile                 # Docker image
├── run.py                     # Flask entry point
├── config.py                  # Configuration
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (auto-created)
│
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models/               # Database models
│   │   └── maintainance.py
│   ├── routes/               # API endpoints
│   │   ├── maintainance_route.py
│   │   └── maintenance_api.py
│   ├── services/             # Business logic
│   │   └── maintainance_service.py
│   ├── schemas/              # Request/response validation
│   │   └── maintainance_schema.py
│   └── utils/                # Helper utilities
│       └── database_seeder.py
│
└── instance/                 # Instance-specific files
    └── (empty)
```

---

## 🚀 Quick Reference Card

| Task | Command |
|------|---------|
| **Start everything** | `./setup-and-run.sh` |
| **Stop Flask** | `Ctrl+C` |
| **Stop database** | `docker-compose down` |
| **View logs** | Check terminal output |
| **Database CLI** | `docker exec -it postgres-maintenance psql -U postgres -d maintenance_db` |
| **API docs** | http://localhost:5001/docs |
| **Health check** | http://localhost:5001/health |
| **Reset database** | `docker-compose down -v` then restart script |

---

## 🆘 Still Having Issues?

1. **Check if Docker Desktop is running**
2. **Make sure no other service is using port 5001 or 5433**
3. **Try running commands manually** (see Manual Development section)
4. **Check error messages carefully** - they usually indicate the problem
5. **Reset everything:**
   ```powershell
   docker-compose down -v
   rm -rf venv
   ./setup-and-run.sh
   ```

---

## 📚 Additional Resources

- **Main Documentation:** `README.md`
- **Database GUI Setup:** `PGADMIN_GUIDE.md`
- **Docker Compose Config:** `../docker-compose.yml`
- **Flask Config:** `config.py`

---

**Happy coding!** 🎉
