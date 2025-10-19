# server.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import jwt
import os
from contextlib import contextmanager
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import requests
import logging
from dotenv import load_dotenv
from fastapi import BackgroundTasks

load_dotenv()  # This loads .env into os.environ


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Joby Notification Server", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "joby"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "port": int(os.getenv("DB_PORT", "5432"))
}

EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "email_user": os.getenv("EMAIL_USER"),
    "email_password": os.getenv("EMAIL_PASSWORD")
}

JOBS_SERVER_URL = os.getenv("JOBS_SERVER_URL", "http://localhost:8002")

security = HTTPBearer()

# ==================== DATABASE CONNECTION ====================
@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def get_db_cursor(conn):
    """Get a cursor that returns results as dictionaries"""
    return conn.cursor(cursor_factory=RealDictCursor)

# ==================== DATABASE INITIALIZATION ====================
def initialize_database():
    """Create tables if they don't exist"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
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
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_frequency ON notifications(frequency)
        """)
        
        logger.info("Database initialized successfully")

# ==================== PYDANTIC MODELS ====================
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    firstName: Optional[str] = ""
    lastName: Optional[str] = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    firstName: Optional[str]
    lastName: Optional[str]

class TokenResponse(BaseModel):
    token: str
    user: UserResponse

class UpdateUserRequest(BaseModel):
    firstName: Optional[str]
    lastName: Optional[str]

class ChangePasswordRequest(BaseModel):
    currentPassword: str
    newPassword: str

class NotificationBase(BaseModel):
    id: str
    title: str
    seniority: Literal["intern", "junior", "senior", "chief"]
    country: str
    location: str
    dist: int = 0
    job_scope: Literal["parttime", "temporary", "fulltime", "full time", "part time"]
    frequency: Literal["daily", "twice_week", "weekly"]  # <- updated
    email_enabled: bool = True

class NotificationResponse(NotificationBase):
    last_sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UpdateNotificationRequest(BaseModel):
    title: str
    seniority: str
    country: str
    location: str
    dist: int
    job_scope: str
    frequency: str  # will validate in API
    email_enabled: bool

# ==================== AUTHENTICATION ====================
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: int, email: str) -> str:
    """Create a JWT token"""
    payload = {
        "userId": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to get the current authenticated user"""
    token = credentials.credentials
    return decode_token(token)

# ==================== AUTH ENDPOINTS ====================
@app.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest):
    """Register a new user"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (request.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password and create user
        password_hash = hash_password(request.password)
        cursor.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            RETURNING id, email, first_name, last_name
        """, (request.email, password_hash, request.firstName, request.lastName))
        
        user = cursor.fetchone()
        token = create_access_token(user['id'], user['email'])
        
        return TokenResponse(
            token=token,
            user=UserResponse(
                id=user['id'],
                email=user['email'],
                firstName=user['first_name'],
                lastName=user['last_name']
            )
        )

@app.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate a user and return a token"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            SELECT id, email, password_hash, first_name, last_name
            FROM users WHERE email = %s
        """, (request.email,))
        
        user = cursor.fetchone()
        if not user or not verify_password(request.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_access_token(user['id'], user['email'])
        
        return TokenResponse(
            token=token,
            user=UserResponse(
                id=user['id'],
                email=user['email'],
                firstName=user['first_name'],
                lastName=user['last_name']
            )
        )

# ==================== USER ENDPOINTS ====================
@app.get("/user/me", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            SELECT id, email, first_name, last_name, created_at
            FROM users WHERE id = %s
        """, (current_user['userId'],))
        
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user['id'],
            email=user['email'],
            firstName=user['first_name'],
            lastName=user['last_name']
        )

@app.put("/user/me", response_model=UserResponse)
async def update_user_profile(
    request: UpdateUserRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's profile"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            UPDATE users
            SET first_name = %s, last_name = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, email, first_name, last_name
        """, (request.firstName, request.lastName, current_user['userId']))
        
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user['id'],
            email=user['email'],
            firstName=user['first_name'],
            lastName=user['last_name']
        )

