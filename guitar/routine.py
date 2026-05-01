import time
from importlib.resources import files
from pathlib import Path
from typing import Callable

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


def load_routines(user_path: Path = USER_ROUTINES_PATH) -> dict:
    """Load built-in routines merged with any user-defined routines at user_path."""
    data_path = files('guitar.data').joinpath('routines.toml')
    with data_path.open('rb') as f:
        built_in = tomllib.load(f)

    routines = built_in.get('routines', {})

    if user_path.exists():
        with user_path.open('rb') as f:
            user_data = tomllib.load(f)
        routines.update(user_data.get('routines', {}))

    return routines


def activity_dispatch() -> dict[str, Callable[[dict], None]]:
    """Return a mapping of activity name → callable that executes a step dict."""
    from guitar import ear, exercises, scales
    from guitar.timer import start_timer

    def run_scales(step: dict) -> None:
        scales.show_scale(step.get('key', 'C'), step.get('scale', 'major'))
        start_timer(minutes=step.get('minutes', 5), activity='scales')

    def run_spider(step: dict) -> None:
        exercises.spider_walk(
            variant=step.get('variant', 1),
            start_fret=step.get('start_fret', 5),
            bpm=step.get('bpm', 60),
        )

    def run_notes(step: dict) -> None:
        exercises.note_identification(
            rounds=step.get('minutes', 5) * 3,
            string_num=step.get('string', 0),
            fret_max=step.get('fret_max', 12),
        )

    def run_ear_intervals(step: dict) -> None:
        ear.quiz_intervals(rounds=step.get('minutes', 5) * 2)

    def run_ear_chords(step: dict) -> None:
        ear.quiz_chords(rounds=step.get('minutes', 5) * 2)

    def run_timer(step: dict) -> None:
        start_timer(minutes=step.get('minutes', 5), activity=step['activity'])

    return {
        'scales': run_scales,
        'spider': run_spider,
        'notes': run_notes,
        'ear_intervals': run_ear_intervals,
        'ear_chords': run_ear_chords,
    }


def resolve_step(
    step: dict,
    dispatch: dict[str, Callable[[dict], None]],
) -> Callable[[dict], None]:
    """Return the callable for a step, falling back to timer for unknown activities."""
    from guitar.timer import start_timer

    return dispatch.get(step['activity'], lambda s: start_timer(
        minutes=s.get('minutes', 5), activity=s['activity']
    ))


@app.command("list")
def list_routines() -> None:
    """List all available practice routines."""
    routines = load_routines()
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
    routines = load_routines()
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
    routines = load_routines()
    if name not in routines:
        console.print(f"[red]Unknown routine '{name}'.[/red]")
        raise typer.Exit(1)

    r = routines[name]
    steps = r.get('steps', [])
    dispatch = activity_dispatch()
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
            resolve_step(step, dispatch)(step)
        except KeyboardInterrupt:
            console.print("\n[yellow]Step skipped.[/yellow]")

        if i < len(steps):
            console.print("\n[dim]Next step coming up...[/dim]")

    total = int(time.time() - routine_start)
    db.log_session(f"routine:{name}", total)
    m, s = total // 60, total % 60
    console.print(f"\n[bold green]Routine complete! Total time: {m}m {s}s[/bold green]")
