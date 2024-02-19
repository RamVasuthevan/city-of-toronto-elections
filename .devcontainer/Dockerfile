FROM python:3.11

# Removes any existing virtual environments
RUN rm -rf .venv

# Update pip and install pipenv
RUN pip install --upgrade pip && \
    pip install pipenv && \
    echo 'if [ -f "Pipfile" ]; then source $(pipenv --venv)/bin/activate; fi' >> ~/.bashrc