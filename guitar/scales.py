import random
from dataclasses import dataclass

import typer
from rich.console import Console
from rich.table import Table

from guitar.fretboard import render_fretboard
from guitar.theory import CHROMATIC, SCALES, scale_notes

app = typer.Typer(help="Scale trainer")
console = Console()


@dataclass
class ScaleQuestion:
    root: str
    scale: str
    notes: list[str]


def make_scale_question() -> ScaleQuestion:
    root = random.choice(CHROMATIC)
    scale = random.choice(list(SCALES.keys()))
    notes = scale_notes(root, scale)
    return ScaleQuestion(root=root, scale=scale, notes=notes)


def check_scale_answer(answer: str, q: ScaleQuestion) -> bool:
    return answer.strip().lower() == f"{q.root} {q.scale}".lower()


def render_scale_board(q: ScaleQuestion, fret_min: int = 0, fret_max: int = 12) -> str:
    """Return header + fretboard string for a scale — no IO."""
    notes_set = set(q.notes)
    root_set = {q.notes[0]}
    header = f"\n[bold]{q.root} {q.scale}[/bold]  —  {' '.join(q.notes)}"
    legend = "[bold red]■[/bold red] root   [green]■[/green] scale tone"
    board = render_fretboard(
        marked=notes_set, roots=root_set, fret_min=fret_min, fret_max=fret_max
    )
    return f"{header}\n{legend}\n\n{board}"


@app.command("list")
def list_scales() -> None:
    """List all available scales."""
    table = Table(title="Available Scales", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Intervals")
    table.add_column("Notes from C")
    for name, intervals in SCALES.items():
        notes = scale_notes('C', name)
        table.add_row(name, str(intervals), '  '.join(notes))
    console.print(table)


@app.command("show")
def show_scale(
    key: str = typer.Argument(help="Root note (e.g. C, F#, Bb)"),
    scale: str = typer.Argument(help="Scale name (e.g. major, blues)"),
    fret_min: int = typer.Option(0, "--min", help="Starting fret"),
    fret_max: int = typer.Option(12, "--max", help="Ending fret"),
) -> None:
    """Display a scale across the fretboard."""
    if scale not in SCALES:
        msg = (
            f"[red]Unknown scale '{scale}'. "
            "Run 'guitar scales list' to see options.[/red]"
        )
        console.print(msg)
        raise typer.Exit(1)
    q = ScaleQuestion(root=key, scale=scale, notes=scale_notes(key, scale))
    console.print(render_scale_board(q, fret_min, fret_max))


@app.command("quiz")
def quiz_scale(
    rounds: int = typer.Option(5, "--rounds", "-r", help="Number of rounds"),
) -> None:
    """Identify a displayed scale by ear/sight."""
    score = 0
    for i in range(rounds):
        q = make_scale_question()
        console.print(f"\n[bold]Round {i + 1}/{rounds}[/bold]")
        console.print(render_scale_board(q))
        console.print(f"Notes shown: [cyan]{' '.join(q.notes)}[/cyan]")
        answer = typer.prompt("Name the scale (e.g. 'C major')")
        if check_scale_answer(answer, q):
            console.print("[green]Correct![/green]")
            score += 1
        else:
            console.print(
                f"[red]Wrong.[/red] It was [bold]{q.root} {q.scale}[/bold]"
            )
    console.print(f"\n[bold]Score: {score}/{rounds}[/bold]")
