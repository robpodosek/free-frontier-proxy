# LiteLLM Proxy

A simple, robust wrapper for [LiteLLM Proxy](https://github.com/BerriAI/litellm) with a tiered fallback configuration. This proxy allows you to access multiple LLM providers (Gemini, Claude, GPT-4o, Groq, etc.) through a single OpenAI-compatible API endpoint.

## Features

- **Unified API**: Access multiple providers via one endpoint.
- **Tiered Fallbacks**: Automatically switches to alternative models if the primary one hits rate limits (429).
- **Environment Driven**: Easily configure API keys via a `.env` file.
- **Python Wrapper**: Simple `main.py` to validate environment and launch the proxy using `uv`.

## Prerequisites

- [Python 3.12+](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management)

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/robpodosek/litellm-proxy.git
   cd litellm-proxy
   ```

2. **Configure Environment Variables:**
   Copy the example environment file and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and add your keys for:
   - Google AI Studio (Gemini)
   - GitHub Models Marketplace (Claude, GPT-4o, Llama)
   - Groq
   - OpenRouter
   - NVIDIA NIM

3. **Install Dependencies:**
   Dependencies are managed by `uv`. They will be installed automatically the first time you run the script.

## Usage

Start the proxy by running:

```bash
python3 main.py
```

The proxy will start on `http://localhost:4000`.

### Example API Call

You can now use the proxy with any OpenAI-compatible client:

```bash
curl --request POST \
  --url http://localhost:4000/v1/chat/completions \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "gemini-pro",
    "messages": [
      {
        "role": "user",
        "content": "Hello!"
      }
    ]
  }'
```

## Configuration

The proxy behavior is defined in `config.yaml`. You can modify the `model_list` and `router_settings` to add new models or change fallback priorities.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
