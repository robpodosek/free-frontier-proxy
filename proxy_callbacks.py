import litellm
from litellm.integrations.custom_logger import CustomLogger
import time
import json
import os
from pathlib import Path

class FreeTierResilienceLogger(CustomLogger):
    def __init__(self):
        self.stats_file = Path(__file__).parent / "stats.json"
        self.cooldown_duration = int(os.environ.get("PROXY_COOLDOWN_SECONDS", 300)) # Default 5 mins
        self.load_stats()

    def load_stats(self):
        if self.stats_file.exists():
            try:
                self.stats = json.loads(self.stats_file.read_text())
            except:
                self.stats = {}
        else:
            self.stats = {}

    def save_stats(self):
        try:
            self.stats_file.write_text(json.dumps(self.stats, indent=2))
        except Exception as e:
            print(f"Error saving stats: {e}")

    def log_pre_api_call(self, model, messages, kwargs): 
        """
        Triggered before the API call is made. 
        We use this to 'fail fast' if we know a model is on cooldown.
        """
        self.load_stats()
        model_id = kwargs.get("model", model)
        
        if model_id in self.stats:
            model_stats = self.stats[model_id]
            if model_stats.get("on_cooldown"):
                cooldown_start = model_stats.get("cooldown_start", 0)
                elapsed = time.time() - cooldown_start
                
                if elapsed < self.cooldown_duration:
                    remaining = int(self.cooldown_duration - elapsed)
                    # Raising RateLimitError here triggers LiteLLM Router fallbacks
                    raise litellm.exceptions.RateLimitError(
                        message=f"Model {model_id} is on local cooldown for another {remaining}s",
                        model=model_id,
                        llm_provider="custom-resilience"
                    )
                else:
                    # Cooldown expired
                    model_stats["on_cooldown"] = False
                    self.save_stats()

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        model = kwargs.get("model", "unknown")
        if model not in self.stats:
            self.stats[model] = {"success": 0, "failure": 0, "total_tokens": 0}
        
        self.stats[model]["success"] += 1
        self.stats[model]["total_tokens"] += getattr(response_obj.usage, "total_tokens", 0)
        self.stats[model]["last_success"] = time.time()
        self.stats[model]["on_cooldown"] = False # Reset cooldown on success
        self.save_stats()

    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        model = kwargs.get("model", "unknown")
        exception = str(kwargs.get("exception", ""))
        
        if model not in self.stats:
            self.stats[model] = {"success": 0, "failure": 0, "total_tokens": 0}
        
        self.stats[model]["failure"] += 1
        self.stats[model]["last_failure"] = time.time()
        self.stats[model]["last_error"] = exception
        
        # If it's a rate limit or a service error, trigger cooldown
        error_indicators = ["429", "rate_limit", "too many requests", "overloaded", "503", "capacity"]
        if any(indicator in exception.lower() for indicator in error_indicators):
            self.stats[model]["on_cooldown"] = True
            self.stats[model]["cooldown_start"] = time.time()
            
        self.save_stats()

# Initialize the custom logger
resilience_logger = FreeTierResilienceLogger()
