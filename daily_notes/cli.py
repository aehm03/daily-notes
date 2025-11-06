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
    comments: str

    def to_str(self) -> str:
        note: str = f"## {self.heading}\n"
        note += textwrap.indent(self.note_content, "  - ")
        note += "\n"
        note += "\n".join([f"  - TODO {action}" for action in self.todos])
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

    system_prompt=(
                "You are an expert meeting facilitator and note-taker. Your task is to process a raw audio transcription "
                "and structure its content perfectly into the provided `Note` Pydantic model.\n"
                "Follow these rules precisely to populate each field:\n\n"
                "1.  **`heading`:**\n"
                "    - Analyze the entire transcript and generate a single, concise title for the note (e.g., 'Project Phoenix Sync - Q4 Planning').\n"
                "    - This title should summarize the main topic of the discussion.\n\n"
                "2.  **`note_content`:**\n"
                "    - Create a clean, well-structured summary of the transcript's key points, decisions, and discussion topics.\n"
                "    - Use `**bold**` or `*italics*` for emphasis on key terms or people.\n"
                "    - Use blank lines to separate distinct topics or paragraphs.\n"
                "    - **Crucially:** Do NOT include the heading here (it's a separate field). Do NOT use markdown lists (`*`, `-`) or add any manual indentation; the system handles this formatting.\n\n"
                "3.  **`todos`:**\n"
                "    - Identify all clear action items, tasks, or follow-ups mentioned.\n"
                "    - Add *only* the task description string to the list (e.g., \"Send the proposal to the client team\").\n"
                "    - Do NOT add prefixes like 'TODO' or any markdown.\n"
                "    - Each task should be a separate string in the `list[str]`.\n\n"
                "4.  **`comments`:**\n"
                "    - Use this field for any meta-observations about the transcript or process.\n"
                "    - Examples: 'Audio quality was poor during the second half.' or 'The speaker's identity for topic X was unclear.'\n"
                "    - If you have no comments, you can leave this field empty or state 'No comments.'\n\n"
                "**Special Rule - Transcript Quality:**\n"
                "The transcript is not of perfect quality. If there are unclear words or terms which do not make sense in the context, "
                "**do not invent content**. Mark the unclear spot directly in the `note_content` with the exact marker `#[[?]]`."
            ),

    note_agent = Agent(
        model=model,
        output_type=Note,
        system_prompt=system_prompt,
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
    typer.echo(f"DONE with comments: {formatted_note.comments}, length:{n} ")


@app.command()
def login():
    config = Config()
    api_key = typer.prompt("Enter your Google API key", hide_input=True)
    config.set_api_key(api_key)
    typer.echo("API key stored successfully")
