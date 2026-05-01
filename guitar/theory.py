CHROMATIC = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Low E to high E
STANDARD_TUNING = ['E', 'A', 'D', 'G', 'B', 'E']

SCALES: dict[str, list[int]] = {
    'major':           [0, 2, 4, 5, 7, 9, 11],
    'minor':           [0, 2, 3, 5, 7, 8, 10],
    'pentatonic_major': [0, 2, 4, 7, 9],
    'pentatonic_minor': [0, 3, 5, 7, 10],
    'blues':           [0, 3, 5, 6, 7, 10],
    'dorian':          [0, 2, 3, 5, 7, 9, 10],
    'mixolydian':      [0, 2, 4, 5, 7, 9, 10],
    'phrygian':        [0, 1, 3, 5, 7, 8, 10],
    'lydian':          [0, 2, 4, 6, 7, 9, 11],
    'locrian':         [0, 1, 3, 5, 6, 8, 10],
    'harmonic_minor':  [0, 2, 3, 5, 7, 8, 11],
    'melodic_minor':   [0, 2, 3, 5, 7, 9, 11],
}

INTERVALS: dict[int, str] = {
    0:  'P1 (Unison)',
    1:  'm2 (Minor 2nd)',
    2:  'M2 (Major 2nd)',
    3:  'm3 (Minor 3rd)',
    4:  'M3 (Major 3rd)',
    5:  'P4 (Perfect 4th)',
    6:  'TT (Tritone)',
    7:  'P5 (Perfect 5th)',
    8:  'm6 (Minor 6th)',
    9:  'M6 (Major 6th)',
    10: 'm7 (Minor 7th)',
    11: 'M7 (Major 7th)',
}

INTERVAL_SHORT: dict[int, str] = {
    0: 'P1', 1: 'm2', 2: 'M2', 3: 'm3', 4: 'M3', 5: 'P4',
    6: 'TT', 7: 'P5', 8: 'm6', 9: 'M6', 10: 'm7', 11: 'M7',
}

CHORDS: dict[str, list[int]] = {
    'major':  [0, 4, 7],
    'minor':  [0, 3, 7],
    'dom7':   [0, 4, 7, 10],
    'maj7':   [0, 4, 7, 11],
    'min7':   [0, 3, 7, 10],
    'dim':    [0, 3, 6],
    'dim7':   [0, 3, 6, 9],
    'aug':    [0, 4, 8],
    'sus2':   [0, 2, 7],
    'sus4':   [0, 5, 7],
    'add9':   [0, 4, 7, 14],
    '5':      [0, 7],
}


def normalize_note(note: str) -> str:
    """Convert flat notation to sharp equivalent."""
    flats = {
        'Db': 'C#', 'Eb': 'D#', 'Fb': 'E', 'Gb': 'F#',
        'Ab': 'G#', 'Bb': 'A#', 'Cb': 'B',
    }
    return flats.get(note, note)


def note_index(note: str) -> int:
    return CHROMATIC.index(normalize_note(note))


def note_at(open_note: str, fret: int) -> str:
    idx = (note_index(open_note) + fret) % 12
    return CHROMATIC[idx]


def scale_notes(root: str, scale: str) -> list[str]:
    root = normalize_note(root)
    root_idx = note_index(root)
    intervals = SCALES[scale]
    return [CHROMATIC[(root_idx + i) % 12] for i in intervals]


def chord_notes(root: str, quality: str) -> list[str]:
    root = normalize_note(root)
    root_idx = note_index(root)
    intervals = CHORDS[quality]
    return [CHROMATIC[(root_idx + i) % 12] for i in intervals]


def interval_semitones(note_a: str, note_b: str) -> int:
    return (note_index(note_b) - note_index(note_a)) % 12


def fretboard_positions(
    target_notes: set[str],
    tuning: list[str] = STANDARD_TUNING,
    fret_range: tuple[int, int] = (0, 12),
) -> list[tuple[int, int]]:
    """Return (string_index, fret) pairs where target notes appear."""
    positions = []
    for s, open_note in enumerate(tuning):
        for fret in range(fret_range[0], fret_range[1] + 1):
            if note_at(open_note, fret) in target_notes:
                positions.append((s, fret))
    return positions
