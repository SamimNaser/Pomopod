import json
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from pomopod.core import state
from pomopod.core.models import Config, DaemonSettings, NotificationSettings, Profile

CONFIG_DIR = Path.home() / ".config" / "pomopod"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _ensure_config_dir() -> None:
  CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _get_default_config() -> Config:
  return Config()


def _load_config() -> Config:
  if not CONFIG_FILE.exists():
    _ensure_config_dir()
    config = _get_default_config()
    _save_config(config)
    return config

  with open(CONFIG_FILE, "r") as f:
    config_json = json.load(f)

  try:
    config = Config.model_validate(config_json)
  except ValidationError:
    return _get_default_config()

  return config


def _save_config(config: Config) -> None:
  _ensure_config_dir()
  with open(CONFIG_FILE, "w") as f:
    json.dump(config.model_dump(), f, indent=2)


def get_profiles() -> dict[str, Profile]:
  config = _load_config()
  return config.profiles


def get_profile_names() -> list[str]:
  config = _load_config()
  return list(config.profiles.keys())


def get_active_profile() -> Profile | None:
  config = _load_config()

  active_profile_name = state.get_active_profile_name()
  if active_profile_name is None:
    return None

  return config.profiles.get(active_profile_name)


def add_profile(name: str, profile: Profile) -> Profile | None:
  config = _load_config()

  if name in list(config.profiles.keys()):
    return None

  config.profiles[name] = profile
  _save_config(config)
  return profile


def remove_profile(name: str) -> Profile | None:
  config = _load_config()

  if name not in list(config.profiles.keys()):
    return None

  profile = config.profiles.pop(name)
  _save_config(config)
  return profile


def get_daemon_settings() -> DaemonSettings:
  config = _load_config()
  return config.daemon


def update_daemon_settings(
  host: Optional[str] = None, port: Optional[int] = None
) -> DaemonSettings:
  config = _load_config()
  if not host:
    host = config.daemon.host
  if not port:
    port = config.daemon.port

  config.daemon = DaemonSettings.model_validate({"host": host, "port": port})
  _save_config(config)
  return config.daemon


def get_notification_settings() -> NotificationSettings:
  config = _load_config()
  return config.notifications


def update_notification_settings(enabled: bool) -> NotificationSettings:
  config = _load_config()
  config.notifications = NotificationSettings(enabled=enabled)
  _save_config(config)
  return config.notifications
