import time
from importlib.resources import files
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from guitar import db

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

app = typer.Typer(help="Predefined practice routines")
console = Console()

USER_ROUTINES_PATH = Path.home() / '.guitar-practice' / 'routines.toml'


def _load_routines() -> dict:
    # Built-in routines
    data_path = files('guitar.data').joinpath('routines.toml')
    with data_path.open('rb') as f:
        built_in = tomllib.load(f)

    routines = built_in.get('routines', {})

    # User-defined routines (merged, user wins on name collision)
    if USER_ROUTINES_PATH.exists():
        with USER_ROUTINES_PATH.open('rb') as f:
            user_data = tomllib.load(f)
        routines.update(user_data.get('routines', {}))

    return routines


@app.command("list")
def list_routines() -> None:
    """List all available practice routines."""
    routines = _load_routines()
    table = Table(title="Practice Routines", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Display Name")
    table.add_column("Steps", justify="right")
    table.add_column("Description")

    for key, r in routines.items():
        table.add_row(
            key,
            r.get('name', key),
            str(len(r.get('steps', []))),
            r.get('description', ''),
        )

    console.print(table)


@app.command("show")
def show_routine(name: str = typer.Argument(help="Routine name")) -> None:
    """Preview the steps in a routine."""
    routines = _load_routines()
    if name not in routines:
        msg = (
            f"[red]Unknown routine '{name}'. "
            "Run 'guitar routine list' to see options.[/red]"
        )
        console.print(msg)
        raise typer.Exit(1)

    r = routines[name]
    console.print(f"\n[bold]{r.get('name', name)}[/bold]")
    if r.get('description'):
        console.print(f"[dim]{r['description']}[/dim]\n")

    table = Table(show_header=True)
    table.add_column("Step", justify="right", width=4)
    table.add_column("Activity", style="cyan")
    table.add_column("Duration")
    table.add_column("Settings")

    for i, step in enumerate(r.get('steps', []), 1):
        minutes = step.get('minutes', '?')
        settings = {k: v for k, v in step.items() if k not in ('activity', 'minutes')}
        table.add_row(
            str(i), step['activity'], f"{minutes}m", str(settings) if settings else ''
        )

    console.print(table)


@app.command("run")
def run_routine(name: str = typer.Argument(help="Routine name")) -> None:
    """Execute a routine step by step with timers."""

    routines = _load_routines()
    if name not in routines:
        console.print(f"[red]Unknown routine '{name}'.[/red]")
        raise typer.Exit(1)

    r = routines[name]
    steps = r.get('steps', [])
    routine_start = time.time()

    console.print(f"\n[bold]Starting: {r.get('name', name)}[/bold]")
    console.print(f"{len(steps)} steps\n")

    for i, step in enumerate(steps, 1):
        activity = step['activity']
        minutes = step.get('minutes', 5)
        console.print(
            f"[bold cyan]Step {i}/{len(steps)}: {activity} ({minutes}m)[/bold cyan]"
        )
        typer.confirm("Ready? Press Enter to start", default=True)

        try:
            _run_step(step)
        except KeyboardInterrupt:
            console.print("\n[yellow]Step skipped.[/yellow]")

        if i < len(steps):
            console.print("\n[dim]Next step coming up...[/dim]")

    total = int(time.time() - routine_start)
    db.log_session(f"routine:{name}", total)
    m, s = total // 60, total % 60
    console.print(f"\n[bold green]Routine complete! Total time: {m}m {s}s[/bold green]")


def _run_step(step: dict) -> None:
    """Dispatch a routine step to the appropriate sub-command."""
    from guitar import ear, exercises, scales
    from guitar.timer import start_timer

    activity = step['activity']
    minutes = step.get('minutes', 5)

    if activity == 'scales':
        scales.show_scale(step.get('key', 'C'), step.get('scale', 'major'))
        start_timer(minutes=minutes, activity='scales')
    elif activity == 'spider':
        exercises.spider_walk(
            variant=step.get('variant', 1),
            start_fret=step.get('start_fret', 5),
            bpm=step.get('bpm', 60),
        )
    elif activity == 'notes':
        exercises.note_identification(
            rounds=minutes * 3,
            string_num=step.get('string', 0),
            fret_max=step.get('fret_max', 12),
        )
    elif activity == 'ear_intervals':
        ear.quiz_intervals(rounds=minutes * 2)
    elif activity == 'ear_chords':
        ear.quiz_chords(rounds=minutes * 2)
    else:
        start_timer(minutes=minutes, activity=activity)
