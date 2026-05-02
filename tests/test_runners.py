import pytest

from guitar.chords import run_chord_quiz
from guitar.ear import (
    ChordQuestion,
    IntervalQuestion,
    run_interval_quiz,
)
from guitar.ear import (
    run_chord_quiz as run_ear_chord_quiz,
)
from guitar.exercises import NoteQuestion, run_note_identification, run_spider_walk
from guitar.scales import ScaleQuestion, run_scale_quiz
from tests.conftest import FakeRenderer

# --- ear: interval quiz ---

def test_run_interval_quiz_correct(monkeypatch: pytest.MonkeyPatch) -> None:
    q = IntervalQuestion(
        note_a='C', note_b='G', semitones=7, correct='P5',
        options=['m3', 'P4', 'M6', 'P5'],
    )
    monkeypatch.setattr('guitar.ear.make_interval_question', lambda: q)
    renderer = FakeRenderer(responses=['P5'] * 3)
    assert run_interval_quiz(3, renderer) == 3


def test_run_interval_quiz_wrong(monkeypatch: pytest.MonkeyPatch) -> None:
    q = IntervalQuestion(
        note_a='C', note_b='G', semitones=7, correct='P5',
        options=['m3', 'P4', 'M6', 'P5'],
    )
    monkeypatch.setattr('guitar.ear.make_interval_question', lambda: q)
    renderer = FakeRenderer(responses=['wrong'] * 3)
    assert run_interval_quiz(3, renderer) == 0


def test_run_interval_quiz_prints_result(monkeypatch: pytest.MonkeyPatch) -> None:
    q = IntervalQuestion(
        note_a='C', note_b='G', semitones=7, correct='P5',
        options=['m3', 'P4', 'M6', 'P5'],
    )
    monkeypatch.setattr('guitar.ear.make_interval_question', lambda: q)
    renderer = FakeRenderer(responses=['P5'])
    run_interval_quiz(1, renderer)
    assert any('Correct' in msg for msg in renderer.printed)


# --- ear: chord quiz ---

def test_run_ear_chord_quiz_correct(monkeypatch: pytest.MonkeyPatch) -> None:
    q = ChordQuestion(
        root='C', quality='major', notes=['C', 'E', 'G'],
        options=['minor', 'dom7', 'dim', 'major'],
    )
    monkeypatch.setattr('guitar.ear.make_chord_question', lambda: q)
    renderer = FakeRenderer(responses=['major'] * 2)
    assert run_ear_chord_quiz(2, renderer) == 2


def test_run_ear_chord_quiz_wrong(monkeypatch: pytest.MonkeyPatch) -> None:
    q = ChordQuestion(
        root='C', quality='major', notes=['C', 'E', 'G'],
        options=['minor', 'dom7', 'dim', 'major'],
    )
    monkeypatch.setattr('guitar.ear.make_chord_question', lambda: q)
    renderer = FakeRenderer(responses=['minor'] * 2)
    assert run_ear_chord_quiz(2, renderer) == 0


# --- chords: chord quiz ---

def test_run_chord_quiz_correct(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('guitar.chords.random.choice', lambda seq: (
        'C' if 'C' in seq else 'major'
    ))
    renderer = FakeRenderer(responses=['major'] * 2)
    assert run_chord_quiz(2, renderer) == 2


def test_run_chord_quiz_wrong(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('guitar.chords.random.choice', lambda seq: (
        'C' if 'C' in seq else 'major'
    ))
    renderer = FakeRenderer(responses=['minor'] * 2)
    assert run_chord_quiz(2, renderer) == 0


# --- scales: scale quiz ---

C_MAJOR = ScaleQuestion(
    root='C', scale='major', notes=['C', 'D', 'E', 'F', 'G', 'A', 'B']
)


def test_run_scale_quiz_correct(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('guitar.scales.make_scale_question', lambda: C_MAJOR)
    renderer = FakeRenderer(responses=['C major'] * 2)
    assert run_scale_quiz(2, renderer) == 2


def test_run_scale_quiz_wrong(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('guitar.scales.make_scale_question', lambda: C_MAJOR)
    renderer = FakeRenderer(responses=['A minor'] * 2)
    assert run_scale_quiz(2, renderer) == 0


def test_run_scale_quiz_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('guitar.scales.make_scale_question', lambda: C_MAJOR)
    renderer = FakeRenderer(responses=['c MAJOR'])
    assert run_scale_quiz(1, renderer) == 1


# --- exercises: note identification ---

def test_run_note_identification_correct(monkeypatch: pytest.MonkeyPatch) -> None:
    q = NoteQuestion(
        string_idx=0, string_name='Low E', fret=0, correct='E',
        options=['A', 'D', 'G', 'E'],
    )
    monkeypatch.setattr('guitar.exercises.make_note_question', lambda si, fm: q)
    renderer = FakeRenderer(responses=['E'] * 3)
    assert run_note_identification(3, [0], 12, renderer) == 3


def test_run_note_identification_wrong(monkeypatch: pytest.MonkeyPatch) -> None:
    q = NoteQuestion(
        string_idx=0, string_name='Low E', fret=0, correct='E',
        options=['A', 'D', 'G', 'E'],
    )
    monkeypatch.setattr('guitar.exercises.make_note_question', lambda si, fm: q)
    renderer = FakeRenderer(responses=['A'] * 3)
    assert run_note_identification(3, [0], 12, renderer) == 0


# --- exercises: spider walk ---

def test_run_spider_walk_prints_all_steps() -> None:
    renderer = FakeRenderer()
    run_spider_walk(variant=1, start_fret=5, bpm=60, renderer=renderer)
    # 6 strings × 4 fingers = 24 steps; each step print contains 'Fret'
    step_prints = [m for m in renderer.printed if 'Fret' in m]
    assert len(step_prints) == 24


def test_run_spider_walk_prints_completion() -> None:
    renderer = FakeRenderer()
    run_spider_walk(variant=1, start_fret=5, bpm=60, renderer=renderer)
    assert any('complete' in m.lower() for m in renderer.printed)
