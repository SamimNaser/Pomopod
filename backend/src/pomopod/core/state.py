from pathlib import Path

from pomopod.core import config
from pomopod.core.constants import DEFAULT_ACTIVE_PROFILE
from pomopod.core.models import Profile

STATE_DIR = Path.home() / ".local" / "share" / "pomopod"
ACTIVE_PROFILE_FILE = STATE_DIR / "active_profile"


def _ensure_state_dir() -> None:
  STATE_DIR.mkdir(parents=True, exist_ok=True)


def get_active_profile_name() -> str | None:
  _ensure_state_dir()

  if not ACTIVE_PROFILE_FILE.exists():
    prof = set_active_profile(DEFAULT_ACTIVE_PROFILE)
    if not prof:
      return None
    return DEFAULT_ACTIVE_PROFILE

  return ACTIVE_PROFILE_FILE.read_text().strip()


def set_active_profile(name: str) -> Profile | None:
  _ensure_state_dir()
  profiles = config.get_profiles()

  if name not in profiles.keys():
    return None

  ACTIVE_PROFILE_FILE.write_text(name)
  return profiles.get(name)
