# Step 1: Specify the base image, ensuring AMD64 compatibility.
# Using a slim image keeps the final build size small.
FROM --platform=linux/amd64 python:3.9-slim-buster

# Step 2: Set the working directory inside the container.
WORKDIR /app

# Step 3: Copy the requirements file first to leverage Docker's layer caching.
# This prevents re-installing dependencies on every code change.
COPY requirements.txt .

# Step 4: Install the Python dependencies.
# --no-cache-dir ensures no unnecessary cache files are stored, reducing image size.
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application code into the container.
COPY process.py .

# Step 6: Define the entry point. This command will run automatically
# when the container starts, executing our processing script.
ENTRYPOINT ["python", "process.py"]