import os
import markdown
from fastapi import FastAPI, Request, HTTPException
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.responses import Response

# Import API routes
from app.api.routes import router as api_router
from app.core.chunking import get_file_type

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

# Generic file viewer endpoint
@app.get("/docs/{file_path:path}", response_class=HTMLResponse)
async def view_file(request: Request, file_path: str):
    # Get the documentation directory from environment variables
    docs_dir = os.getenv("DOCS_DIR", "./DOCUMENTATION")
    # Get API title from environment variable or use default
    api_title = os.getenv("API_TITLE", "PYMPL2 Python3 API")
    
    # Construct the full file path
    full_path = os.path.join(docs_dir, file_path)
    
    # Check if the file exists
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine file type
    file_type = get_file_type(file_path)
    
    try:
        # Read the file
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Handle different file types
        if file_type == "markdown":
            return await render_markdown(content, file_path, api_title)
        elif file_type in ["python", "javascript", "typescript", "java", "cpp", "c", "go", "rust", "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "perl", "bash", "powershell", "batch", "html", "css", "scss", "sass", "less", "xml", "json", "yaml", "toml", "ini", "sql", "graphql"]:
            return await render_code(content, file_path, api_title, file_type)
        elif file_type in ["csv", "tsv"]:
            return await render_csv(content, file_path, api_title, file_type)
        else:
            return await render_text(content, file_path, api_title, file_type)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

async def render_markdown(content: str, file_path: str, api_title: str) -> HTMLResponse:
    """Render markdown content as HTML."""
    # Convert Markdown to HTML
    html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
    
    # Create HTML page
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
    
    return HTMLResponse(content=html)

async def render_code(content: str, file_path: str, api_title: str, file_type: str) -> HTMLResponse:
    """Render code content with syntax highlighting."""
    # Map file types to language identifiers for syntax highlighting
    language_map = {
        "python": "python",
        "javascript": "javascript",
        "typescript": "typescript",
        "java": "java",
        "cpp": "cpp",
        "c": "c",
        "go": "go",
        "rust": "rust",
        "php": "php",
        "ruby": "ruby",
        "swift": "swift",
        "kotlin": "kotlin",
        "scala": "scala",
        "r": "r",
        "matlab": "matlab",
        "perl": "perl",
        "bash": "bash",
        "powershell": "powershell",
        "batch": "batch",
        "html": "html",
        "css": "css",
        "scss": "scss",
        "sass": "sass",
        "less": "less",
        "xml": "xml",
        "json": "json",
        "yaml": "yaml",
        "toml": "toml",
        "ini": "ini",
        "sql": "sql",
        "graphql": "graphql"
    }
    
    language = language_map.get(file_type, "text")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{file_path}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/static/css/styles.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css">
        <style>
            .code-container {{
                padding: 2rem;
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .file-info {{
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 4px;
                margin-bottom: 1rem;
                border-left: 4px solid #4a6fa5;
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
            pre {{
                margin: 0;
                border-radius: 4px;
            }}
            code {{
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 14px;
                line-height: 1.5;
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
            
            <div class="code-container">
                <div class="file-info">
                    <strong>File:</strong> {file_path}<br>
                    <strong>Type:</strong> {file_type}<br>
                    <strong>Language:</strong> {language}
                </div>
                
                <pre><code class="language-{language}">{content}</code></pre>
            </div>
            
            <footer>
                <p>Powered by OpenAI and FAISS</p>
            </footer>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)

async def render_csv(content: str, file_path: str, api_title: str, file_type: str) -> HTMLResponse:
    """Render CSV/TSV content as a table."""
    import csv
    from io import StringIO
    
    # Parse CSV content
    delimiter = ',' if file_type == 'csv' else '\t'
    reader = csv.reader(StringIO(content), delimiter=delimiter)
    rows = list(reader)
    
    if not rows:
        return await render_text(content, file_path, api_title, file_type)
    
    # Create table HTML
    table_html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
    
    for i, row in enumerate(rows):
        table_html += "<tr>"
        for cell in row:
            if i == 0:  # Header row
                table_html += f"<th style='padding: 8px; background-color: #f8f9fa; border: 1px solid #dee2e6;'>{cell}</th>"
            else:
                table_html += f"<td style='padding: 8px; border: 1px solid #dee2e6;'>{cell}</td>"
        table_html += "</tr>"
    
    table_html += "</table>"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{file_path}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/static/css/styles.css">
        <style>
            .data-container {{
                padding: 2rem;
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                overflow-x: auto;
            }}
            .file-info {{
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 4px;
                margin-bottom: 1rem;
                border-left: 4px solid #4a6fa5;
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
            
            <div class="data-container">
                <div class="file-info">
                    <strong>File:</strong> {file_path}<br>
                    <strong>Type:</strong> {file_type}<br>
                    <strong>Rows:</strong> {len(rows)}
                </div>
                
                {table_html}
            </div>
            
            <footer>
                <p>Powered by OpenAI and FAISS</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)

async def render_text(content: str, file_path: str, api_title: str, file_type: str) -> HTMLResponse:
    """Render plain text content."""
    # Escape HTML characters
    escaped_content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{file_path}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/static/css/styles.css">
        <style>
            .text-container {{
                padding: 2rem;
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .file-info {{
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 4px;
                margin-bottom: 1rem;
                border-left: 4px solid #4a6fa5;
            }}
            .text-content {{
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 14px;
                line-height: 1.5;
                white-space: pre-wrap;
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 4px;
                overflow-x: auto;
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
            
            <div class="text-container">
                <div class="file-info">
                    <strong>File:</strong> {file_path}<br>
                    <strong>Type:</strong> {file_type}
                </div>
                
                <div class="text-content">{escaped_content}</div>
            </div>
            
            <footer>
                <p>Powered by OpenAI and FAISS</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)