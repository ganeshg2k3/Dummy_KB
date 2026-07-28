"""Dummy CLI entry point - imports from config_loader and retry_utils to
exercise cross-file dependency edges in the knowledge graph."""

import sys

from config_loader import load_config, get_bool, get_int, validate_environment
from retry_utils import retry, batch_retry_calls, fibonacci


@retry(max_attempts=2, backoff_seconds=0.1)
def load_app_config(path):
    """Load and validate the application config, retrying on transient errors."""
    config = load_config(path, required_keys=["environment", "log_level"])
    validate_environment(config)
    return config


def build_runtime_settings(config):
    """Translate raw config strings into typed runtime settings."""
    settings = {
        "debug": get_bool(config, "debug", default=False),
        "max_workers": get_int(config, "max_workers", default=4),
        "environment": config["environment"],
        "log_level": config.get("log_level", "INFO"),
    }
    return settings


def process_items(items):
    """Run a dummy transformation over a list of items using batch_retry_calls."""
    def transform(item):
        if item < 0:
            raise ValueError(f"Cannot process negative item: {item}")
        return fibonacci(item)

    results, failures = batch_retry_calls(items, transform, max_attempts=2)
    return results, failures


def main(config_path="app.conf"):
    """CLI entry point: load config, build settings, run a demo batch job."""
    try:
        config = load_app_config(config_path)
    except Exception as e:
        print(f"Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)

    settings = build_runtime_settings(config)
    print(f"Running in {settings['environment']} mode, log_level={settings['log_level']}")

    demo_items = [3, 5, 8, -1, 10]
    results, failures = process_items(demo_items)

    print(f"Processed {len(results)} items successfully")
    if failures:
        print(f"{len(failures)} item(s) failed: {failures}")

    return settings, results, failures


if __name__ == "__main__":
    main()
