from guitar.exercises import (
    SPIDER_PATTERNS,
    STRING_NAMES,
    SpiderStep,
    make_note_question,
    render_note_question,
    render_spider_step,
    spider_walk_steps,
)
from guitar.theory import CHROMATIC, STANDARD_TUNING, note_at


def test_spider_patterns_exist():
    assert 1 in SPIDER_PATTERNS
    assert 5 in SPIDER_PATTERNS


def test_spider_pattern_1_correct():
    assert SPIDER_PATTERNS[1] == [1, 2, 3, 4]


def test_spider_pattern_5_reverse():
    assert SPIDER_PATTERNS[5] == [4, 3, 2, 1]


def test_string_names_length():
    assert len(STRING_NAMES) == len(STANDARD_TUNING)


def test_note_at_each_string_open():
    expected_open = ['E', 'A', 'D', 'G', 'B', 'E']
    for i, open_note in enumerate(STANDARD_TUNING):
        assert note_at(open_note, 0) == expected_open[i]


def test_note_at_12th_fret_octave():
    for open_note in STANDARD_TUNING:
        assert note_at(open_note, 12) == open_note


def test_spider_walk_steps_count():
    steps = spider_walk_steps(1, start_fret=5)
    # 6 strings × 4 fingers
    assert len(steps) == 6 * 4


def test_spider_walk_steps_are_spider_steps():
    steps = spider_walk_steps(1, start_fret=5)
    assert all(isinstance(s, SpiderStep) for s in steps)


def test_spider_walk_steps_frets_correct():
    steps = spider_walk_steps(1, start_fret=5)
    # pattern [1,2,3,4] → frets 5,6,7,8 for each string
    first_string_frets = [s.fret for s in steps[:4]]
    assert first_string_frets == [5, 6, 7, 8]


def test_spider_walk_steps_notes_match_theory():
    steps = spider_walk_steps(1, start_fret=1)
    for step in steps:
        expected = note_at(STANDARD_TUNING[step.string_idx], step.fret)
        assert step.note == expected


def test_render_spider_step_contains_string_and_fret():
    step = SpiderStep(string_idx=0, string_name='Low E', finger_num=1, fret=5, note='A')
    output = render_spider_step(step, start_fret=5)
    assert 'Low E' in output
    assert '5' in output
    assert 'A' in output


def test_make_note_question_structure():
    q = make_note_question(list(range(6)), fret_max=12)
    assert q.correct in CHROMATIC
    assert len(q.options) == 4
    assert q.correct in q.options
    assert 0 <= q.fret <= 12


def test_make_note_question_fret_respects_max():
    for _ in range(20):
        q = make_note_question(list(range(6)), fret_max=5)
        assert q.fret <= 5


def test_make_note_question_string_filter():
    # Only string 0 (low E)
    for _ in range(10):
        q = make_note_question([0], fret_max=12)
        assert q.string_idx == 0


def test_render_note_question_contains_string_and_fret():
    from guitar.exercises import NoteQuestion
    q = NoteQuestion(
        string_idx=0, string_name='Low E', fret=5,
        correct='A', options=['A', 'B', 'C', 'D'],
    )
    output = render_note_question(q, 1, 10)
    assert 'Low E' in output
    assert '5' in output
    assert 'Round 1/10' in output
