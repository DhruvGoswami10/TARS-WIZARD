"""Rich terminal UI for TARS — replaces Tkinter GUI."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from tars.ui import status

console = Console()


def print_banner():
    """Print the TARS startup banner."""
    banner = Text()
    banner.append("████████╗ █████╗ ██████╗ ███████╗\n", style="bold #f8d566")
    banner.append("╚══██╔══╝██╔══██╗██╔══██╗██╔════╝\n", style="bold #f8d566")
    banner.append("   ██║   ███████║██████╔╝███████╗\n", style="bold #f8d566")
    banner.append("   ██║   ██╔══██║██╔══██╗╚════██║\n", style="bold #f8d566")
    banner.append("   ██║   ██║  ██║██║  ██║███████║\n", style="bold #f8d566")
    banner.append("   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝\n", style="bold #f8d566")
    banner.append("  TARS-WIZARD v2.0", style="bold white")
    console.print(banner)


def print_status_panel():
    """Print startup status showing detected devices and services."""
    checks = status.get_all_status()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Component", style="bold")
    table.add_column("Status")

    for name, (ok, message) in checks.items():
        icon = "[green]✓[/green]" if ok else "[red]✗[/red]"
        style = "green" if ok else "dim"
        table.add_row(f"{icon} {name}", f"[{style}]{message}[/{style}]")

    console.print(Panel(table, title="[bold]System Status[/bold]", border_style="cyan"))


def print_settings(state):
    """Print current TARS personality settings."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Setting", style="bold")
    table.add_column("Value")

    table.add_row("Language", state.current_language.capitalize())
    table.add_row("Humor", f"{int(state.humor * 100)}%")
    table.add_row("Honesty", f"{int(state.honesty * 100)}%")

    console.print(Panel(table, title="[bold]Settings[/bold]", border_style="cyan"))


def print_help():
    """Print available commands."""
    table = Table(show_header=True, header_style="bold #f8d566", box=None)
    table.add_column("Command", style="bold")
    table.add_column("Description")

    table.add_row("move forward", "Walk forward one step")
    table.add_row("turn left / turn right", "Turn in place")
    table.add_row("speak [language]", "Switch language (e.g. 'speak spanish')")
    table.add_row("time", "Get current time")
    table.add_row("weather", "Get weather report")
    table.add_row("what do you see", "Describe the scene (camera)")
    table.add_row("how many people", "Count people (YOLO)")
    table.add_row("greet everyone", "Greet visible people")
    table.add_row("set humor to [N]%", "Adjust sarcasm level")
    table.add_row("set honesty to [N]%", "Adjust honesty level")
    table.add_row("settings", "Show current settings")
    table.add_row("help", "Show this help")
    table.add_row("stop / exit / quit", "Shut down TARS")
    table.add_row("", "")
    table.add_row("[dim]anything else[/dim]", "[dim]Chat with TARS via AI[/dim]")

    console.print(Panel(table, title="[bold]Commands[/bold]", border_style="cyan"))


def print_user(text):
    """Print user input."""
    console.print(f"[bold green]H:[/bold green] {text}")


def print_tars(text):
    """Print TARS response."""
    console.print(f"[bold #f8d566]TARS:[/bold #f8d566] {text}")


def print_system(text):
    """Print system message."""
    console.print(f"[dim]{text}[/dim]")


def print_error(text):
    """Print error message."""
    console.print(f"[bold red]Error:[/bold red] {text}")


def get_input():
    """Get user input with TARS prompt."""
    try:
        return console.input("[bold #f8d566]TARS>[/bold #f8d566] ").strip()
    except (EOFError, KeyboardInterrupt):
        return None
