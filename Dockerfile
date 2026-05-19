# Use an official, lightweight Python runtime as a parent image
FROM python:3.11-slim

# Force python to output all logs directly to the console without buffering.
# This ensures your logs show up in GCP Cloud Logging in real-time.
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker's build caching.
# This prevents re-installing packages if you only modified your Python code.
COPY requirements.txt .

# Install dependencies cleanly without caching the index files
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source package and the entrypoint script into the container
COPY src/ ./src/
COPY main.py .

# Define the command to run your pipeline when the container fires up
CMD ["python", "main.py"]