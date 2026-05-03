# Free Frontier Proxy

This project provides a robust, resilient proxy that enables free access to frontier-class AI models. 

Built on top of [LiteLLM Proxy](https://github.com/BerriAI/litellm), this repository is specifically configured to leverage high-quality free API tiers. By combining providers such as GitHub Models, Google AI Studio, Groq, and OpenRouter, the proxy creates a highly available and unified OpenAI-compatible endpoint. If a primary free tier encounters a rate limit, the proxy automatically falls back to the next available provider. This ensures your applications remain operational without incurring inference costs.

## Core Architecture and Value Proposition

API costs can scale rapidly in AI application development. This proxy mitigates those costs by acting as an intelligent load balancer across established free APIs:

- **Frontier Models:** Access models including `gemini-1.5-pro`, `gpt-4o`, `claude-3-5-sonnet`, and `llama-3.1-405b` at no cost using GitHub developer tokens and Google AI Studio.
- **Graceful Fallbacks:** When a primary API key reaches its rate limit (429 error), the proxy automatically cascades the request through a prioritized list of alternatives. For example, a failed request to Gemini Pro will fallback to Claude 3.5 Sonnet, and subsequently to Groq Llama 70B.
- **High-Performance Open Source:** Utilizes Groq and NVIDIA NIM for high-throughput inference on leading open-weight models.
- **Ultimate Reliability:** Incorporates OpenRouter's free tier and local CPU-bound models (via `ollama`) as a final safeguard to ensure a response is always generated.

## Prerequisites

- [Python 3.12+](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management)

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/robpodosek/free-frontier-proxy.git
   cd free-frontier-proxy
   ```

2. **Configure Environment Variables:**
   Copy the example environment file and add your API keys:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and configure your keys. You do not need to populate all keys to start, but configuring multiple providers increases the resilience of the proxy.
   - Google AI Studio (Gemini)
   - GitHub Models Marketplace (Claude, GPT-4o, Llama)
   - Groq
   - OpenRouter
   - NVIDIA NIM

3. **Install Dependencies:**
   Dependencies are managed by `uv` and will be installed automatically the first time the script is executed.

## Usage

### Local Development
For development and local testing, run the script directly. This provides instant logs and allows you to test code changes immediately.

```bash
uv run main.py
```

### Production Deployment (Docker)
For hosting on a VPS, the recommended approach is Docker. This ensures the proxy runs silently in the background and automatically restarts on server reboots.

1. Ensure your API keys are available. If you use a tool like `direnv` instead of a `.env` file, the `docker-compose.yml` is configured to inherit keys from your host shell automatically.
2. Build and start the container in detached mode:
   ```bash
   docker compose up -d --build
   ```
3. To view real-time logs:
   ```bash
   docker compose logs -f
   ```
4. To stop the container:
   ```bash
   docker compose down
   ```

The proxy will initialize and listen on `http://localhost:4000`.

### Example API Call

The proxy functions as a drop-in replacement for any OpenAI-compatible client. Configure your client's base URL to `http://localhost:4000/v1`.

```bash
curl --request POST \
  --url http://localhost:4000/v1/chat/completions \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "gemini-pro",
    "messages": [
      {
        "role": "user",
        "content": "Provide a brief summary of how this proxy functions."
      }
    ]
  }'
```

## Configuration

The routing logic and fallback cascades are defined in `config.yaml`. You can edit this file to add new models, change providers, or adjust the fallback priorities to suit your requirements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
