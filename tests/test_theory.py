
from guitar.theory import (
    chord_notes,
    fretboard_positions,
    interval_semitones,
    normalize_note,
    note_at,
    scale_notes,
)


def test_note_at_open():
    assert note_at('E', 0) == 'E'


def test_note_at_fret():
    assert note_at('E', 1) == 'F'
    assert note_at('E', 12) == 'E'
    assert note_at('A', 5) == 'D'


def test_note_at_wraps():
    assert note_at('B', 1) == 'C'


def test_normalize_flat():
    assert normalize_note('Bb') == 'A#'
    assert normalize_note('Eb') == 'D#'
    assert normalize_note('C') == 'C'


def test_scale_notes_c_major():
    assert scale_notes('C', 'major') == ['C', 'D', 'E', 'F', 'G', 'A', 'B']


def test_scale_notes_a_minor():
    assert scale_notes('A', 'minor') == ['A', 'B', 'C', 'D', 'E', 'F', 'G']


def test_scale_notes_a_blues():
    assert scale_notes('A', 'blues') == ['A', 'C', 'D', 'D#', 'E', 'G']


def test_chord_notes_c_major():
    assert chord_notes('C', 'major') == ['C', 'E', 'G']


def test_chord_notes_a_minor():
    assert chord_notes('A', 'minor') == ['A', 'C', 'E']


def test_chord_notes_g_dom7():
    assert chord_notes('G', 'dom7') == ['G', 'B', 'D', 'F']


def test_interval_semitones_unison():
    assert interval_semitones('C', 'C') == 0


def test_interval_semitones_fifth():
    assert interval_semitones('C', 'G') == 7


def test_interval_semitones_wraps():
    assert interval_semitones('B', 'C') == 1


def test_fretboard_positions_returns_pairs():
    positions = fretboard_positions({'C', 'E', 'G'}, fret_range=(0, 5))
    assert all(isinstance(s, int) and isinstance(f, int) for s, f in positions)
    assert len(positions) > 0


def test_fretboard_positions_e_string_open():
    # Low E string (index 0), fret 0 = E
    positions = fretboard_positions({'E'}, fret_range=(0, 0))
    assert (0, 0) in positions
    assert (5, 0) in positions  # high e string also open E
