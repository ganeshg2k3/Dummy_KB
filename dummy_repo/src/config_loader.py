"""Dummy config loader module - exercises branching, exceptions, and
control-flow complexity for knowledge graph testing."""

import os


class ConfigError(Exception):
    """Raised when a config file is missing or malformed."""
    pass


def load_config(path, required_keys=None):
    """Load a simple key=value config file from disk."""
    if not os.path.exists(path):
        raise ConfigError(f"Config file not found: {path}")

    config = {}
    with open(path, "r") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ConfigError(f"Invalid line {line_num} in {path}: {line}")
            key, _, value = line.partition("=")
            config[key.strip()] = value.strip()

    if required_keys:
        missing = [k for k in required_keys if k not in config]
        if missing:
            raise ConfigError(f"Missing required keys: {missing}")

    return config


def get_bool(config, key, default=False):
    """Coerce a config string value to a boolean."""
    if key not in config:
        return default
    value = config[key].lower()
    if value in ("true", "yes", "1", "on"):
        return True
    elif value in ("false", "no", "0", "off"):
        return False
    else:
        raise ConfigError(f"Cannot parse boolean for key '{key}': {config[key]}")


def get_int(config, key, default=None):
    """Coerce a config string value to an int, with fallback on failure."""
    if key not in config:
        return default
    try:
        return int(config[key])
    except ValueError:
        return default


def merge_configs(base_config, override_config):
    """Merge two config dicts, with override_config values taking precedence."""
    merged = dict(base_config)
    for key, value in override_config.items():
        merged[key] = value
    return merged


def validate_environment(config, allowed_envs=("dev", "staging", "prod")):
    """Check that config['environment'] is one of the allowed environments."""
    env = config.get("environment")
    if env is None:
        raise ConfigError("Config is missing 'environment' key")
    if env not in allowed_envs:
        raise ConfigError(f"Unknown environment '{env}', must be one of {allowed_envs}")
    return True
