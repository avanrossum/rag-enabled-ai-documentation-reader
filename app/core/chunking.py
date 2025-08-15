import re
import tiktoken
import os
from typing import List, Dict, Any, Optional

def get_file_type(file_path: str) -> str:
    """
    Determine the file type based on the file extension.
    
    Args:
        file_path: The path to the file
        
    Returns:
        The file type as a string (markdown, python, javascript, etc.)
    """
    _, ext = os.path.splitext(file_path.lower())
    
    # Define file type mappings
    file_types = {
        # Markdown
        '.md': 'markdown',
        '.markdown': 'markdown',
        
        # Programming languages
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.m': 'matlab',
        '.pl': 'perl',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.fish': 'bash',
        '.ps1': 'powershell',
        '.bat': 'batch',
        '.cmd': 'batch',
        
        # Web technologies
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        '.xml': 'xml',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
        
        # Documentation
        '.txt': 'text',
        '.rst': 'rst',
        '.adoc': 'asciidoc',
        '.tex': 'latex',
        
        # Configuration files
        '.env': 'env',
        '.gitignore': 'gitignore',
        '.dockerfile': 'dockerfile',
        '.dockerignore': 'dockerignore',
        '.gitattributes': 'gitattributes',
        
        # Data files
        '.csv': 'csv',
        '.tsv': 'csv',
        '.sql': 'sql',
        '.graphql': 'graphql',
        '.gql': 'graphql',
    }
    
    return file_types.get(ext, 'text')

def get_token_count(text: str, model: str = "gpt-4") -> int:
    """
    Count the number of tokens in a text string.
    
    Args:
        text: The text to count tokens for
        model: The model to use for tokenization
        
    Returns:
        The number of tokens in the text
    """
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    metadata: Optional[Dict[str, Any]] = None,
    file_type: str = "text"
) -> List[Dict[str, Any]]:
    """
    Split text into chunks of a specified token size.
    
    Args:
        text: The text to split
        chunk_size: The maximum number of tokens per chunk
        chunk_overlap: The number of tokens to overlap between chunks
        metadata: Additional metadata to include with each chunk
        file_type: The type of file being processed (markdown, python, etc.)
        
    Returns:
        A list of dictionaries containing the chunks and their metadata
    """
    if metadata is None:
        metadata = {}
    
    # For markdown files, use the specialized markdown chunking
    if file_type == "markdown":
        return chunk_markdown(text, chunk_size, chunk_overlap, metadata)
    
    # For code files, try to split by functions/classes
    if file_type in ["python", "javascript", "typescript", "java", "cpp", "c", "go", "rust"]:
        return chunk_code(text, chunk_size, chunk_overlap, metadata, file_type)
    
    # For other text files, use simple paragraph-based chunking
    return chunk_simple_text(text, chunk_size, chunk_overlap, metadata)

