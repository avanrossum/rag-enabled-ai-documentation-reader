import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Import API routes
from app.api.routes import router as api_router

# Create FastAPI app
app = FastAPI(
    title="API Documentation Assistant",
    description="A RAG-powered API documentation assistant",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

# Include API routes
app.include_router(api_router, prefix="/api")

# Root endpoint - serve the frontend
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Metadata endpoint
@app.get("/metadata")
async def metadata():
    return {
        "name": "API Documentation Assistant",
        "version": "0.1.0",
        "embedding_model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        "completion_model": os.getenv("COMPLETION_MODEL", "gpt-4o"),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)