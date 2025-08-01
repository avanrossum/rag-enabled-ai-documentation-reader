import re
import tiktoken
from typing import List, Dict, Any, Optional

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