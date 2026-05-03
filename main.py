#!/usr/bin/env python3
import os, subprocess, sys, re
from pathlib import Path

def main():
    root = Path(__file__).parent
    env_file = root / ".env"
    
    print("\n--- LiteLLM Proxy Wrapper ---")
    
    # Load .env file if it exists so we can verify the keys
    try:
        from dotenv import load_dotenv
        if env_file.exists():
            load_dotenv(env_file)
            print(f"Loaded environment from {env_file}")
    except ImportError:
        pass

    # Verify keys from config.yaml
    if (cfg := root / "config.yaml").exists():
        required = set(re.findall(r'os\.environ/([A-Z0-9_]+)', cfg.read_text()))
        if missing := [v for v in sorted(required) if not os.environ.get(v)]:
            print("WARNING: The following environment variables are missing:")
            for var in missing:
                print(f"  - {var}")
            print("The proxy will still start, but some models may fail to load.\n")
        else:
            print("SUCCESS: All required environment variables are set.\n")

    cmd = ["uv", "run", "--no-sync", "litellm", "--config", str(cfg), "--port", "4000", "--debug"]
    print(f"Starting LiteLLM Proxy on port 4000...\nRunning: {' '.join(cmd)}\n")
    
    try:
        subprocess.run(cmd, check=True, env={**os.environ, "PYTHONUNBUFFERED": "1"})
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nLiteLLM Proxy stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
