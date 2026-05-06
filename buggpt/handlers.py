# global imports
from pathlib import Path
import subprocess
from rich.console import Console
from rich.markdown import Markdown

from .build_context import (
    build_system_context, 
    build_conversation, 
    read_file_safe
)


def handle_shell_command(command: str, console: Console):
    """Run a shell command and print output."""
    try:
        result = subprocess.run(
            command, shell=True, text=True,
            capture_output=True, timeout=10
        )
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(result.stderr, style="red")
        if not result.stdout and not result.stderr:
            console.print(f"[dim]Command exited with code {result.returncode}[/]")
    except subprocess.TimeoutExpired:
        console.print("[red]Command timed out — interactive or long-running commands aren't supported.[/]")


def handle_clear(conversation: list, target_path: Path, console: Console) -> list:
    """Reset conversation history, keeping directory context."""
    console.print("[dim]Conversation cleared.[/]")
    return build_conversation(target_path)


def handle_read(filepath: str, target_path: Path, conversation: list, console: Console) -> list:
    """Manually inject a file into the conversation."""
    contents = read_file_safe(target_path / filepath)
    console.print(f"[dim]Injecting file: {filepath}[/]")
    conversation.append({"role": "user", "content": f"Contents of {filepath}:\n\n```\n{contents}\n```"})
    conversation.append({"role": "assistant", "content": "Thanks, I've read that file."})
    return conversation


def handle_context(target_path: Path, console: Console):
    """Print the current system context."""
    console.print(Markdown(build_system_context(target_path)))


def handle_ls(target_path: Path, console: Console):
    """Display the current directory contents."""
    try:
        entries = sorted(target_path.iterdir(), key=lambda e: e.name.lower())
        output = " ".join(
            f"[bold blue]{e.name}[/]" if e.is_dir() else e.name
            for e in entries
        )
        console.print(output)
    except PermissionError:
        console.print("[red]Permission denied.[/]")


def handle_help(console: Console):
    console.print(Markdown(
        "## BugGPT Commands\n"
        "- `cd <path>` — change target directory\n"
        "- `ls` - list current directory\n"
        "- `!<command>` — run a shell command\n"
        "- `/clear` — reset conversation history\n"
        "- `/read <file>` — inject a file into the conversation\n"
        "- `/help` — show this message\n"
        "- `quit` or `exit` — exit BugGPT\n"
    ))