# Use the official Python image from the Docker Hub
FROM python:3.10-slim


# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the dependency files to the working directory
COPY poetry.lock pyproject.toml ./

# Upgrade pip and install Poetry
RUN pip install --upgrade pip && \
    pip install poetry

# Copy the application code to the working directory
COPY . .

# Install dependencies including fastapi[all] and uvicorn
RUN poetry install --no-root

# Ensure uvicorn is installed in the correct environment
RUN poetry run uvicorn --version

# Expose the application port
EXPOSE 8000

# Copy environment file
COPY .env .env

# Set environment variables from .env file
ENV $(cat .env | grep -v ^# | xargs)


# Set the default command to run the application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
