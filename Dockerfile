# Base Python Image
FROM python:3.11-slim

# Install Go and Git because TestRunner executes:
# go vet
# go test
RUN apt-get update && \
    apt-get install -y golang-go git && \
    rm -rf /var/lib/apt/lists/*

# Working directory inside container
WORKDIR /app

# Clone validator repository so target Go codebase is ready
RUN git clone --depth 1 https://github.com/go-playground/validator.git /app/validator

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI (supporting dynamic $PORT for Render and local 8000 default)
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]