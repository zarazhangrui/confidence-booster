FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV REDIS_URL=redis://redis:6379

# Use Railway's PORT environment variable if available, otherwise default to 8080
ENV PORT=8080

# Expose port
EXPOSE ${PORT}

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "app:app"]
