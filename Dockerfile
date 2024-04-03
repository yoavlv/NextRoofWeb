## Use an official Python runtime as the base image
#FROM python:3.11.2-buster
#
## Set the working directory in the container
##WORKDIR /opt/project
#WORKDIR /app
#COPY . /app/
## Prevents Python from writing .pyc bytecode files.
#ENV PYTHONDONTWRITEBYTECODE 1
## Ensures Python's stdout and stderr streams are unbuffered, which can be useful for logging.
#ENV PYTHONUNBUFFERED 1
## Adds /app to the Python module search path.
#ENV PYTHONPATH /app:$PYTHONPATH
## A custom environment variable possibly used by the application to detect if it's running inside Docker.
#ENV NextRoofWeb_SETTING_IN_DOCKER true
#
## Install dependencies
#RUN set -xe \
#    && apt-get update \
#    && apt-get install -y --no-install-recommends build-essential \
#    && pip install virtualenvwrapper poetry==1.6.1 \
#    && apt-get clean \
#    && rm -rf /var/lib/apt/lists/*
#
## Copy and install Python dependencies
#COPY ["poetry.lock", "pyproject.toml", "./"]
#RUN poetry install --no-root
#
## Copy project files
#COPY ["README.md", "Makefile", "./"]
#COPY core NextRoofWeb
#COPY local local
#
## Expose the Django development server port (adjust if needed)
#EXPOSE 8000
#
## Set up the entrypoint
#COPY scripts/entrypoint.sh /entrypoint.sh
#RUN chmod a+x /entrypoint.sh
#
#ENTRYPOINT ["/entrypoint.sh"]



# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y netcat && \
    apt-get clean

# Install Poetry
RUN pip install --upgrade pip && \
    pip install poetry

# Copy the project files to the container
COPY ./pyproject.toml ./poetry.lock* /app/

# Install project dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy the rest of your app's source code from your host to your image filesystem.
COPY . /app

# Make the entrypoint.sh script executable
RUN chmod +x /app/scripts/entrypoint.sh

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