@app.post("/user/me/password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """Change user's password"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        
        # Verify current password
        cursor.execute("""
            SELECT password_hash FROM users WHERE id = %s
        """, (current_user['userId'],))
        
        user = cursor.fetchone()
        if not user or not verify_password(request.currentPassword, user['password_hash']):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Update password
        new_hash = hash_password(request.newPassword)
        cursor.execute("""
            UPDATE users
            SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (new_hash, current_user['userId']))
        
        return {"message": "Password updated successfully"}

# ==================== NOTIFICATION ENDPOINTS ====================
@app.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(current_user: dict = Depends(get_current_user)):
    """Get all notifications for the current user"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            SELECT id, title, seniority, country, location, dist, job_scope,
                   frequency, email_enabled, last_sent_at, created_at, updated_at
            FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (current_user['userId'],))
        
        notifications = cursor.fetchall()
        return [NotificationResponse(**notif) for notif in notifications]

@app.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationBase,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create a new notification and trigger async job email sending"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)

        # Insert notification into DB
        cursor.execute("""
            INSERT INTO notifications
            (id, user_id, title, seniority, country, location, dist, job_scope, frequency, email_enabled)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, title, seniority, country, location, dist, job_scope, frequency, email_enabled, created_at
        """, (
            notification.id,
            current_user['userId'],
            notification.title,
            notification.seniority,
            notification.country,
            notification.location,
            notification.dist,
            notification.job_scope,
            notification.frequency,
            notification.email_enabled
        ))

        created = cursor.fetchone()

        # Fetch user info
        cursor.execute("SELECT email, first_name FROM users WHERE id = %s", (current_user['userId'],))
        user = cursor.fetchone()
        user_name = user['first_name'] or user['email'].split('@')[0]

        # Schedule background email task (async)
        if notification.email_enabled:
            background_tasks.add_task(
                delayed_fetch_and_email,
                user_email=user['email'],
                user_name=user_name,
                notification=created
            )

        # Respond immediately to client
        return NotificationResponse(**created)


def delayed_fetch_and_email(user_email: str, user_name: str, notification: dict):
    """Wait up to 10 minutes for job server response, then send email"""
    import time

    max_wait_time = 600  # 10 minutes
    start_time = time.time()
    jobs = []

    while time.time() - start_time < max_wait_time:
        jobs = fetch_jobs_from_server(notification)
        if jobs:  # stop early if jobs found
            break
        time.sleep(30)  # retry every 30 seconds

    if jobs:
        send_job_email(user_email, user_name, notification, jobs)
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute("""
                UPDATE notifications
                SET last_sent_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (notification['id'],))
    else:
        logger.warning(f"No jobs found for {notification['title']} within timeout window")

@app.put("/notifications/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: str,
    request: UpdateNotificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update a notification"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            UPDATE notifications
            SET title = %s, seniority = %s, country = %s, location = %s,
                dist = %s, job_scope = %s, frequency = %s, email_enabled = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s
            RETURNING id, title, seniority, country, location, dist, job_scope,
                      frequency, email_enabled, last_sent_at, created_at, updated_at
        """, (
            request.title, request.seniority, request.country, request.location,
            request.dist, request.job_scope, request.frequency, request.email_enabled,
            notification_id, current_user['userId']
        ))
        
        updated = cursor.fetchone()
        if not updated:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return NotificationResponse(**updated)

@app.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a notification"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            DELETE FROM notifications
            WHERE id = %s AND user_id = %s
            RETURNING id
        """, (notification_id, current_user['userId']))
        
        deleted = cursor.fetchone()
        if not deleted:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"message": "Notification deleted successfully"}

@app.put("/notifications")
async def bulk_save_notifications(
    notifications: List[NotificationBase],
    current_user: dict = Depends(get_current_user)
):
    """Replace all notifications for the user"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        
        # Delete existing notifications
        cursor.execute("DELETE FROM notifications WHERE user_id = %s", (current_user['userId'],))
        
        # Insert new notifications
        for notif in notifications:
            cursor.execute("""
                INSERT INTO notifications
                (id, user_id, title, seniority, country, location, dist, job_scope, frequency, email_enabled)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                notif.id, current_user['userId'], notif.title, notif.seniority,
                notif.country, notif.location, notif.dist, notif.job_scope,
                notif.frequency, notif.email_enabled
            ))
        
        return {"message": "Notifications saved successfully"}

# ==================== JOB FETCHING & EMAIL ====================
def fetch_jobs_from_server(notification: dict) -> list:
    """Fetch jobs from the jobs server, matching jobs server schema"""

    # Map frontend/backend frequency to days_back
    days_back_map = {
        "daily": 1,
        "twice_week": 3,  # twice a week ≈ every 3 days
        "weekly": 7
    }

    job_scope_map = {
        "full time": "fulltime",
        "fulltime": "fulltime",
        "part time": "parttime",
        "parttime": "parttime",
        "temporary": "temporary"
    }

    payload = {
        "title": notification['title'],
        "seniority": notification['seniority'],
        "country": notification['country'],
        "location": notification['location'],
        "dist": int(notification['dist']),
        "job_scope": job_scope_map.get(notification['job_scope'].lower(), "fulltime"),
        "days_back": days_back_map.get(notification['frequency'], 1)
    }

    try:
        response = requests.post(f"{JOBS_SERVER_URL}/jobs_search", json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get('jobs', [])
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        return []


def send_job_email(user_email: str, user_name: str, notification: dict, jobs: list):
    """Send job alert email to user"""
    if not jobs or not EMAIL_CONFIG['email_user'] or not EMAIL_CONFIG['email_password']:
        logger.info(f"Skipping email to {user_email}: No jobs or email not configured")
        return
    
    # Build job list HTML
    job_list_html = ""
    for job in jobs:
        job_list_html += f"""
        <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
            <h3 style="margin: 0 0 10px 0; color: #333;">{job.get('title', 'N/A')}</h3>
            <p style="margin: 5px 0;"><strong>Company:</strong> {job.get('company', 'N/A')}</p>
            <p style="margin: 5px 0;"><strong>Location:</strong> {job.get('location', 'N/A')}</p>
            <p style="margin: 5px 0;"><strong>Job Type:</strong> {job.get('job_type', 'N/A')}</p>
            <p style="margin: 5px 0;">
                <a href="{job.get('job_url_direct') or job.get('job_url', '#')}" 
                   style="color: #ff6600; text-decoration: none; font-weight: bold;">
                    View Job →
                </a>
            </p>
        </div>
        """
    
    # Create email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Joby: {len(jobs)} New {notification['title']} Jobs"
    msg['From'] = EMAIL_CONFIG['email_user']
    msg['To'] = user_email
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #ff6600;">Hello {user_name}! 👋</h2>
        <p>We found <strong>{len(jobs)}</strong> new jobs matching your "{notification['title']}" alert:</p>
        {job_list_html}
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;" />
        <p style="color: #666; font-size: 14px;">
            This is your {notification['frequency']} job alert from <strong>Joby</strong>.
            <br />
            Manage your notifications at any time from your dashboard.
        </p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    
    try:
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['email_user'], EMAIL_CONFIG['email_password'])
            server.send_message(msg)
        
        logger.info(f"Email sent to {user_email} for notification: {notification['title']}")
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {e}")

def process_notifications(frequency: str):
    """Process notifications for a given frequency"""
    logger.info(f"Processing {frequency} notifications...")
    
    try:
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            
            cursor.execute("""
                SELECT n.*, u.email, u.first_name, u.last_name
                FROM notifications n
                JOIN users u ON n.user_id = u.id
                WHERE n.frequency = %s AND n.email_enabled = true
            """, (frequency,))
            
            notifications = cursor.fetchall()
            
            for notif in notifications:
                jobs = fetch_jobs_from_server(notif)
                
                if jobs:
                    user_name = notif['first_name'] or notif['email'].split('@')[0]
                    send_job_email(notif['email'], user_name, notif, jobs)
                    
                    # Update last_sent_at
                    cursor.execute("""
                        UPDATE notifications
                        SET last_sent_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (notif['id'],))
            
            conn.commit()
            logger.info(f"Completed processing {frequency} notifications")
    except Exception as e:
        logger.error(f"Error processing {frequency} notifications: {e}")

# ==================== SCHEDULER ====================
def setup_scheduler():
    """Set up scheduled jobs"""
    scheduler = BackgroundScheduler()
    
    # Daily notifications - every day at 8 AM
    scheduler.add_job(
        lambda: process_notifications('daily'),
        CronTrigger(hour=8, minute=0),
        id='daily_notifications'
    )

    # Twice a week notifications - e.g., Monday & Thursday at 8 AM
    scheduler.add_job(
        lambda: process_notifications('twice_week'),
        CronTrigger(day_of_week='mon,thu', hour=8, minute=0),
        id='twice_week_notifications'
    )
    
    # Weekly notifications - every Monday at 8 AM
    scheduler.add_job(
        lambda: process_notifications('weekly'),
        CronTrigger(day_of_week='mon', hour=8, minute=0),
        id='weekly_notifications'
    )
    

    scheduler.start()
    logger.info("Scheduler started successfully")
    
    return scheduler

# ==================== STARTUP & SHUTDOWN ====================
scheduler = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and start scheduler on startup"""
    global scheduler
    initialize_database()
    scheduler = setup_scheduler()
    logger.info("Joby Notification Server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown scheduler on app shutdown"""
    if scheduler:
        scheduler.shutdown()
    logger.info("Joby Notification Server shut down")

# ==================== HEALTH CHECK ====================
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "message": "Joby Notification Server is running",
        "timestamp": datetime.utcnow().isoformat(),
        "jobs_server": JOBS_SERVER_URL
    }

# Manual trigger endpoint (for testing)
@app.post("/test-email/{frequency}")
async def trigger_test_email(
    frequency: str,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger email notifications (for testing)"""
    if frequency not in ["daily", "weekly", "biweekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid frequency")
    
    process_notifications(frequency)
    return {"message": f"Triggered {frequency} notifications"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)