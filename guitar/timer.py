import time
from datetime import datetime

import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from guitar import db

app = typer.Typer(help="Practice timer and session history")
console = Console()


def format_duration(seconds: int) -> str:
    """Return a human-readable duration string, e.g. '5m 3s'."""
    return f"{seconds // 60}m {seconds % 60}s"


def progress_bar(elapsed: int, total: int, width: int = 30) -> str:
    """Return a filled/empty block progress bar string."""
    filled = int((elapsed / total) * width) if total else 0
    return '█' * filled + '░' * (width - filled)


def render_timer_panel(
    elapsed: int, total: int, activity: str
) -> Panel:
    """Return a Rich Panel showing countdown and progress — no IO."""
    remaining = total - elapsed
    mins, secs = divmod(remaining, 60)
    bar = progress_bar(elapsed, total)
    return Panel(
        f"[cyan]{bar}[/cyan]\n\n  [bold]{mins:02d}:{secs:02d}[/bold] remaining",
        title=f"[green]{activity}[/green]",
        width=50,
    )


@app.command("start")
def start_timer(  # pragma: no cover
    minutes: int = typer.Option(
        20, "--minutes", "-m", help="Session length in minutes"
    ),
    activity: str = typer.Option("timer", "--activity", "-a", help="Activity label"),
) -> None:
    """Run a countdown timer and log the session."""
    total_seconds = minutes * 60
    started = datetime.now()
    console.print(
        f"\n[bold]Starting {minutes}-minute session[/bold]  (Ctrl-C to stop early)\n"
    )

    try:
        with Live(refresh_per_second=1, console=console) as live:
            for elapsed in range(total_seconds + 1):
                live.update(render_timer_panel(elapsed, total_seconds, activity))
                if elapsed < total_seconds:
                    time.sleep(1)
    except KeyboardInterrupt:
        elapsed_seconds = int((datetime.now() - started).total_seconds())
        dur = format_duration(elapsed_seconds)
        console.print(f"\n[yellow]Session stopped early at {dur}[/yellow]")
        _finish_session(activity, elapsed_seconds)
        return

    console.print("\n[bold green]Session complete![/bold green]")
    _finish_session(activity, total_seconds)


def _finish_session(activity: str, duration_seconds: int) -> None:  # pragma: no cover
    notes = typer.prompt("Session notes (optional, press Enter to skip)", default="")
    db.log_session(activity, duration_seconds, notes)
    console.print(f"[dim]Logged {format_duration(duration_seconds)} session.[/dim]")


@app.command("history")
def show_history(  # pragma: no cover
    limit: int = typer.Option(20, "--limit", "-n", help="Number of sessions to show"),
) -> None:
    """Show recent practice sessions."""
    rows = db.get_history(limit)
    if not rows:
        console.print("[dim]No sessions logged yet.[/dim]")
        return

    table = Table(title="Practice History", show_header=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Date")
    table.add_column("Activity", style="cyan")
    table.add_column("Duration")
    table.add_column("Notes")

    for row in rows:
        dt = datetime.fromisoformat(row['started_at'])
        table.add_row(
            str(row['id']),
            dt.strftime('%Y-%m-%d %H:%M'),
            row['activity'],
            format_duration(row['duration_seconds']),
            row['notes'] or '',
        )

    console.print(table)


@app.command("streak")
def show_streak() -> None:  # pragma: no cover
    """Show your current daily practice streak."""
    streak = db.get_streak()
    if streak == 0:
        console.print("[yellow]No streak yet — log a session to start one![/yellow]")
    elif streak == 1:
        console.print("[green]🔥 1-day streak — keep it going![/green]")
    else:
        console.print(f"[bold green]🔥 {streak}-day streak![/bold green]")
