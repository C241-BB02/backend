# Use the official Python image as the base image
FROM python:3.9-slim

# env variable as build arguments
ARG DATABASE_NAME
ARG DATABASE_USER
ARG DATABASE_PASSWORD
ARG DATABASE_HOST
ARG DATABASE_PORT
ARG SECRET_KEY
ARG ENVIRONMENT
ARG GOOGLE_APPLICATION_CREDENTIALS

# set env variables for docker
ENV DATABASE_NAME=$DATABASE_NAME
ENV DATABASE_USER=$DATABASE_USER
ENV DATABASE_PASSWORD=$DATABASE_PASSWORD
ENV DATABASE_HOST=$DATABASE_HOST
ENV DATABASE_PORT=$DATABASE_PORT
ENV SECRET_KEY=$SECRET_KEY
ENV ENVIRONMENT=$ENVIRONMENT
ENV GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS

# Set the working directory in the container
WORKDIR /docker-app

# Copy the requirements file into the container at /docker-app
COPY requirements.txt /docker-app/

# Install any dependencies specified in requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the current directory contents into the container at /docker-app
COPY . /docker-app/

# Expose port 8000
EXPOSE 8000

# Create the directory for static files
RUN mkdir -p /docker-app/staticfiles

# Collect static for better visualization
RUN python manage.py collectstatic --no-input

# Run DB migration
RUN python manage.py migrate --no-input

# Run Gunicorn
CMD ["gunicorn", "blur_bokeh_project.wsgi:application", "--bind", "0.0.0.0:8000"]