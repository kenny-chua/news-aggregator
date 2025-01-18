# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install project dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5001 for the Flask app
EXPOSE 5001

# Command to run your Flask app
CMD ["python", "run.py"]
