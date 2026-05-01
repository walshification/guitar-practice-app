import typer

from guitar import chords, ear, exercises, routine, scales, timer

app = typer.Typer(
    name="guitar",
    help=(
        "Guitar practice CLI — scales, chords, timer,"
        " ear training, exercises, and routines."
    ),
    no_args_is_help=True,
)

app.add_typer(scales.app, name="scales")
app.add_typer(chords.app, name="chords")
app.add_typer(timer.app, name="timer")
app.add_typer(ear.app, name="ear")
app.add_typer(exercises.app, name="exercises")
app.add_typer(routine.app, name="routine")

if __name__ == "__main__":
    app()
