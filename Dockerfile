FROM python:3.9-slim

WORKDIR /app

# Install dependencies (ignoring local system caches)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the API port for HF Spaces (default is 7860)
EXPOSE 7860

# Set PYTHONPATH to the root directory so modules are findable
ENV PYTHONPATH=/app

# Start the FastAPI server as a module
CMD ["python", "-m", "server.app"]
