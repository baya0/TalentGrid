import logging

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routes import (
    auth_router,
    candidates_router,
    search_router,
    import_router,
    gmail_router,
    analytics_router,
    admin_router,
)


# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="TalentGrid API",
    description="Smart Talent Sourcing Platform with RAG-powered search",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(candidates_router)
app.include_router(search_router)
app.include_router(import_router)
app.include_router(gmail_router)
app.include_router(analytics_router)
app.include_router(admin_router)


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "TalentGrid API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Initialize AI system on startup
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("TalentGrid API starting...")

    # AI components are lazy-loaded on first use
    # This avoids startup failures if optional dependencies are missing

    print("TalentGrid API ready!")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
