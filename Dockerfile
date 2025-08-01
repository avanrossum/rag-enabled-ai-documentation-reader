FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make startup script executable
RUN chmod +x scripts/startup.sh

# Create a non-root user to run the application
RUN useradd -m appuser
USER appuser

# Expose the port
EXPOSE 8000

# Run the startup script using shell
CMD ["/bin/bash", "scripts/startup.sh"]