FROM python:3.10-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0
ENV PORT 8080

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

# Install dependencies
COPY ./requirements.txt .

# Upgrade pip and install packages
RUN pip install --upgrade pip setuptools wheel
RUN pip install gunicorn
RUN pip install Pillow
RUN pip install python-dotenv
RUN pip install django-storages[boto3]
RUN pip install intasend-python
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p staticfiles media

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8080

# Run the application
CMD gunicorn dict.wsgi:application --bind 0.0.0.0:${PORT} --workers 3