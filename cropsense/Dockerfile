# Stage 1: Build the React Frontend
FROM node:20-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the FastAPI Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend ./backend

# Copy the frontend build from Stage 1 into the backend directory
# (FastAPI main.py is configured to serve from ../frontend/dist)
COPY --from=frontend-build /frontend/dist ./frontend/dist

# Expose port
EXPOSE 8000

# Environment variables
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV PORT=8000

# Run the application
WORKDIR /app/backend
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
