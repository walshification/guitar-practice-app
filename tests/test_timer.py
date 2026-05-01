from guitar.timer import format_duration, progress_bar


def test_format_duration_whole_minutes():
    assert format_duration(300) == '5m 0s'


def test_format_duration_with_seconds():
    assert format_duration(183) == '3m 3s'


def test_format_duration_zero():
    assert format_duration(0) == '0m 0s'


def test_format_duration_under_a_minute():
    assert format_duration(45) == '0m 45s'


def test_progress_bar_empty():
    bar = progress_bar(0, 100, width=10)
    assert bar == '░░░░░░░░░░'


def test_progress_bar_full():
    bar = progress_bar(100, 100, width=10)
    assert bar == '██████████'


def test_progress_bar_half():
    bar = progress_bar(50, 100, width=10)
    assert bar == '█████░░░░░'


def test_progress_bar_length():
    bar = progress_bar(30, 100, width=20)
    assert len(bar) == 20
