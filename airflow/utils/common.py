import hashlib
import os

import yaml
from fuzzywuzzy import process


def rename_place_id(place_name: str) -> str:
    """
    Rename place_id to a hash value (md5)
    (暫時定義一個編碼規則, 之後未來可以根據業務需求調整)

    Args:
        place_name (str): The name of the place

    Returns:
        str: The hash value of the place name
    """
    return hashlib.md5(place_name.encode("utf-8")).hexdigest()


def mapping_place_id(place_name: str, df) -> str:
    best_match, best_score, *_ = process.extractOne(place_name, df["attraction_name"])

    if best_match:
        return df[df["attraction_name"] == best_match]["attraction_id"].values[0]

    return None


def resolve_env_variables(config: dict) -> dict:
    """
    Recursively resolve environment variables in the configuration.

    Args:
        config (dict): The configuration dictionary.

    Returns:
        dict: The configuration dictionary with environment variables resolved.
    """
    if isinstance(config, dict):
        for key, value in config.items():
            config[key] = resolve_env_variables(value)
    elif isinstance(config, str) and config.startswith("ENV_"):
        env_var = config.split("ENV_")[1]
        return os.getenv(env_var, config)  # Default to original if not found
    return config


def add_env_suffix(config: dict) -> dict:
    """
    Add environment suffix to table names in the configuration.

    Args:
        config (dict): The configuration dictionary.

    Returns:
        dict: The configuration dictionary with environment suffix added to table names.
    """
    env_suffix = os.getenv("ENV_SUBFIX", config.get("env", ""))
    if "gcp" in config and "table" in config["gcp"]:
        for key, value in config["gcp"]["table"].items():
            if isinstance(value, str) and not value.startswith("ENV_"):
                config["gcp"]["table"][key] = f"{env_suffix}-{value}"
    return config


def load_config() -> dict:
    """
    Load and process the configuration from a YAML file.

    Args:
        None

    Returns:
        dict: The configuration dictionary.
    """
    config_path = os.path.join(os.path.dirname(__file__), "config.yml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Resolve environment variables
    config = resolve_env_variables(config)

    # Add environment suffix to table names
    config = add_env_suffix(config)

    return config
