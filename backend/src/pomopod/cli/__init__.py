from pathlib import Path
from typing import Optional

import typer

from pomopod.cli.config import app as config
from pomopod.cli.profile import app as profile

app = typer.Typer(help="Pomopod CLI")
app.add_typer(
  profile,
  name="profile",
  help="Manage pomodoro profiles",
)
app.add_typer(
  config,
  name="config",
  help="Manage pomodoro profiles",
)


# @app.command(name="tui")
# def tui():
#   typer.echo("TUI will come soon")
#
#
# @app.command(name="gui")
# def gui():
#   typer.echo("GUI will come soon")


@app.command(name="serve")
def serve(host: str = "0.0.0.0", port: int = 8089, config: Optional[Path] = None):
  if port < 0 or port > 65535:
    typer.secho("Port must be between 0 and 65535", color=True, fg=typer.colors.RED)
    return

  if host == "":
    typer.echo("Host cannot be empty")
    return
  elif ("." in host and host.split(".") != 4) or (":" in host and host.split(":") != 6):
    typer.echo("Invalid host")
    return

  if config:
    typer.echo(f"Using custom config file at `{config}`")
  else:
    typer.echo("Using default config file at `~/.config/pomopod/config.yaml`")

  typer.echo("Starting server...")


@app.command(name="join")
def join(room_code: str):
  typer.echo(f"Joining room: {room_code}!")


@app.command(name="status")
def status():
  typer.echo("Fetching status...")
