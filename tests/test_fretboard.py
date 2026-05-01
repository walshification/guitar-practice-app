from guitar.fretboard import render_chord_box, render_fretboard


def test_fretboard_has_pipe_separators():
    board = render_fretboard(fret_min=0, fret_max=3)
    assert '|' in board


def test_fretboard_shows_all_strings():
    board = render_fretboard(fret_min=0, fret_max=3)
    lines = board.strip().split('\n')
    # 6 string lines + 1 ruler = 7
    assert len(lines) == 7


def test_fretboard_marks_root_differently():
    # Root note uses ANSI bold red; scale tone uses green
    board = render_fretboard(
        marked={'C', 'E', 'G'}, roots={'C'}, fret_min=0, fret_max=5
    )
    # ANSI red code for root
    assert '\033[1;31m' in board
    # ANSI green for scale tones
    assert '\033[32m' in board


def test_chord_box_structure():
    fingering = [None, 3, 2, 0, 1, 0]  # C major
    box = render_chord_box(fingering, start_fret=1, num_frets=4)
    assert '●' in box or '○' in box
    assert '|' in box


def test_chord_box_muted_strings():
    fingering = [None, None, 0, 2, 3, 2]  # D major
    box = render_chord_box(fingering, start_fret=1)
    lines = box.split('\n')
    assert 'X' in lines[0]
