# guitar-practice-app

![Coverage](coverage.svg)

A CLI app to help practice the guitar — scales, chords, ear training, technique exercises, and timed practice sessions.

## Installation

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv venv
make build    # installs the guitar CLI into the venv
make install  # installs dev dependencies (pytest, ruff)
```

Activate the venv to use the `guitar` command directly:

```bash
source .venv/bin/activate
```

Or prefix with `uv run`:

```bash
uv run guitar --help
```

## Usage

### Scales

```bash
guitar scales list                  # list all available scales
guitar scales show C major          # display C major on the fretboard
guitar scales show A blues --min 5  # blues scale starting at fret 5
guitar scales quiz                  # identify scales by sight
```

### Chords

```bash
guitar chords list                  # list all chord qualities
guitar chords show Cmajor           # display chord diagram and tones
guitar chords quiz                  # identify chord quality from tones
```

### Practice Timer

```bash
guitar timer start                  # 20-minute session (default)
guitar timer start --minutes 10     # custom duration
guitar timer history                # view recent sessions
guitar timer streak                 # view current daily streak
```

### Ear Training

```bash
guitar ear intervals                # identify intervals between two notes
guitar ear chords                   # identify chord quality from tones
```

### Exercises

```bash
guitar exercises spider             # step through the 1-2-3-4 spider walk
guitar exercises spider --variant 2 # alternate finger pattern
guitar exercises notes              # note identification quiz
guitar exercises notes --string 1   # focus on the low E string
```

### Practice Routines

```bash
guitar routine list                       # list built-in and custom routines
guitar routine show beginner_warmup       # preview routine steps
guitar routine run beginner_warmup        # run a full routine with timers
```

Custom routines can be defined in `~/.guitar-practice/routines.toml`:

```toml
[routines.my_routine]
name = "My Routine"
description = "Daily warmup"
steps = [
  { activity = "spider", variant = 1, start_fret = 5, bpm = 60, minutes = 5 },
  { activity = "scales", key = "G", scale = "pentatonic_minor", minutes = 10 },
]
```

## Development

```bash
make fmt     # format with ruff
make lint    # lint with ruff
make test    # run tests with coverage
make ci      # lint + test
```
