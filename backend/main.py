from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from services.db_service import init_db
from routes import auth_routes, blog_router

# Lifespan context manager to initialize DB
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Allowed origins for CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5174",  # Vite can use multiple ports
    "http://127.0.0.1:5174"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Use the defined origins list
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Serve static files from uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth_routes.router)
app.include_router(blog_router.router)
