# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run the A2A server. 
# Cloud Run automatically sets the PORT environment variable to 8080 by default.
CMD sh -c "uvicorn app.a2a.a2a_agent:a2a_app --host 0.0.0.0 --port ${PORT:-8080}"
