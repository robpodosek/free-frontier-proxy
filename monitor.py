import time
import json
import yaml
import os
import sys
from pathlib import Path
import litellm
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

console = Console()

# Silence LiteLLM warnings and "bullshit" help messages
litellm.set_verbose = False
litellm.suppress_debug_info = True

class HealthMonitor:
    def __init__(self, config_path="config.yaml", stats_path="stats.json"):
        self.config_path = Path(config_path)
        self.stats_path = Path(stats_path)
        self.load_config()
        self.load_stats()
        
    def load_config(self):
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.models = [m['model_name'] for m in self.config.get('model_list', [])]
        # Map model_name to litellm_params for testing
        self.model_map = {m['model_name']: m['litellm_params'] for m in self.config.get('model_list', [])}

    def load_stats(self):
        if self.stats_path.exists():
            try:
                self.stats = json.loads(self.stats_path.read_text())
            except:
                self.stats = {}
        else:
            self.stats = {}

    def save_stats(self):
        self.stats_path.write_text(json.dumps(self.stats, indent=2))

    def check_health(self, model_name):
        params = self.model_map[model_name].copy()
        model_id = params.pop('model')
        
        # Replace os.environ strings with actual values
        for k, v in params.items():
            if isinstance(v, str) and v.startswith("os.environ/"):
                env_var = v.split("/")[-1]
                params[k] = os.environ.get(env_var)

        try:
            # Quick ping test
            start = time.time()
            # Increase timeout for local models which might need to spin up
            timeout = 30 if "local" in model_name or "ollama" in model_id else 10
            
            litellm.completion(
                model=model_id,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
                request_timeout=timeout,
                **params
            )
            latency = time.time() - start
            
            if model_name not in self.stats:
                self.stats[model_name] = {}
            
            self.stats[model_name]["on_cooldown"] = False
            self.stats[model_name]["last_health_check"] = time.time()
            self.stats[model_name]["health_status"] = "OK"
            self.stats[model_name]["latency"] = round(latency, 2)
            if "last_health_error" in self.stats[model_name]:
                del self.stats[model_name]["last_health_error"]
            return True, "OK"
        except Exception as e:
            error_msg = str(e)
            if model_name not in self.stats:
                self.stats[model_name] = {}
            
            # If it's a rate limit, mark as cooldown
            if any(ind in error_msg.lower() for ind in ["429", "rate_limit", "too many requests", "overloaded", "503", "capacity"]):
                self.stats[model_name]["on_cooldown"] = True
                self.stats[model_name]["cooldown_start"] = time.time()
                self.stats[model_name]["health_status"] = "COOLDOWN"
            else:
                self.stats[model_name]["health_status"] = "ERROR"
            
            self.stats[model_name]["last_health_check"] = time.time()
            self.stats[model_name]["last_health_error"] = error_msg[:100]
            return False, error_msg

    def run_loop(self, interval=300):
        """Run the health check loop."""
        with Live(self.generate_table(), refresh_per_second=1) as live:
            while True:
                for model in self.models:
                    # Only check if not on cooldown, or if cooldown might have expired
                    if model in self.stats and self.stats[model].get("on_cooldown"):
                        elapsed = time.time() - self.stats[model].get("cooldown_start", 0)
                        if elapsed < 300: # 5 min cooldown check
                            continue
                    
                    self.check_health(model)
                    self.save_stats()
                    live.update(self.generate_table())
                
                time.sleep(interval)

    def generate_table(self):
        table = Table(title="Proactive Health Monitor", show_header=True, header_style="bold green")
        table.add_column("Model", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Latency", justify="right")
        table.add_column("Last Check", justify="right")
        
        for model in self.models:
            stat = self.stats.get(model, {})
            status = stat.get("health_status", "WAITING")
            
            if status == "OK":
                status_str = "[bold green]ONLINE[/bold green]"
            elif status == "COOLDOWN":
                status_str = "[bold yellow]COOLDOWN[/bold yellow]"
            elif status == "ERROR":
                status_str = "[bold red]ERROR[/bold red]"
            else:
                status_str = "[dim]WAITING[/dim]"
                
            latency = f"{stat.get('latency', '-')}s"
            last_check = "N/A"
            if "last_health_check" in stat:
                diff = int(time.time() - stat["last_health_check"])
                last_check = f"{diff}s ago"
                
            table.add_row(model, status_str, latency, last_check)
            
        return table

if __name__ == "__main__":
    monitor = HealthMonitor()
    # If run with --once, just check all once and exit
    if "--once" in sys.argv:
        console.print("[bold blue]Running single health check pass...[/bold blue]")
        for model in monitor.models:
            success, msg = monitor.check_health(model)
            status = "[green]OK[/green]" if success else f"[red]FAIL[/red] ({msg[:50]})"
            console.print(f" - {model}: {status}")
            monitor.save_stats()
    else:
        monitor.run_loop()
