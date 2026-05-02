from rich.console import Console

from guitar.theory import STANDARD_TUNING, note_at

console = Console()

STRING_NAMES = ['e', 'B', 'G', 'D', 'A', 'E']  # high to low for display


def render_fretboard(
    marked: frozenset[str] | set[str] = frozenset(),
    roots: frozenset[str] | set[str] = frozenset(),
    fret_min: int = 0,
    fret_max: int = 12,
    tuning: list[str] = STANDARD_TUNING,
) -> str:
    """
    Return an ASCII fretboard string with | fret separators.

    marked  — notes to highlight in green
    roots   — subset of marked notes to highlight in bold red
    """
    lines = []
    frets = list(range(fret_min, fret_max + 1))

    # Display strings high-to-low (e string on top)
    display_order = list(reversed(range(len(tuning))))

    for s in display_order:
        open_note = tuning[s]
        string_label = STRING_NAMES[s]
        cells = []
        for fret in frets:
            note = note_at(open_note, fret)
            cell = note.ljust(2)
            if note in roots:
                cells.append(f'\033[1;31m{cell}\033[0m')
            elif note in marked:
                cells.append(f'\033[32m{cell}\033[0m')
            else:
                cells.append('──')
        lines.append(f'{string_label} |' + '|'.join(f'-{c}-' for c in cells) + '|')

    # Fret number ruler
    ruler_parts = []
    for fret in frets:
        ruler_parts.append(f' {str(fret).ljust(3)}')
    lines.append('   ' + ' '.join(ruler_parts))

    return '\n'.join(lines)


def render_chord_box(
    fingering: list[int | None],
    root_strings: frozenset[int] | set[int] = frozenset(),
    start_fret: int = 1,
    num_frets: int = 4,
) -> str:
    """
    Render a vertical chord box diagram.

    fingering — list of 6 fret numbers (None = muted), index 0 = low E
    root_strings — string indices where the root note is played
    start_fret — lowest fret shown in the box
    """
    num_strings = len(fingering)
    col_width = 3

    header = '  ' + ' '.join(
        ('X' if f is None else 'O' if f == 0 else ' ')
        for f in fingering
    )

    nut = '  ' + ('═' * (num_strings * col_width - 1)) if start_fret == 1 else ''

    rows = []
    for fret in range(start_fret, start_fret + num_frets):
        row = f'{fret} |'
        for s, played_fret in enumerate(fingering):
            if played_fret == fret:
                dot = '●' if s in root_strings else '○'
                row += f' {dot} |'
            else:
                row += '   |'
        rows.append(row)

    parts = [header]
    if nut:
        parts.append(nut)
    parts.extend(rows)
    return '\n'.join(parts)


def print_fretboard(  # pragma: no cover
    marked: frozenset[str] | set[str] = frozenset(),
    roots: frozenset[str] | set[str] = frozenset(),
    fret_min: int = 0,
    fret_max: int = 12,
    title: str = '',
) -> None:
    if title:
        console.print(f'\n[bold]{title}[/bold]')
    board = render_fretboard(
        marked=marked, roots=roots, fret_min=fret_min, fret_max=fret_max
    )
    console.print(board)
    console.print()