def chunk_simple_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Split plain text into chunks based on paragraphs and token limits.
    """
    if metadata is None:
        metadata = {}
    
    # Split text into paragraphs
    paragraphs = re.split(r'\n\s*\n', text.strip())
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # Check if adding this paragraph would exceed the chunk size
        combined = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
        if get_token_count(combined) > chunk_size and current_chunk:
            # Save the current chunk
            chunk_metadata = metadata.copy()
            chunks.append({
                "content": current_chunk,
                "metadata": chunk_metadata
            })
            
            # Start a new chunk with overlap
            words = current_chunk.split()
            overlap_text = " ".join(words[-chunk_overlap:]) if len(words) > chunk_overlap else current_chunk
            current_chunk = overlap_text + "\n\n" + paragraph
        else:
            current_chunk = combined
    
    # Add the final chunk if it's not empty
    if current_chunk:
        chunk_metadata = metadata.copy()
        chunks.append({
            "content": current_chunk,
            "metadata": chunk_metadata
        })
    
    return chunks

def chunk_code(
    code: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    metadata: Optional[Dict[str, Any]] = None,
    language: str = "python"
) -> List[Dict[str, Any]]:
    """
    Split code into chunks based on functions, classes, and other logical units.
    """
    if metadata is None:
        metadata = {}
    
    # Define patterns for different languages
    patterns = {
        "python": {
            "function": r'def\s+\w+\s*\([^)]*\)\s*:',
            "class": r'class\s+\w+',
            "import": r'^(import|from)\s+',
            "comment": r'^\s*#'
        },
        "javascript": {
            "function": r'(function\s+\w+|const\s+\w+\s*=\s*\([^)]*\)\s*=>|let\s+\w+\s*=\s*\([^)]*\)\s*=>)',
            "class": r'class\s+\w+',
            "import": r'^(import|export)\s+',
            "comment": r'^\s*//'
        },
        "typescript": {
            "function": r'(function\s+\w+|const\s+\w+\s*:\s*[^=]*=\s*\([^)]*\)\s*=>|let\s+\w+\s*:\s*[^=]*=\s*\([^)]*\)\s*=>)',
            "class": r'class\s+\w+',
            "import": r'^(import|export)\s+',
            "comment": r'^\s*//'
        },
        "java": {
            "function": r'(public|private|protected)?\s*(static\s+)?\w+\s+\w+\s*\([^)]*\)\s*{',
            "class": r'(public\s+)?class\s+\w+',
            "import": r'^import\s+',
            "comment": r'^\s*//'
        }
    }
    
    pattern = patterns.get(language, patterns["python"])
    
    # Split code into lines
    lines = code.split('\n')
    
    chunks = []
    current_chunk = ""
    current_context = ""
    
    for line in lines:
        # Check for function/class definitions
        if re.search(pattern["function"], line):
            current_context = f"Function: {line.strip()}"
        elif re.search(pattern["class"], line):
            current_context = f"Class: {line.strip()}"
        elif re.search(pattern["import"], line):
            current_context = f"Import: {line.strip()}"
        
        # Check if adding this line would exceed the chunk size
        combined = current_chunk + "\n" + line if current_chunk else line
        if get_token_count(combined) > chunk_size and current_chunk:
            # Save the current chunk
            chunk_metadata = metadata.copy()
            if current_context:
                chunk_metadata["code_context"] = current_context
            chunks.append({
                "content": current_chunk,
                "metadata": chunk_metadata
            })
            
            # Start a new chunk with overlap
            lines_list = current_chunk.split('\n')
            overlap_lines = lines_list[-chunk_overlap:] if len(lines_list) > chunk_overlap else lines_list
            overlap_text = '\n'.join(overlap_lines)
            current_chunk = overlap_text + "\n" + line
        else:
            current_chunk = combined
    
    # Add the final chunk if it's not empty
    if current_chunk:
        chunk_metadata = metadata.copy()
        if current_context:
            chunk_metadata["code_context"] = current_context
        chunks.append({
            "content": current_chunk,
            "metadata": chunk_metadata
        })
    
    return chunks

def chunk_markdown(
    markdown_text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Split markdown text into chunks of a specified token size.
    
    Args:
        markdown_text: The markdown text to split
        chunk_size: The maximum number of tokens per chunk
        chunk_overlap: The number of tokens to overlap between chunks
        metadata: Additional metadata to include with each chunk
        
    Returns:
        A list of dictionaries containing the chunks and their metadata
    """
    if metadata is None:
        metadata = {}
    
    # Split the text into sections based on headers
    sections = re.split(r'(#{1,6}\s+[^\n]+)', markdown_text)
    
    # Initialize chunks
    chunks = []
    current_chunk = ""
    current_headers = []
    
    for i, section in enumerate(sections):
        # Check if this is a header
        if i % 2 == 1:  # Headers are at odd indices
            header = section.strip()
            header_level = len(re.match(r'^(#+)', header).group(1))
            
            # Remove headers of higher level (deeper nesting)
            current_headers = [h for h in current_headers if h[0] < header_level]
            current_headers.append((header_level, header))
        else:
            # This is content
            content = section.strip()
            if not content:
                continue
                
            # Get the current header context
            header_context = " > ".join([h[1] for h in current_headers])
            
            # Check if adding this content would exceed the chunk size
            combined = current_chunk + "\n\n" + content if current_chunk else content
            if get_token_count(combined) > chunk_size and current_chunk:
                # Save the current chunk
                chunk_metadata = metadata.copy()
                chunk_metadata["header_context"] = header_context
                chunks.append({
                    "content": current_chunk,
                    "metadata": chunk_metadata
                })
                
                # Start a new chunk with overlap
                words = current_chunk.split()
                overlap_text = " ".join(words[-chunk_overlap:]) if len(words) > chunk_overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + content
            else:
                current_chunk = combined
    
    # Add the final chunk if it's not empty
    if current_chunk:
        header_context = " > ".join([h[1] for h in current_headers])
        chunk_metadata = metadata.copy()
        chunk_metadata["header_context"] = header_context
        chunks.append({
            "content": current_chunk,
            "metadata": chunk_metadata
        })
    
    return chunks