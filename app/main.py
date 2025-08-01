import os
import markdown
from fastapi import FastAPI, Request, HTTPException
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

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
    # Get API title from environment variable or use default
    api_title = os.getenv("API_TITLE", "PYMPL2 Python3 API")
    return templates.TemplateResponse("index.html", {"request": request, "api_title": api_title})

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

# Markdown documentation viewer endpoint
@app.get("/docs/{file_path:path}", response_class=HTMLResponse)
async def view_markdown(request: Request, file_path: str):
    # Get the documentation directory from environment variables
    docs_dir = os.getenv("DOCS_DIR", "./DOCUMENTATION")
    # Get API title from environment variable or use default
    api_title = os.getenv("API_TITLE", "PYMPL2 Python3 API")
    
    # Construct the full file path
    full_path = os.path.join(docs_dir, file_path)
    
    # Check if the file exists
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if the file is a Markdown file
    if not full_path.endswith('.md'):
        raise HTTPException(status_code=400, detail="Only Markdown files are supported")
    
    try:
        # Read the Markdown file
        with open(full_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
        
        # Create a simple HTML page with the converted Markdown
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{file_path}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="/static/css/styles.css">
            <style>
                .markdown-body {{
                    padding: 2rem;
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .markdown-body h1, .markdown-body h2, .markdown-body h3,
                .markdown-body h4, .markdown-body h5, .markdown-body h6 {{
                    color: #4a6fa5;
                    margin-top: 1.5rem;
                    margin-bottom: 1rem;
                }}
                .markdown-body code {{
                    background-color: #f0f4f8;
                    padding: 0.2rem 0.4rem;
                    border-radius: 4px;
                }}
                .markdown-body pre {{
                    background-color: #f0f4f8;
                    padding: 1rem;
                    border-radius: 4px;
                    overflow-x: auto;
                }}
                .markdown-body table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 1rem 0;
                }}
                .markdown-body th, .markdown-body td {{
                    border: 1px solid #dee2e6;
                    padding: 0.5rem;
                }}
                .markdown-body th {{
                    background-color: #f8f9fa;
                }}
                .back-button {{
                    margin: 1rem 0;
                    display: inline-block;
                    padding: 0.5rem 1rem;
                    background-color: #4a6fa5;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                }}
                .back-button:hover {{
                    background-color: #3a5a8a;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>API Documentation Assistant</h1>
                    <p>Viewing {api_title} documentation: {file_path}</p>
                </header>
                
                <a href="/" class="back-button">Back to Search</a>
                
                <div class="markdown-body">
                    {html_content}
                </div>
                
                <footer>
                    <p>Powered by OpenAI and FAISS</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        return html
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)