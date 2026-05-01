from guitar.chords import (
    OPEN_FINGERINGS,
    open_fingering,
    parse_chord,
    render_chord_display,
)


def test_parse_chord_simple():
    assert parse_chord('Cmajor') == ('C', 'major')


def test_parse_chord_sharp():
    assert parse_chord('F#min7') == ('F#', 'min7')


def test_parse_chord_flat_style():
    root, quality = parse_chord('Bbminor')
    assert quality == 'minor'
    assert root == 'Bb'


def test_parse_chord_unknown_returns_none_quality():
    _, quality = parse_chord('Xunknown')
    assert quality is None


def test_open_fingering_known():
    fingering = open_fingering('C', 'major')
    assert fingering is not None
    assert fingering == OPEN_FINGERINGS['Cmajor']


def test_open_fingering_unknown_returns_none():
    assert open_fingering('C#', 'dim7') is None


def test_render_chord_display_contains_notes():
    output = render_chord_display('C', 'major')
    assert 'C' in output
    assert 'E' in output
    assert 'G' in output


def test_render_chord_display_with_fingering():
    output = render_chord_display('C', 'major')
    assert '|' in output  # chord box uses | separators


def test_render_chord_display_no_fingering():
    output = render_chord_display('C#', 'dim7')
    assert 'No preset fingering' in output
