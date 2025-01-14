FROM python:3.11-slim

WORKDIR /app

# Install uv globally
RUN pip install uv

# Copy the entire project into the container
COPY . .

# Install dependencies with uv
RUN uv install

# Expose the port your app uses
EXPOSE 5000

# Command to run your app
CMD ["uv", "run", "python", "run.py"]
