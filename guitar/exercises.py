import random
from dataclasses import dataclass, field

import typer
from rich.console import Console

from guitar.fretboard import render_fretboard
from guitar.quiz import resolve_answer, score_summary
from guitar.renderer import Renderer, RichRenderer
from guitar.theory import CHROMATIC, STANDARD_TUNING, note_at

app = typer.Typer(help="Technique exercises")
console = Console()

SPIDER_PATTERNS: dict[int, list[int]] = {
    1: [1, 2, 3, 4],
    2: [1, 3, 2, 4],
    3: [1, 4, 2, 3],
    4: [2, 1, 3, 4],
    5: [4, 3, 2, 1],  # reverse
}

STRING_NAMES = ['Low E', 'A', 'D', 'G', 'B', 'High e']


@dataclass
class SpiderStep:
    string_idx: int
    string_name: str
    finger_num: int
    fret: int
    note: str


@dataclass
class NoteQuestion:
    string_idx: int
    string_name: str
    fret: int
    correct: str
    options: list[str] = field(default_factory=list)


def spider_walk_steps(variant: int, start_fret: int) -> list[SpiderStep]:
    """Return every step in a spider walk pattern as pure data."""
    pattern = SPIDER_PATTERNS[variant]
    steps = []
    for string_idx, open_note in enumerate(STANDARD_TUNING):
        for finger_num in pattern:
            fret = start_fret + finger_num - 1
            note = note_at(open_note, fret)
            steps.append(SpiderStep(
                string_idx=string_idx,
                string_name=STRING_NAMES[string_idx],
                finger_num=finger_num,
                fret=fret,
                note=note,
            ))
    return steps


def render_spider_step(step: SpiderStep, start_fret: int) -> str:
    """Return the header line + fretboard string for one spider step."""
    header = (
        f"[bold]{step.string_name}[/bold]  |  "
        f"Fret [cyan]{step.fret}[/cyan]  |  "
        f"Finger [cyan]{step.finger_num}[/cyan]  |  "
        f"Note [bold red]{step.note}[/bold red]"
    )
    board = render_fretboard(
        marked={step.note},
        roots={step.note},
        fret_min=start_fret,
        fret_max=start_fret + 4,
    )
    return f"{header}\n{board}"


def make_note_question(string_indices: list[int], fret_max: int) -> NoteQuestion:
    """Generate one note-identification question."""
    s = random.choice(string_indices)
    fret = random.randint(0, fret_max)
    correct = note_at(STANDARD_TUNING[s], fret)
    distractors = random.sample([n for n in CHROMATIC if n != correct], 3)
    options = distractors + [correct]
    random.shuffle(options)
    return NoteQuestion(
        string_idx=s,
        string_name=STRING_NAMES[s],
        fret=fret,
        correct=correct,
        options=options,
    )


def render_note_question(q: NoteQuestion, round_num: int, total: int) -> str:
    lines = [
        f"\n[bold]Round {round_num}/{total}[/bold]",
        f"  String: [cyan]{q.string_name}[/cyan]   Fret: [cyan]{q.fret}[/cyan]",
    ]
    lines += [f"  {i}. {opt}" for i, opt in enumerate(q.options, 1)]
    return "\n".join(lines)


def run_spider_walk(
    variant: int, start_fret: int, bpm: int, renderer: Renderer
) -> None:
    pattern = SPIDER_PATTERNS[variant]
    renderer.print(f"\n[bold]Spider Walk — Variant {variant}[/bold]")
    renderer.print(
        f"Finger order: [cyan]{' → '.join(str(f) for f in pattern)}[/cyan]"
    )
    renderer.print(
        f"Start fret: [cyan]{start_fret}[/cyan]   BPM: [cyan]{bpm}[/cyan]"
    )
    renderer.print(
        "\nPress [bold]Enter[/bold] to advance, [bold]Ctrl-C[/bold] to stop.\n"
    )
    for step in spider_walk_steps(variant, start_fret):
        renderer.print(render_spider_step(step, start_fret))
        renderer.prompt("")
    renderer.print("[bold green]Pattern complete![/bold green]")


def run_note_identification(
    rounds: int, string_indices: list[int], fret_max: int, renderer: Renderer
) -> int:
    score = 0
    for i in range(rounds):
        q = make_note_question(string_indices, fret_max)
        renderer.print(render_note_question(q, i + 1, rounds))
        raw = renderer.prompt("Note")
        answer = resolve_answer(raw, q.options)
        if answer == q.correct:
            renderer.print("[green]Correct![/green]")
            score += 1
        else:
            renderer.print(f"[red]Wrong.[/red] It was [bold]{q.correct}[/bold]")
    renderer.print(f"\n[bold]Score: {score_summary(score, rounds)}[/bold]")
    return score


@app.command("spider")
def spider_walk(  # pragma: no cover
    variant: int = typer.Option(1, "--variant", "-v", help="Pattern variant 1-5"),
    start_fret: int = typer.Option(5, "--fret", "-f", help="Starting fret"),
    bpm: int = typer.Option(60, "--bpm", help="Target BPM for the exercise"),
) -> None:
    """
    Step through a spider walk exercise.

    Press Enter to advance to the next position, Ctrl-C to quit.
    """
    if variant not in SPIDER_PATTERNS:
        console.print("[red]Variant must be 1-5.[/red]")
        raise typer.Exit(1)
    try:
        run_spider_walk(variant, start_fret, bpm, RichRenderer())
    except KeyboardInterrupt:
        console.print("\n[yellow]Exercise stopped.[/yellow]")


@app.command("notes")
def note_identification(  # pragma: no cover
    rounds: int = typer.Option(15, "--rounds", "-r", help="Number of questions"),
    string_num: int = typer.Option(
        0, "--string", "-s", help="String to focus on (0 = all, 1=low E … 6=high e)"
    ),
    fret_max: int = typer.Option(12, "--fret-max", help="Maximum fret to quiz"),
) -> None:
    """Quiz: name the note at a given string and fret."""
    string_indices = list(range(len(STANDARD_TUNING)))
    if string_num != 0:
        string_indices = [string_num - 1]
    run_note_identification(rounds, string_indices, fret_max, RichRenderer())
