document.addEventListener('DOMContentLoaded', () => {
    const queryForm = document.getElementById('query-form');
    const queryInput = document.getElementById('query-input');
    const loading = document.getElementById('loading');
    const answerContainer = document.getElementById('answer-container');
    const answer = document.getElementById('answer');
    const sourcesContainer = document.getElementById('sources-container');
    const sources = document.getElementById('sources');

    // Handle form submission
    queryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const query = queryInput.value.trim();
        
        if (!query) {
            return;
        }
        
        // Show loading indicator
        loading.classList.remove('hidden');
        answerContainer.classList.add('hidden');
        sourcesContainer.classList.add('hidden');
        
        try {
            // Call the API
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query,
                    top_k: 5
                }),
            });
            
            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Display the answer
            answer.innerHTML = formatAnswer(data.answer);
            answerContainer.classList.remove('hidden');
            
            // Display the sources
            if (data.sources && data.sources.length > 0) {
                sources.innerHTML = formatSources(data.sources);
                sourcesContainer.classList.remove('hidden');
            } else {
                sourcesContainer.classList.add('hidden');
            }
        } catch (error) {
            console.error('Error:', error);
            answer.innerHTML = `<p class="error">Error: ${error.message}</p>`;
            answerContainer.classList.remove('hidden');
            sourcesContainer.classList.add('hidden');
        } finally {
            // Hide loading indicator
            loading.classList.add('hidden');
        }
    });
    
    // Format the answer with Markdown-like syntax
    function formatAnswer(text) {
        // Replace code blocks
        text = text.replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>');
        
        // Replace inline code
        text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Replace bold text
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Replace italic text
        text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        // Replace newlines with <br>
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }
    
    // Format the sources
    function formatSources(sources) {
        return sources.map((source, index) => {
            const metadata = source.metadata || {};
            const sourceFile = metadata.source || 'Unknown source';
            const headerContext = metadata.header_context || '';
            const codeContext = metadata.code_context || '';
            const fileType = metadata.file_type || '';
            
            // Create a link to the file
            const sourceLink = sourceFile ?
                `<a href="/docs/${encodeURIComponent(sourceFile)}" target="_blank" class="source-link">Source ${index + 1}: ${sourceFile}</a>` :
                `<span>Source ${index + 1}: Unknown source</span>`;
            
            // Build context information
            let contextInfo = '';
            if (headerContext) {
                contextInfo += `<div class="source-context">${headerContext}</div>`;
            }
            if (codeContext) {
                contextInfo += `<div class="source-context code-context">${codeContext}</div>`;
            }
            if (fileType && fileType !== 'text') {
                contextInfo += `<div class="source-context file-type">File type: ${fileType}</div>`;
            }
            
            return `
                <div class="source">
                    <div class="source-header">
                        <span>${sourceLink}</span>
                        <span>Relevance: ${Math.round((1 - source.score) * 100)}%</span>
                    </div>
                    ${contextInfo}
                    <div class="source-content">${source.content}</div>
                </div>
            `;
        }).join('');
    }
});