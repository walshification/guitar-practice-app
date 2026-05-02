from pathlib import Path

import pytest

from guitar.routine import activity_dispatch, load_routines, resolve_step


def test_load_routines_returns_builtin():
    routines = load_routines()
    assert len(routines) > 0


def test_load_routines_builtin_have_steps():
    routines = load_routines()
    for name, r in routines.items():
        assert 'steps' in r, f"routine '{name}' has no steps"
        assert len(r['steps']) > 0


def test_load_routines_builtin_steps_have_activity():
    routines = load_routines()
    for name, r in routines.items():
        for step in r['steps']:
            assert 'activity' in step, f"step in '{name}' missing activity"


def test_load_routines_merges_user_file(tmp_path: Path):
    user_file = tmp_path / 'routines.toml'
    user_file.write_text(
        '[routines.custom]\nname = "Custom"\n'
        '[[routines.custom.steps]]\nactivity = "notes"\nminutes = 5\n'
    )
    routines = load_routines(user_path=user_file)
    assert 'custom' in routines
    assert routines['custom']['name'] == 'Custom'


def test_load_routines_user_overrides_builtin(tmp_path: Path):
    user_file = tmp_path / 'routines.toml'
    user_file.write_text(
        '[routines.beginner_warmup]\nname = "Overridden"\n'
        '[[routines.beginner_warmup.steps]]\nactivity = "notes"\nminutes = 1\n'
    )
    routines = load_routines(user_path=user_file)
    assert routines['beginner_warmup']['name'] == 'Overridden'


def test_load_routines_missing_user_file(tmp_path: Path):
    routines = load_routines(user_path=tmp_path / 'nonexistent.toml')
    assert len(routines) > 0  # built-ins still load


def test_activity_dispatch_contains_known_activities():
    dispatch = activity_dispatch()
    for activity in ('scales', 'spider', 'notes', 'ear_intervals', 'ear_chords'):
        assert activity in dispatch
        assert callable(dispatch[activity])


def test_resolve_step_known_activity():
    dispatch = activity_dispatch()
    step = {'activity': 'notes', 'minutes': 5}
    fn = resolve_step(step, dispatch)
    assert fn is dispatch['notes']


def test_resolve_step_unknown_falls_back_to_callable():
    dispatch = activity_dispatch()
    step = {'activity': 'free_play', 'minutes': 10}
    fn = resolve_step(step, dispatch)
    assert callable(fn)


def test_dispatch_scales_passes_key_and_scale(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr('guitar.scales.show_scale', lambda k, s: calls.append((k, s)))
    monkeypatch.setattr('guitar.timer.start_timer', lambda **kw: None)
    activity_dispatch()['scales']({'key': 'G', 'scale': 'blues', 'minutes': 3})
    assert calls == [('G', 'blues')]


def test_dispatch_scales_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr('guitar.scales.show_scale', lambda k, s: calls.append((k, s)))
    monkeypatch.setattr('guitar.timer.start_timer', lambda **kw: None)
    activity_dispatch()['scales']({})
    assert calls == [('C', 'major')]


def test_dispatch_spider_passes_step_params(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, int]] = []
    monkeypatch.setattr('guitar.exercises.spider_walk', lambda **kw: calls.append(kw))
    activity_dispatch()['spider']({'variant': 2, 'start_fret': 3, 'bpm': 80})
    assert calls == [{'variant': 2, 'start_fret': 3, 'bpm': 80}]


def test_dispatch_notes_maps_minutes_to_rounds(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, int]] = []
    monkeypatch.setattr(
        'guitar.exercises.note_identification', lambda **kw: calls.append(kw)
    )
    activity_dispatch()['notes']({'minutes': 2, 'string': 1, 'fret_max': 7})
    assert calls == [{'rounds': 6, 'string_num': 1, 'fret_max': 7}]


def test_dispatch_ear_intervals_maps_minutes_to_rounds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, int]] = []
    monkeypatch.setattr('guitar.ear.quiz_intervals', lambda **kw: calls.append(kw))
    activity_dispatch()['ear_intervals']({'minutes': 3})
    assert calls == [{'rounds': 6}]


def test_dispatch_ear_chords_maps_minutes_to_rounds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, int]] = []
    monkeypatch.setattr('guitar.ear.quiz_chords', lambda **kw: calls.append(kw))
    activity_dispatch()['ear_chords']({'minutes': 2})
    assert calls == [{'rounds': 4}]
