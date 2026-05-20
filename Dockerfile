# ==========================================
# Stage 1: Build the Angular Frontend
# ==========================================
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend source code
COPY frontend/package*.json ./
RUN npm install

# Copy the rest of the frontend code and build
COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Build the FastAPI Backend & Serve
# ==========================================
FROM python:3.11-slim

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy python dependencies and lockfile
COPY pyproject.toml /app/

# Install dependencies using uv sync (creates virtual environment)
RUN uv sync

# Copy application backend code
COPY . /app/

# Copy the compiled Angular frontend from Stage 1 into the location expected by main.py
COPY --from=frontend-builder /app/frontend/dist/frontend/browser /app/frontend/dist/frontend/browser

# Expose Cloud Run default port
EXPOSE 8080

# Define environment variables
ENV PYTHONUNBUFFERED=1

# Run uvicorn server serving both FastAPI and static files
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
