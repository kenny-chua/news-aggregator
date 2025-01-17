# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install uv and dependencies
RUN pip install uv

# Expose port 5001 for the container
EXPOSE 5001

# Command to run your app
CMD ["uv", "run", "python", "run.py"]
