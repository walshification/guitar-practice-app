import random
from dataclasses import dataclass, field

import typer
from rich.console import Console

from guitar.quiz import resolve_answer, score_summary
from guitar.renderer import Renderer, RichRenderer
from guitar.theory import (
    CHORDS,
    CHROMATIC,
    INTERVAL_SHORT,
    chord_notes,
    interval_semitones,
)

app = typer.Typer(help="Ear training quizzes (text-based)")
console = Console()


@dataclass
class IntervalQuestion:
    note_a: str
    note_b: str
    semitones: int
    correct: str
    options: list[str] = field(default_factory=list)


@dataclass
class ChordQuestion:
    root: str
    quality: str
    notes: list[str]
    options: list[str] = field(default_factory=list)


def make_interval_question() -> IntervalQuestion:
    all_intervals = list(INTERVAL_SHORT.values())
    note_a = random.choice(CHROMATIC)
    note_b = random.choice(CHROMATIC)
    semitones = interval_semitones(note_a, note_b)
    correct = INTERVAL_SHORT[semitones]
    distractors = random.sample([v for v in all_intervals if v != correct], 3)
    options = distractors + [correct]
    random.shuffle(options)
    return IntervalQuestion(
        note_a=note_a,
        note_b=note_b,
        semitones=semitones,
        correct=correct,
        options=options,
    )


def make_chord_question() -> ChordQuestion:
    qualities = list(CHORDS.keys())
    root = random.choice(CHROMATIC)
    quality = random.choice(qualities)
    notes = chord_notes(root, quality)
    distractors = random.sample(
        [q for q in qualities if q != quality], min(3, len(qualities) - 1)
    )
    options = distractors + [quality]
    random.shuffle(options)
    return ChordQuestion(root=root, quality=quality, notes=notes, options=options)


def render_interval_question(q: IntervalQuestion, round_num: int, total: int) -> str:
    lines = [
        f"\n[bold]Round {round_num}/{total}[/bold]",
        f"  [cyan]{q.note_a}[/cyan]  →  [cyan]{q.note_b}[/cyan]",
    ]
    lines += [f"  {i}. {opt}" for i, opt in enumerate(q.options, 1)]
    return "\n".join(lines)


def render_chord_question(q: ChordQuestion, round_num: int, total: int) -> str:
    tones_str = " ".join(q.notes)
    lines = [
        f"\n[bold]Round {round_num}/{total}[/bold]",
        f"  Tones: [cyan]{tones_str}[/cyan]  root: [bold red]{q.root}[/bold red]",
    ]
    lines += [f"  {i}. {opt}" for i, opt in enumerate(q.options, 1)]
    return "\n".join(lines)


def run_interval_quiz(rounds: int, renderer: Renderer) -> int:
    score = 0
    for i in range(rounds):
        q = make_interval_question()
        renderer.print(render_interval_question(q, i + 1, rounds))
        raw = renderer.prompt("Answer (1-4 or interval name)")
        answer = resolve_answer(raw, q.options)
        if answer == q.correct:
            renderer.print("[green]Correct![/green]")
            score += 1
        else:
            renderer.print(
                f"[red]Wrong.[/red] It was [bold]{q.correct}[/bold]"
                f" ({q.semitones}st)"
            )
    renderer.print(f"\n[bold]Score: {score_summary(score, rounds)}[/bold]")
    return score


def run_chord_quiz(rounds: int, renderer: Renderer) -> int:
    score = 0
    for i in range(rounds):
        q = make_chord_question()
        renderer.print(render_chord_question(q, i + 1, rounds))
        raw = renderer.prompt("Answer (1-4 or quality name)")
        answer = resolve_answer(raw, q.options)
        if answer == q.quality:
            renderer.print("[green]Correct![/green]")
            score += 1
        else:
            renderer.print(f"[red]Wrong.[/red] It was [bold]{q.quality}[/bold]")
    renderer.print(f"\n[bold]Score: {score_summary(score, rounds)}[/bold]")
    return score


@app.command("intervals")
def quiz_intervals(  # pragma: no cover
    rounds: int = typer.Option(10, "--rounds", "-r", help="Number of rounds"),
) -> None:
    """Identify the interval between two notes."""
    run_interval_quiz(rounds, RichRenderer())


@app.command("chords")
def quiz_chords(  # pragma: no cover
    rounds: int = typer.Option(10, "--rounds", "-r", help="Number of rounds"),
) -> None:
    """Identify chord quality from its tones."""
    run_chord_quiz(rounds, RichRenderer())
