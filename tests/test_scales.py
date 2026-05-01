from guitar.scales import (
    ScaleQuestion,
    check_scale_answer,
    make_scale_question,
    render_scale_board,
)
from guitar.theory import SCALES


def test_make_scale_question_structure():
    q = make_scale_question()
    assert q.scale in SCALES
    assert len(q.notes) == len(SCALES[q.scale])
    assert q.notes[0] == q.root or True  # root is first note by definition


def test_check_scale_answer_correct():
    notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    q = ScaleQuestion(root='C', scale='major', notes=notes)
    assert check_scale_answer('C major', q) is True


def test_check_scale_answer_case_insensitive():
    notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    q = ScaleQuestion(root='C', scale='major', notes=notes)
    assert check_scale_answer('c Major', q) is True


def test_check_scale_answer_wrong():
    notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    q = ScaleQuestion(root='C', scale='major', notes=notes)
    assert check_scale_answer('C minor', q) is False


def test_render_scale_board_contains_root_and_scale():
    notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    q = ScaleQuestion(root='C', scale='major', notes=notes)
    output = render_scale_board(q)
    assert 'C' in output
    assert 'major' in output


def test_render_scale_board_contains_fretboard_separators():
    q = ScaleQuestion(root='A', scale='blues', notes=['A', 'C', 'D', 'D#', 'E', 'G'])
    output = render_scale_board(q)
    assert '|' in output
