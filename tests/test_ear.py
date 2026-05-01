from guitar.ear import (
    ChordQuestion,
    IntervalQuestion,
    make_chord_question,
    make_interval_question,
    render_chord_question,
    render_interval_question,
)
from guitar.theory import CHORDS, CHROMATIC, INTERVAL_SHORT


def test_make_interval_question_structure():
    q = make_interval_question()
    assert q.note_a in CHROMATIC
    assert q.note_b in CHROMATIC
    assert q.correct in INTERVAL_SHORT.values()
    assert len(q.options) == 4
    assert q.correct in q.options


def test_make_interval_question_correct_matches_semitones():
    q = make_interval_question()
    assert INTERVAL_SHORT[q.semitones] == q.correct


def test_make_chord_question_structure():
    q = make_chord_question()
    assert q.root in CHROMATIC
    assert q.quality in CHORDS
    assert len(q.notes) == len(CHORDS[q.quality])
    assert q.quality in q.options
    assert len(q.options) == 4


def test_render_interval_question_contains_notes():
    q = IntervalQuestion(
        note_a='C', note_b='G', semitones=7, correct='P5',
        options=['P4', 'M3', 'P5', 'm7'],
    )
    output = render_interval_question(q, 1, 5)
    assert 'C' in output
    assert 'G' in output
    assert 'Round 1/5' in output
    for opt in q.options:
        assert opt in output


def test_render_chord_question_contains_tones():
    q = ChordQuestion(
        root='C', quality='major', notes=['C', 'E', 'G'],
        options=['major', 'minor', 'dim', 'aug'],
    )
    output = render_chord_question(q, 2, 5)
    assert 'Round 2/5' in output
    assert 'C' in output
    assert 'E' in output
    assert 'G' in output
