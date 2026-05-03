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
    
    # Load .env file if it exists so we can verify the keys
    try:
        from dotenv import load_dotenv
        if env_file.exists():
            load_dotenv(env_file)
            print(f"Loaded environment from {env_file}")
    except ImportError:
        pass # python-dotenv not available, rely on system env

    # Verify keys from config.yaml
    config_file = project_root / "config.yaml"
    if config_file.exists():
        import re
        content = config_file.read_text()
        # Find all patterns like os.environ/KEY_NAME
        required_vars = set(re.findall(r'os\.environ/([A-Z0-9_]+)', content))
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            print("WARNING: The following environment variables are missing:")
            for var in sorted(missing_vars):
                print(f"  - {var}")
            print("The proxy will still start, but some models may fail to load.\n")
        else:
            print("SUCCESS: All required environment variables are set.\n")

    # Command to run the proxy
    # We use --no-sync for faster startup
    cmd = [
        "uv", "run", "--no-sync", "litellm",
        "--config", str(project_root / "config.yaml"),
        "--port", "4000",
        "--debug"
    ]
    
    print(f"Starting LiteLLM Proxy on port 4000...")
    print(f"Running: {' '.join(cmd)}\n")
    
    # Set PYTHONUNBUFFERED to ensure we see logs immediately
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    try:
        # Run the command and pipe output directly to stdout/stderr
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: LiteLLM Proxy exited with code {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nLiteLLM Proxy stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
