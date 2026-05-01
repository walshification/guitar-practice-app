from guitar.quiz import resolve_answer, score_summary


def test_resolve_answer_by_number():
    options = ['P4', 'M3', 'P5', 'm7']
    assert resolve_answer('3', options) == 'P5'


def test_resolve_answer_by_text():
    options = ['P4', 'M3', 'P5', 'm7']
    assert resolve_answer('P4', options) == 'P4'


def test_resolve_answer_out_of_range_returns_raw():
    options = ['P4', 'M3']
    assert resolve_answer('9', options) == '9'


def test_resolve_answer_strips_whitespace():
    options = ['major', 'minor']
    assert resolve_answer('  major  ', options) == 'major'


def test_score_summary_perfect():
    assert score_summary(5, 5) == '5/5 (100%)'


def test_score_summary_zero():
    assert score_summary(0, 10) == '0/10 (0%)'


def test_score_summary_partial():
    assert score_summary(3, 4) == '3/4 (75%)'
