# Use a stable, lightweight official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies (none are strictly needed for PyMuPDF wheel, but nice to have)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies first to cache this layer
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY pdf_booklet /app/pdf_booklet
COPY make_booklet.py /app/
COPY run_web_ui.py /app/

# Expose server port
EXPOSE 8000

# Run the Web UI server by default
CMD ["python3", "make_booklet.py", "--web"]
