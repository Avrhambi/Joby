# Joby Notification Server 

A high-performance FastAPI server that handles user authentication, job notification preferences, and scheduled email alerts for the Joby job search application.

## Features

- 🔐 JWT-based authentication (signup/login)
- 📊 PostgreSQL with raw SQL queries
- 🔔 CRUD operations for notification preferences
- 📧 Automated email notifications (daily, weekly, biweekly, monthly)
- 🔄 Integration with jobs server (port 8002)
- ⚡ High-performance async operations
- 📝 Auto-generated API documentation

## Prerequisites

- Python 3.8+ (3.10+ recommended)
- PostgreSQL 12+
- Jobs server running on port 8002

## Installation

### 1. Create a virtual environment

```bash
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up PostgreSQL

```bash
# Create database
psql -U postgres
CREATE DATABASE joby;
\q
```

The server will automatically create tables on first run.

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your credentials
nano .env
```

**Required variables:**
```env
DB_PASSWORD=your_password
JWT_SECRET=your-super-secret-key
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### 5. Gmail Setup

1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use that password as `EMAIL_PASSWORD` (not your regular password!)

## Running the Server

### Development Mode

```bash
uvicorn server:app --reload --port 8001
```

### Production Mode

```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
```

### Using Python directly

```bash
python server.py
```

The server will start on `http://localhost:8001`

## API Documentation

FastAPI automatically generates interactive API docs:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Register new user |
| POST | `/login` | Login and get JWT token |

### User Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/user/me` | Get user profile | ✅ |
| PUT | `/user/me` | Update user profile | ✅ |
| POST | `/user/me/password` | Change password | ✅ |

### Notifications

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/notifications` | List all notifications | ✅ |
| POST | `/notifications` | Create notification | ✅ |
| PUT | `/notifications/{id}` | Update notification | ✅ |
| DELETE | `/notifications/{id}` | Delete notification | ✅ |
| PUT | `/notifications` | Bulk replace all | ✅ |

### Testing/Admin

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Health check | ❌ |
| POST | `/test-email/{frequency}` | Trigger test emails | ✅ |

## Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE notifications (
    id VARCHAR(50) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    seniority VARCHAR(50) NOT NULL,
    country VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    dist INTEGER DEFAULT 0,
    job_scope VARCHAR(50) NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    email_enabled BOOLEAN DEFAULT true,
    last_sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Scheduled Jobs

Powered by **APScheduler** (more reliable than node-cron):

| Schedule | Trigger | Frequency |
|----------|---------|-----------|
| Daily | 8:00 AM daily | `daily` |
| Weekly | 8:00 AM Monday | `weekly` |
| Biweekly | 8:00 AM every 2nd Monday | `biweekly` |
| Monthly | 8:00 AM 1st of month | `monthly` |

### How it works:

1. Scheduler runs at specified time
2. Fetches all enabled notifications for that frequency
3. For each notification:
   - Calls jobs server with user preferences
   - Gets matching jobs (filtered by days_back)
   - Sends HTML email with job listings
   - Updates `last_sent_at` timestamp

### Email content includes:

- User's first name
- Number of jobs found
- Job title, company, location, type
- Direct application URL (`job_url_direct`)
- Frequency reminder

## Testing

### 1. Test health check

```bash
curl http://localhost:8001/
```

### 2. Create a user

```bash
curl -X POST http://localhost:8001/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "firstName": "John",
    "lastName": "Doe"
  }'
```

**Save the token from the response!**

### 3. Create a notification

```bash
curl -X POST http://localhost:8001/notifications \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "id": "notif123",
    "title": "Software Engineer",
    "seniority": "junior",
    "country": "Israel",
    "location": "Tel Aviv",
    "dist": 25,
    "job_scope": "fulltime",
    "frequency": "daily",
    "email_enabled": true
  }'
```

### 4. Test email manually

```bash
curl -X POST http://localhost:8001/test-email/daily \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. View API docs

Open browser: http://localhost:8001/docs

Try out endpoints interactively!


## Troubleshooting

### Database Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql
# or
pg_isready

# Test connection
psql -U postgres -d joby -c "SELECT 1;"

# View tables
psql -U postgres -d joby -c "\dt"
```

### Email Not Sending

1. **Check Gmail App Password**:
   - Must be 16-character app password
   - Not your regular Gmail password
   - 2FA must be enabled

2. **Check logs**:
   ```bash
   # Server logs will show email errors
   # Look for "Failed to send email"
   ```

3. **Test SMTP connection**:
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'app-password')
   server.quit()  # If no error, config is correct
   ```

### Jobs Server Connection

```bash
# Test jobs server
curl http://localhost:8002/

# Check if it's running
lsof -i :8002
```

### Port Already in Use

```bash
# Find process using port 8001
lsof -ti:8001

# Kill it
lsof -ti:8001 | xargs kill -9

# Or change port in command
uvicorn server:app --port 8003
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check Python version (need 3.8+)
python --version
```


## Monitoring

### View logs

```bash
# If running with systemd
sudo journalctl -u joby -f

# If running directly
# Logs appear in terminal
```

### Check database connections

```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'joby';
```

### Monitor scheduler

The scheduler logs to stdout:
- Job execution times
- Success/failure status
- Error messages


## License

MIT

## Support

For issues or questions:
- Check the troubleshooting section
- Review API docs at `/docs`
- Check server logs
- Ensure jobs server is running


