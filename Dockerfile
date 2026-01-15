FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt gunicorn

# Copy application
COPY . /app

# Default port (can be overridden by environment variable)
ENV PORT=5000
EXPOSE 5000

# Use Gunicorn with the app factory
CMD gunicorn --bind 0.0.0.0:$PORT app:create_app()
