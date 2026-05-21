FROM python:3.10-alpine

# Set environment variables - Fixed format
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

# Install ALL dependencies at once from requirements.txt
COPY ./requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p staticfiles media static/img

# Create missing image placeholder (replace with actual images)
RUN touch static/img/carousel-1.jpg

# Temporarily disable manifest storage if it causes issues
RUN sed -i 's/STATICFILES_STORAGE/# STATICFILES_STORAGE/g' dict/settings.py || true

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8080

# Run the application - Fixed JSON format
CMD ["sh", "-c", "gunicorn dict.wsgi:application --bind 0.0.0.0:${PORT} --workers 3"]