FROM python:3.9-slim

WORKDIR /app

# Install dependencies (ignoring local system caches)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the API port for HF Spaces (default is 7860)
EXPOSE 7860

# Start the FastAPI server by calling the main() function
CMD ["python", "server/app.py"]
