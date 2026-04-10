import time
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

from pomopod.core.constants import DEFAULT_ACTIVE_SPACE


class CatppuccinColor(str, Enum):
  ROSEWATER = "rosewater"
  FLAMINGO = "flamingo"
  PINK = "pink"
  MAUVE = "mauve"
  RED = "red"
  MAROON = "maroon"
  PEACH = "peach"
  YELLOW = "yellow"
  GREEN = "green"
  TEAL = "teal"
  SKY = "sky"
  SAPPHIRE = "sapphire"
  BLUE = "blue"
  LAVENDER = "lavender"


def validate_color(v: str) -> str:
  v = v.lower().strip()

  if v in CatppuccinColor.__members__.values():
    return v

  if v.startswith("#"):
    hex = v[1:]
    if len(hex) in (3, 6) and all(c in "0123456789abcdef" for c in hex):
      return v

  raise ValueError(f"Invalid color: {v}. Use Catppuccin colors or #RRGGBB")


ValidatedColor = Annotated[str, BeforeValidator(validate_color)]


class Space(BaseModel):
  focus_duration: int = Field(default=25, ge=1, le=600, description="Focus duration in minutes")
  short_break_duration: int = Field(default=5, ge=1, le=120, description="Short break in minutes")
  long_break_duration: int = Field(default=10, ge=1, le=300, description="Long break in minutes")

  sessions_before_long_break: int = Field(
    default=4, ge=1, le=25, description="Sessions before long break"
  )

  color: ValidatedColor = Field(default=CatppuccinColor.ROSEWATER, description="Color")

  model_config = {
    "str_strip_whitespace": True,
  }


class DaemonSettings(BaseModel):
  host: str = Field(default="127.0.0.1", description="Host")
  port: int = Field(default=8765, description="Port")


class NotificationSettings(BaseModel):
  enabled: bool = Field(default=True, description="Enable notifications")


class Config(BaseModel):
  spaces: dict[str, Space] = Field(
    default_factory=lambda: {DEFAULT_ACTIVE_SPACE: Space()},
    description="Spaces",
  )
  daemon: DaemonSettings = Field(default_factory=DaemonSettings, description="Daemon settings")
  notifications: NotificationSettings = Field(
    default_factory=NotificationSettings, description="Notification settings"
  )


class TimerStateType(str, Enum):
  FOCUS = "FOCUS"
  SHORT_BREAK = "SHORT_BREAK"
  LONG_BREAK = "LONG_BREAK"
  IDLE = "IDLE"


class TimerState(BaseModel):
  space_name: str = DEFAULT_ACTIVE_SPACE
  current_type: TimerStateType = TimerStateType.IDLE
  current_session_number: int = 1
  sessions_before_long_break: int = 4
  is_paused: bool = True
  end_timestamp_ms: int = 0

  def _now(self):
    return int(round(time.time() * 1000))

  def get_time_left_ms(self) -> int:
    remaining = self.end_timestamp_ms - self._now()
    return max(0, remaining)

  def start(self, duration_ms: int):
    """Start the timer with given duration."""
    self.is_paused = False
    self.end_timestamp_ms = self._now() + duration_ms

  def pause(self) -> int:
    """Pause the timer, return remaining time."""
    if self.is_paused:
      return self.get_time_left_ms()

    self.end_timestamp_ms = self.get_time_left_ms()
    self.is_paused = True
    return self.end_timestamp_ms

  def resume(self):
    """Resume the timer with saved remaining."""
    if not self.is_paused:
      return

    remaining = self.end_timestamp_ms
    self.is_paused = False
    self.end_timestamp_ms = self._now() + remaining

  def reset(self):
    """Reset the timer for current session."""
    self.is_paused = True
    self.end_timestamp_ms = 0

  def stop(self):
    """Stop the timer and reset to idle."""
    self.current_type = TimerStateType.IDLE
    self.is_paused = True
    self.end_timestamp_ms = 0
    self.current_session_number = 1

  def get_next_session_type(self) -> TimerStateType:
    """Determine next session after current ends."""
    if self.current_type == TimerStateType.IDLE:
      return TimerStateType.FOCUS
    elif self.current_type == TimerStateType.FOCUS:
      if self.current_session_number >= self.sessions_before_long_break:
        return TimerStateType.LONG_BREAK
      else:
        return TimerStateType.SHORT_BREAK
    else:
      return TimerStateType.FOCUS

  def cycle_session(self):
    """Move to next session after current ends."""
    if self.current_type == TimerStateType.FOCUS:
      self.current_session_number += 1
    self.current_type = self.get_next_session_type()

  def reset_sessions_number(self):
    """Reset the sessions number for current space."""
    if self.current_type == TimerStateType.IDLE:
      return
    self.current_session_number = 1
