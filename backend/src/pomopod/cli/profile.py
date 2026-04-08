from typing import Optional

import typer
from pydantic import ValidationError
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from pomopod.core import config, state

app = typer.Typer()
console = Console()


def complete_profiles(incomplete: str) -> list[str]:
  return [p for p in config.get_profile_names() if p.startswith(incomplete)]


@app.command(name="ls")
def list_profiles():
  """
  List all pomodoro profiles with details.
  """
  profiles = config.get_profiles()

  headers = ("Name", "Focus", "Short Break", "Long Break", "Sessions", "Color")
  table = Table(*headers, title="Profiles")

  for name, prof in profiles.items():
    table.add_row(
      name,
      str(prof.focus_duration),
      str(prof.short_break_duration),
      str(prof.long_break_duration),
      str(prof.sessions_until_long_break),
      str(prof.color),
    )

  console.print(table)


@app.command(name="set")
def set_profile(
  name: str = typer.Argument(
    ...,
    help="Name of the pomodoro profile",
    autocompletion=complete_profiles,
  ),
):
  """
  Set the active pomodoro profile.
  """
  prof = state.set_active_profile(name)
  if not prof:
    rprint(f'Profile [bold red]"{name}"[/bold red] does not exist')
  else:
    rprint(f'Active profile set to [bold green]"{name}"[/bold green]')


@app.command(name="add")
def add_profile(
  name: str = typer.Argument(
    ...,
    help="Name of the new pomodoro profile",
  ),
  data: Optional[str] = typer.Option(
    None,
    "--data",
    "-d",
    help="Data to create the profile from",
  ),
):
  """
  Add a new pomodoro profile.
  """
  if name in config.get_profile_names():
    rprint(f'Profile [bold red]"{name}"[/bold red] already exists')
    return

  if data and len(data.split()) < 5:
    rprint("Given data is not enough to create a profile.")
    data = None

  if not data:
    rprint("Enter the durations in minutes.")
    focus_duration = typer.prompt("Focus duration", type=int)
    short_break_duration = typer.prompt("Short break duration", type=int)
    long_break_duration = typer.prompt("Long break duration", type=int)
    sessions_before_long_break = typer.prompt("Sessions", type=int)
    color = typer.prompt("Color", type=str)
  else:
    focus_duration, short_break_duration, long_break_duration, sessions_before_long_break, color = (
      data.split()
    )

  try:
    prof = config.Profile.model_validate(
      {
        "focus_duration": focus_duration,
        "short_break_duration": short_break_duration,
        "long_break_duration": long_break_duration,
        "sessions_until_long_break": sessions_before_long_break,
        "color": color,
      }
    )
  except ValidationError as e:
    rprint("[bold red]\nInvalid profile\n[/bold red]")
    rprint(f"Errors: {e.error_count()}")
    for error in e.errors():
      rprint(f"{error['loc']}: {error['msg']}")
    return

  prof = config.add_profile(name, prof)

  if not prof:
    rprint(f'Profile [bold red]"{name}"[/bold red] already exists')
  else:
    rprint(f'Profile [bold green]"{name}"[/bold green] added')


@app.command(name="rm")
def remove_profile(
  name: str = typer.Argument(
    ...,
    help="Name of the profile to remove",
    autocompletion=complete_profiles,
  ),
  force: bool = typer.Option(
    False,
    "--force",
    "-f",
    help="Delete without confirmation",
  ),
):
  """
  Remove a pomodoro profile.
  """
  if name not in config.get_profile_names():
    rprint(f'Profile [bold red]"{name}"[/bold red] does not exist')
    return

  if name == state.get_active_profile_name():
    rprint(f'Cannot delete active profile [bold red]"{name}"[/bold red]')
    return

  if not force:
    typer.confirm(f'Delete the "{name}" profile?', abort=True)

  prof = config.remove_profile(name)

  if not prof:
    rprint(f'Profile [bold red]"{name}"[/bold red] does not exist')
  else:
    rprint(f'Profile [bold green]"{name}"[/bold green] removed permanantly')


@app.command(name="rename")
def rename_profile(
  name: str = typer.Argument(
    ...,
    help="Name of the profile to rename",
    autocompletion=complete_profiles,
  ),
  new_name: Optional[str] = typer.Option(
    None,
    "--new-name",
    "-to",
    help="New name of the profile",
  ),
):
  """
  Rename a pomodoro profile.
  """
  if name not in config.get_profile_names():
    rprint(f'Profile [bold red]"{name}"[/bold red] does not exist')
    return

  if not new_name:
    new_name_input = typer.prompt(f'New name for "{name}" profile')
    new_name = str(new_name_input)

  if new_name in config.get_profile_names():
    rprint(f'Profile [bold red]"{name}"[/bold red] already exists')
    return

  rename_active_profile = name == state.get_active_profile_name()

  prof = config.remove_profile(name)

  if not prof:
    rprint(f'Profile [bold red]"{name}"[/bold red] does not exist')
    return

  prof = config.add_profile(new_name, prof)

  if not prof:
    rprint(f'Profile [bold red]"{name}"[/bold red] already exists')
  else:
    rprint(
      f'Profile [bold green]"{name}"[/bold green] renamed to [bold green]"{new_name}"[/bold green]'
    )

  if rename_active_profile:
    set_profile(new_name)
