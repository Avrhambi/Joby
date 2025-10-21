from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from routes import auth as auth_routes
from routes import user as user_routes
from routes import notifications as notif_routes
from config.settings import BACKEND_SERVER_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Joby Notification Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(notif_routes.router)


@app.on_event("startup")
async def startup_event():
    # initialize DB schema via central config helper
    from config.db import init_db
    init_db()
    logger.info("Startup complete: DB ensured and routes mounted (via config.db.init_db)")


@app.get("/")
async def health_check():
    return {"message": "Joby Notification Server is running", "backend server": BACKEND_SERVER_URL}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8001)