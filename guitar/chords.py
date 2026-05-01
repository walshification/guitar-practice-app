import random

import typer
from rich.console import Console
from rich.table import Table

from guitar.fretboard import render_chord_box
from guitar.theory import CHORDS, CHROMATIC, chord_notes

app = typer.Typer(help="Chord library")
console = Console()

# Hardcoded open-position fingerings (None = muted, 0 = open)
OPEN_FINGERINGS: dict[str, list[int | None]] = {
    'Cmajor': [None, 3, 2, 0, 1, 0],
    'Gmajor': [3, 2, 0, 0, 0, 3],
    'Dmajor': [None, None, 0, 2, 3, 2],
    'Amajor': [None, 0, 2, 2, 2, 0],
    'Emajor': [0, 2, 2, 1, 0, 0],
    'Aminor': [None, 0, 2, 2, 1, 0],
    'Eminor': [0, 2, 2, 0, 0, 0],
    'Dminor': [None, None, 0, 2, 3, 1],
    'Fmajor': [1, 1, 2, 3, 3, 1],
    'Bminor': [None, 2, 4, 4, 3, 2],
}


def parse_chord(chord: str) -> tuple[str, str | None]:
    """Split 'Cmajor' → ('C', 'major'), 'F#min7' → ('F#', 'min7')."""
    for quality in sorted(CHORDS.keys(), key=len, reverse=True):
        if chord.lower().endswith(quality.lower()):
            root = chord[: len(chord) - len(quality)]
            return root, quality
    for length in (2, 1):
        root = chord[:length]
        quality = chord[length:].lower()
        if quality in CHORDS:
            return root, quality
    return chord, None


def open_fingering(root: str, quality: str) -> list[int | None] | None:
    return OPEN_FINGERINGS.get(f"{root}{quality}")


def render_chord_display(root: str, quality: str) -> str:
    """Return a full chord display string — notes header + diagram — no IO."""
    notes = chord_notes(root, quality)
    header = f"\n[bold]{root} {quality}[/bold]  —  {' '.join(notes)}\n"
    fingering = open_fingering(root, quality)
    if fingering:
        box = render_chord_box(fingering, start_fret=1, num_frets=4)
        body = f"{box}\n\n[dim]Low E → high e (left → right)[/dim]"
    else:
        body = "[dim]No preset fingering — showing chord tones only.[/dim]"
    return f"{header}{body}\n\nChord tones: {' '.join(notes)}"


@app.command("list")
def list_chords() -> None:
    """List all available chord qualities."""
    table = Table(title="Available Chord Qualities", show_header=True)
    table.add_column("Quality", style="cyan")
    table.add_column("Intervals")
    table.add_column("Tones from C")
    for quality, intervals in CHORDS.items():
        tones = chord_notes('C', quality)
        table.add_row(quality, str(intervals), '  '.join(tones))
    console.print(table)


@app.command("show")
def show_chord(
    chord: str = typer.Argument(help="Chord as <key><quality>, e.g. Cmajor, F#min7"),
) -> None:
    """Display a chord's notes and a basic diagram."""
    root, quality = parse_chord(chord)
    if quality is None:
        console.print(
            f"[red]Could not parse '{chord}'. Try e.g. Cmajor, Amin7, F#dom7[/red]"
        )
        raise typer.Exit(1)
    console.print(render_chord_display(root, quality))


@app.command("quiz")
def quiz_chord(
    rounds: int = typer.Option(5, "--rounds", "-r", help="Number of rounds"),
) -> None:
    """Identify chord quality from its tones."""
    score = 0
    qualities = list(CHORDS.keys())
    for i in range(rounds):
        root = random.choice(CHROMATIC)
        quality = random.choice(qualities)
        notes = chord_notes(root, quality)
        tones_str = ' '.join(notes)
        console.print(f"\n[bold]Round {i + 1}/{rounds}[/bold]")
        console.print(
            f"Tones: [cyan]{tones_str}[/cyan]  root: [bold red]{root}[/bold red]"
        )
        answer = typer.prompt("Quality (e.g. major, min7, dim)")
        if answer.strip().lower() == quality.lower():
            console.print("[green]Correct![/green]")
            score += 1
        else:
            console.print(f"[red]Wrong.[/red] It was [bold]{quality}[/bold]")
    console.print(f"\n[bold]Score: {score}/{rounds}[/bold]")
