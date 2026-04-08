
import os
from dotenv import load_dotenv

load_dotenv()

def _get_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")

def _get_int(key: str, default: int | None = None) -> int:
    val = os.getenv(key)
    if val is None:
        if default is None:
            raise RuntimeError(f"Missing required env: {key}")
        return default
    return int(val)

def _get_str(key: str, default: str | None = None) -> str:
    val = os.getenv(key)
    if val is None:
        if default is None:
            raise RuntimeError(f"Missing required env: {key}")
        return default
    return val


class Config:
    REDIS = {
        "host": _get_str("REDIS_HOST"),
        "port": _get_int("REDIS_PORT"),
        "db": _get_int("REDIS_DATABASE_ID", 0),
    }

    APP = {
        "host": _get_str("APP_HOST"),
        "port": _get_int("APP_PORT", 8000),
        "reload": _get_bool("DEBUG", False),
    }

    TEMPORAL = {
        "address": _get_str("TEMPORAL_ADDRESS"),
        "namespace": _get_str("TEMPORAL_NAMESPACE", "default"),
    }

    BACKEND = {
        # "host": _get_str("BACKEND_HOST", "localhost"),
        # "port": _get_int("BACKEND_PORT", 8000),
        # "secured": _get_bool("BACKEND_SECURED", False),
        "base_url": _get_str("BACKEND_BASE_URL"),
        "api_key": _get_str("BACKEND_API_KEY"),
    }

    # BACKEND["base_url"] = (
    #     f"http{'s' if BACKEND['secured'] else ''}://"
    #     f"{BACKEND['host']}:{BACKEND['port']}"
    # )
