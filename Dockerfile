FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Keep Python output unbuffered for immediate log visibility
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependency definition first for caching
COPY pyproject.toml ./

# Install the project dependencies
RUN uv sync --no-dev

# Copy the rest of the application files
COPY . .

# Expose the port litellm proxy runs on
EXPOSE 4000

# Run the proxy wrapper
CMD ["uv", "run", "main.py"]
