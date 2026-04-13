from rich import print as rprint

from pomopod.core.config import is_config_correct
from pomopod.core.state import _is_active_space_set

if not is_config_correct():
  rprint("[bold red]Config file is not correct.[/bold red]\n Please run 'pomopod config init'")

if not _is_active_space_set():
  rprint("[bold red]No active space set.[/bold red]\n Please run 'pomopod space set <space_name>'")
