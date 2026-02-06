# Complete Setup Guide

This guide walks you through setting up the Toy Inventory System with Supplier Management from scratch.

## 📋 Prerequisites

- **Python 3.8+** installed
- **Docker** and **Docker Compose** installed
- **Git** (optional, for cloning)

## 🚀 Step-by-Step Setup

### Step 1: Install Python Dependencies

```bash
# Create and activate virtual environment (recommended)
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Dependencies installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - Database ORM
- `psycopg2-binary` - PostgreSQL adapter
- `pydantic[email]` - Data validation with email support
- `pytest` - Testing framework
- `httpx` - HTTP client for tests

### Step 2: Start PostgreSQL Database

```bash
# Start database in background
docker-compose up -d

# Verify it's running
docker ps
```

You should see `fiverr_postgres` and `fiverr_adminer` containers running.

**Database Details:**
- Host: `localhost`
- Port: `5432`
- Database: `fiverr_db`
- Username: `admin`
- Password: `admin123`

**Adminer (Database UI):**
- URL: http://localhost:8080
- Login with the credentials above

### Step 3: Run Database Migrations

Run these scripts in order:

```bash
# 1. Create toys table
python scripts/create_toys_table.py

# 2. Create suppliers table, foreign keys, triggers, and views
python scripts/create_suppliers_table.py
```

**Expected output:**
```
Toys table created successfully!
Suppliers table created successfully!
```

### Step 4: (Optional) Seed Sample Data

```bash
python scripts/seed_suppliers.py
```

This creates sample suppliers for common toy categories:
- Action Figures Supplier
- Dolls Supplier
- Building Blocks Supplier
- Plush Toys Supplier
- Board Games Supplier
- Educational Toys Supplier

### Step 5: Start the API Server

```bash
uvicorn main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 6: Verify Setup

Open your browser or use curl:

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
{"status":"up"}

# List suppliers (if you seeded data)
curl http://localhost:8000/suppliers
```

## ✅ You're Ready!

Your system is now fully set up. Check out:
- **[QUICK_START.md](./QUICK_START.md)** for common operations
- **[API_REFERENCE.md](./API_REFERENCE.md)** for complete API documentation

---

## 🔧 Troubleshooting

### Database Connection Failed

**Problem:** Health check returns `{"status":"down"}`

**Solutions:**
1. Verify Docker containers are running:
   ```bash
   docker ps
   ```

2. Check database logs:
   ```bash
   docker logs fiverr_postgres
   ```

3. Restart containers:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Port Already in Use

**Problem:** `Error: Port 5432 is already in use`

**Solutions:**
1. Stop existing PostgreSQL:
   ```bash
   # Windows
   net stop postgresql
   
   # Linux/Mac
   sudo systemctl stop postgresql
   ```

2. Or change the port in `docker-compose.yml`:
   ```yaml
   ports:
     - "5433:5432"  # Changed from 5432:5432
   ```
   Then update `app/database.py` to use port 5433.

### Migration Script Errors

**Problem:** `Table already exists` error

**Solution:** This is normal if you've run migrations before. The scripts use `CREATE TABLE IF NOT EXISTS`, so they're safe to re-run.

**Problem:** `Permission denied` or `Access denied`

**Solution:** Ensure the database is running and credentials are correct in `app/database.py`.

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:** Activate your virtual environment and install dependencies:
```bash
.\.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

### Pytest Not Found

**Problem:** `pytest: command not found`

**Solution:** Use Python module syntax:
```bash
python -m pytest tests/ -v
```

---

## 🗑️ Clean Uninstall

To completely remove the system:

```bash
# 1. Stop and remove containers with volumes
docker-compose down -v

# 2. Remove virtual environment
# Windows
Remove-Item -Recurse -Force .venv

# Linux/Mac
rm -rf .venv

# 3. (Optional) Remove __pycache__ directories
# Windows
Get-ChildItem -Recurse -Directory __pycache__ | Remove-Item -Recurse -Force

# Linux/Mac
find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## 🔄 Resetting the Database

To start fresh with a clean database:

```bash
# Option 1: Use cleanup script
python scripts/clean_test_data.py

# Option 2: Recreate database completely
docker-compose down -v
docker-compose up -d
python scripts/create_toys_table.py
python scripts/create_suppliers_table.py
python scripts/seed_suppliers.py  # Optional
```

---

## 🌐 Accessing the Database

### Via Adminer (Web UI)

1. Open http://localhost:8080
2. Login:
   - System: `PostgreSQL`
   - Server: `postgres`
   - Username: `admin`
   - Password: `admin123`
   - Database: `fiverr_db`

### Via psql (Command Line)

```bash
docker exec -it fiverr_postgres psql -U admin -d fiverr_db
```

Common commands:
```sql
\dt              -- List tables
\d toys          -- Describe toys table
\d suppliers     -- Describe suppliers table
SELECT * FROM toys LIMIT 5;
SELECT * FROM suppliers;
\q               -- Quit
```

---

## 📦 Production Deployment Notes

For production deployment, you should:

1. **Change Database Credentials:**
   - Update `docker-compose.yml`
   - Update `app/database.py`
   - Use environment variables instead of hardcoded values

2. **Use a Production ASGI Server:**
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Enable HTTPS/SSL**

4. **Set up Database Backups**

5. **Configure Logging**

6. **Add Authentication/Authorization**

See [ARCHITECTURE.md](./ARCHITECTURE.md) for more production considerations.
