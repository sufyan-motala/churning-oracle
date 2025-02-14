# Stage 1: Builder stage
# Use Python 3.11 slim image as the base for building dependencies
FROM python:3.11-slim as builder

# Set the working directory in the builder stage
WORKDIR /app

# Copy requirements file and install dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
# Use Python 3.11 slim as the base for the final image
FROM python:3.11-slim

# Set the working directory in the final stage
WORKDIR /app

# Copy only the installed dependencies from builder stage
# This reduces the final image size by excluding build tools and cache
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application source code
COPY src/app/ ./app/
COPY src/frontend/ ./frontend/

# Set Python path to ensure modules can be found
ENV PYTHONPATH=/app

# Command to run the application
CMD ["python", "-m", "app.main"]
