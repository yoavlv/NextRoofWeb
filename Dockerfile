# Use an official Python runtime as the base image
FROM python:3.11.2-buster

# Set the working directory in the container
#WORKDIR /opt/project
WORKDIR /app
COPY . /app/
# Prevents Python from writing .pyc bytecode files.
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures Python's stdout and stderr streams are unbuffered, which can be useful for logging.
ENV PYTHONUNBUFFERED 1
# Adds /app to the Python module search path.
ENV PYTHONPATH /app:$PYTHONPATH
# A custom environment variable possibly used by the application to detect if it's running inside Docker.
ENV NextRoofWeb_SETTING_IN_DOCKER true

# Install dependencies
RUN set -xe \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install virtualenvwrapper poetry==1.6.1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY ["poetry.lock", "pyproject.toml", "./"]
RUN poetry install --no-root

# Copy project files
COPY ["README.md", "Makefile", "./"]
COPY core NextRoofWeb
COPY local local

# Expose the Django development server port (adjust if needed)
EXPOSE 8000

# Set up the entrypoint
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
