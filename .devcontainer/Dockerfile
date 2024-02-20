FROM python:3.11

# Remove any existing virtual environments
RUN rm -rf .venv

# Update pip and install pipenv
RUN pip install --upgrade pip && \
    pip install pipenv && \
    echo 'if [ -f "Pipfile" ]; then source $(pipenv --venv)/bin/activate; fi' >> ~/.bashrc

# Install system dependencies for SpatiaLite
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libsqlite3-mod-spatialite \
    spatialite-bin \
    libspatialite-dev \
    && rm -rf /var/lib/apt/lists/*