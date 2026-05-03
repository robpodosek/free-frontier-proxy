#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def main():
    """
    Main entry point for the LiteLLM Proxy.
    Validates the environment (.env file) and starts the proxy using 'uv run litellm'.
    """
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    
    print("\n--- LiteLLM Proxy Wrapper ---")
    if not env_file.exists():
        print(f"WARNING: No .env file found at {env_file}")
        print("Please copy .env.example to .env and fill in your API keys.")
        print("Continuing with system environment variables...\n")
    else:
        print(f"SUCCESS: Found .env file at {env_file}\n")

    # Command to run the proxy
    cmd = [
        "uv", "run", "litellm",
        "--config", str(project_root / "config.yaml"),
        "--port", "4000"
    ]
    
    print(f"Starting LiteLLM Proxy on port 4000...")
    print(f"Running: {' '.join(cmd)}\n")
    
    try:
        # Run the command and pipe output directly to stdout/stderr
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: LiteLLM Proxy exited with code {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nLiteLLM Proxy stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
