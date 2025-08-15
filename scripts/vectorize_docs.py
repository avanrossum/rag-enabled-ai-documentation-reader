import os
import sys
import glob
from typing import List, Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.chunking import chunk_text, get_file_type
from app.core.embeddings import get_embeddings
from app.db.vector_store import FAISSVectorStore

def vectorize_documentation():
    """
    Vectorize all files in the documentation directory.
    """
    # Get the documentation directory from environment variables
    docs_dir = os.getenv("DOCS_DIR", "./DOCUMENTATION")
    
    print(f"Vectorizing documentation in {docs_dir}...")
    
    # Initialize vector store
    vector_store = FAISSVectorStore()
    
    # Define supported file extensions
    supported_extensions = [
        # Markdown
        "*.md", "*.markdown",
        # Programming languages
        "*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", "*.cpp", "*.cc", "*.cxx", 
        "*.c", "*.h", "*.hpp", "*.go", "*.rs", "*.php", "*.rb", "*.swift", "*.kt", 
        "*.scala", "*.r", "*.m", "*.pl", "*.sh", "*.bash", "*.zsh", "*.fish", 
        "*.ps1", "*.bat", "*.cmd",
        # Web technologies
        "*.html", "*.htm", "*.css", "*.scss", "*.sass", "*.less", "*.xml", 
        "*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg", "*.conf",
        # Documentation
        "*.txt", "*.rst", "*.adoc", "*.tex",
        # Configuration files
        "*.env", ".gitignore", ".dockerfile", ".dockerignore", ".gitattributes",
        # Data files
        "*.csv", "*.tsv", "*.sql", "*.graphql", "*.gql"
    ]
    
    # Find all supported files in the documentation directory
    all_files = []
    for pattern in supported_extensions:
        files = glob.glob(os.path.join(docs_dir, "**", pattern), recursive=True)
        all_files.extend(files)
    
    # Remove duplicates and sort
    all_files = sorted(list(set(all_files)))
    
    print(f"Found {len(all_files)} files to process.")
    
    # Process each file
    all_chunks = []
    
    for file_path in all_files:
        # Get relative path for metadata
        rel_path = os.path.relpath(file_path, docs_dir)
        
        # Determine file type
        file_type = get_file_type(file_path)
        
        print(f"Processing {rel_path} (type: {file_type})...")
        
        try:
            # Read the file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Create metadata
            metadata = {
                "source": rel_path,
                "file_path": file_path,
                "file_type": file_type
            }
            
            # Chunk the content using the appropriate method
            chunks = chunk_text(content, metadata=metadata, file_type=file_type)
            
            # Add chunks to the list
            all_chunks.extend(chunks)
            
            print(f"  Created {len(chunks)} chunks.")
        except Exception as e:
            print(f"  Error processing {rel_path}: {e}")
    
    if not all_chunks:
        print("No chunks created. Exiting.")
        return
    
    print(f"Created a total of {len(all_chunks)} chunks.")
    
    # Extract content for embedding
    texts = [chunk["content"] for chunk in all_chunks]
    
    # Generate embeddings in batches
    batch_size = 100
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        print(f"Generating embeddings for batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}...")
        
        batch_embeddings = get_embeddings(batch_texts)
        all_embeddings.extend(batch_embeddings)
    
    print(f"Generated {len(all_embeddings)} embeddings.")
    
    # Add documents and embeddings to vector store
    vector_store.add_documents(all_chunks, all_embeddings)
    
    # Save vector store
    vector_store.save()
    
    print("Vector store saved successfully.")

if __name__ == "__main__":
    # Run the function
    vectorize_documentation()