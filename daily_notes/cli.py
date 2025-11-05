from datetime import datetime
from pathlib import Path
import textwrap
from pydantic import BaseModel
import typer
from hns.cli import AudioRecorder, WhisperTranscriber
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from .config import Config

app = typer.Typer(no_args_is_help=True, help="Create a new note")

class Note(BaseModel):
    heading: str
    note_content: str
    todos: list[str]
    errors_and_problems: str

    def to_str(self) -> str:
        note: str = f"## {self.heading}\n"
        note += textwrap.indent(self.note_content, "  ")
        note += "\n"
        note += "\n".join([textwrap.indent(f"TODO {action}", "  ") for action in self.todos])
        note += "\n"
        return note

@app.command()
def note():
    config = Config()
    api_key = config.get_api_key()

    if not api_key:
        typer.echo("❌ API key not found. Please run 'daily login' to configure your Google API key.", err=True)
        raise typer.Exit(1)

    # Create the provider and model with the stored API key
    provider = GoogleProvider(api_key=api_key)
    model: GoogleModel = GoogleModel("gemini-2.5-flash-lite", provider=provider)

    note_agent = Agent(
        model=model,
        output_type=Note,
        system_prompt=(
            "You are an expert meeting facilitator Your task is to convert the user's "
            "audio transcription into a well-structured, clean and concise markdown note.\n"
            "Follow these rules:\n"
            "- Use appropriate markdown elements like headings highlighting (`**bold**` or `*italics*`).\n"
            "- Use idendation to structure topics, don't use listings like '*'",
            "- If you identify any action items, tasks, or follow-ups add them to the list of todos.\n"
            "- If there are some unclear words, mark them with a question mark (?).\n"
            "- If there are any problems, add them to errors and problems so they can be logged."
        ),
    )

    recorder = AudioRecorder(sample_rate=16000, channels=1)
    audio_file_path: Path = recorder.record()

    transcriber = WhisperTranscriber()
    transcription, _ = transcriber.transcribe(audio_file_path, show_progress=True)
    typer.echo(transcription)
    Path.unlink(audio_file_path)

    try:
        formatted_note: Note = note_agent.run_sync(transcription).output

    except Exception as e:
        print(f"\n❌ An error occurred while generating the note: {e}")
        return

    home_dir = Path.home()
    journal_dir = home_dir / "Documents" / "logseq" / "journals"
    utc_today_str = datetime.utcnow().strftime("%Y_%m_%d")
    note_file_path = journal_dir / f"{utc_today_str}.md"
    with open(note_file_path, "a", encoding="utf-8") as f:
        n = f.write(formatted_note.to_str() + "\n")

    typer.echo(formatted_note.to_str())
    typer.echo(f"DONE with {formatted_note.errors_and_problems}, {n} ")


@app.command()
def login():
    config = Config()
    api_key = typer.prompt("Enter your Google API key", hide_input=True)
    config.set_api_key(api_key)
    typer.echo("API key stored successfully")
