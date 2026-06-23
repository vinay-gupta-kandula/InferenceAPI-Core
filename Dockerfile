# ==========================================
# STAGE 1: Builder (Compiles dependencies)
# ==========================================
FROM python:3.10-slim AS builder

# Set the working directory for the build
WORKDIR /build

# Copy only the requirements file first to cache the pip install step
COPY requirements.txt .

# Install dependencies into a specific folder so they are easy to copy later
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ==========================================
# STAGE 2: Runtime (Lean production image)
# ==========================================
FROM python:3.10-slim

# Set working directory for the final app
WORKDIR /app

# Copy the compiled Python packages from the builder stage
COPY --from=builder /install /usr/local

# Copy your actual source code
COPY src/ ./src/

# Set environment variables so Python runs efficiently
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 8000

# The command to start the server when the container boots
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]