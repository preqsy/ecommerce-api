# Use a Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy only the necessary files for dependency installation
COPY poetry.lock pyproject.toml ./

# Upgrade pip and install Poetry
RUN pip install --upgrade pip && \
    pip install poetry

# Copy the entire application code
COPY . .

# Install dependencies for Arq
RUN poetry install --no-root

# Expose any necessary ports for Arq (if applicable)
# EXPOSE ...

# Command to run Arq
CMD ["poetry", "run", "arq", "task_queue.main.WorkerSettings"]
