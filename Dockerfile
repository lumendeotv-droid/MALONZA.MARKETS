FROM python:3.10-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG=0
ENV PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    jpeg-dev \
    zlib-dev \
    cargo \
    postgresql-dev

# Copy requirements and install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Create necessary directories and placeholder images
RUN mkdir -p staticfiles media static/img
RUN if [ ! -f static/img/carousel-1.jpg ]; then touch static/img/carousel-1.jpg; fi

# Run Django migrations and collect static files
RUN python manage.py migrate --noinput
RUN python manage.py collectstatic --noinput || \
    (echo "Collectstatic failed with manifest storage, retrying without compression..." && \
     python manage.py collectstatic --noinput --ignore=*.css)

# Expose port
EXPOSE 8080

# Run migrations on startup (safety net) then start gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn dict.wsgi:application --bind 0.0.0.0:${PORT} --workers 3"]