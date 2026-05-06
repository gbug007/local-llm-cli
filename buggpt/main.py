# global imports
from pathlib import Path
import argparse
import re
import requests
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule

# local imports
from .build_context import *
from .handlers import *

# constants
MAX_FILE_READS = 10
ENDPOINT = "http://localhost:5001/v1/chat/completions"
HEADERS = {"Content-Type": "application/json"}


def get_ai_response(conversation: list) -> str:
    """Send prompt to AI and return cleaned response."""

    payload = {
        "model": "koboldcpp",
        "messages": conversation,
        "max_tokens": 1500,
        "temperature": 0.7,
    }

    try:
        response = requests.post(ENDPOINT, json=payload, headers=HEADERS, timeout=30)
        response.raise_for_status() 
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    
    except (KeyError, IndexError):
        return "No response text found."
    
    except Exception as e:
        return f"Error: {str(e)}"
    

def get_response(conversation: list, target_path: Path, console: Console) -> str:
    """Run the agentic file-read loop and return the final response."""
    for _ in range(MAX_FILE_READS):
        response = get_ai_response(conversation)
        filepath = extract_filepath(response)

        if not filepath:
            break

        console.print(f"[dim]Reading file: {filepath}[/]")
        contents = read_file_safe(target_path / filepath)
        conversation.append({"role": "assistant", "content": response})
        conversation.append({"role": "user", "content": f"Contents of {filepath}:\n\n```\n{contents}\n```"})

    conversation.append({"role": "assistant", "content": response})

    return response


def get_user_input(console: Console) -> str:
    """Collect input, supporting multiline paste with blank line to submit."""
    first_line = console.input("\n[bold cyan]You:[/] ").strip()
    if not first_line:
        return ""
    
    lines = [first_line]
    while True:
        line = console.input("[dim]...[/] ")
        if line == "":
            break
        lines.append(line)
    
    return "\n".join(lines)


def extract_filepath(response: str) -> str | None:
    """Extract a valid filepath from a READ_FILE: directive, or return None."""
    if "READ_FILE:" not in response:
        return None
    
    # strips the path from the AI response
    candidate = response[response.index("READ_FILE:"):] \
            .removeprefix("READ_FILE:") \
            .strip() \
            .splitlines()[0] \
            .strip("`\"' ")
    
    # only accepts paths
    return candidate if re.match(r'^[\w./\-]+\.\w+$', candidate) else None


def display_response(console: Console, response: str):
    """Render the AI response as Markdown."""
    console.rule("AI Response", style="dark_orange")
    console.print()
    console.print(Markdown(response))
    console.print()
    console.rule(style="dark_orange")


def change_directory(path_input: str, console: Console) -> tuple[Path, list] | None:
    """Change target directory and return new path and conversation."""
    new_path = Path(path_input).expanduser().resolve()

    if not new_path.is_dir():
        console.print(f"[red]Error: '{new_path}' is not a valid directory.[/]")
        return None
    
    conversation = build_conversation(new_path)
    console.print(f"[dim]Switched to: {new_path}[/]")
    return new_path, conversation


def main():
    # parse --path argument (optional)
    parser = argparse.ArgumentParser(description="BugGPT - directory-aware AI assistant")
    parser.add_argument("--path", type=Path, default=Path.cwd(),
                        help="Directory to use as context (default: current directory)")
    args = parser.parse_args()

    # resolve/validate path
    target_path = args.path.resolve()
    if not target_path.is_dir():
        print(f"Error: '{target_path}' is not a valid directory.")
        return
    
    # Setup rich console
    console = Console()
    conversation = build_conversation(target_path)

    console.print(Panel(
        Markdown(
            "Enter your question or message below.\n\n"
            "**Commands:**\n"
            "- `cd <path>` — change target directory\n"
            "- `ls` — list current directory\n"
            "- `!<command>` — run a shell command\n"
            "- `/read <file>` — inject a file into the conversation\n"
            "- `/clear` — reset conversation history\n"
            "- `/help` — show this message\n"
            "- `quit` or `exit` — exit\n"
        ),
        title="[bold dark_orange]Welcome to BugGPT![/]",
        subtitle=f"[dim]{target_path}[/]",
        border_style="bold dark_orange",
    ))
    
    while True:
        # user_input = console.input("\n[bold cyan]You:[/] ").strip()
        user_input = get_user_input(console)

        if user_input.lower() in ('quit', 'exit'):
            console.print("Goodbye!\n", style="bold dark_orange")
            break
        elif user_input.startswith('!'):
            handle_shell_command(user_input[1:].strip(), console)
            continue
        elif user_input.startswith('cd '):
            result = change_directory(user_input[3:].strip(), console)
            if result:
                target_path, conversation = result
            continue
        elif user_input == 'ls':
            handle_ls(target_path, console)
            continue
        elif user_input == '/clear':
            conversation = handle_clear(conversation, target_path, console)
            continue
        elif user_input.startswith('/read '):
            conversation = handle_read(user_input[6:].strip(), target_path, conversation, console)
            continue
        elif user_input == '/help':
            handle_help(console)
            continue
        elif not user_input:
            console.print("Please enter a valid input.", style="dim")
            continue
        else:
            conversation.append({"role": "user", "content": user_input})
            console.print("Thinking...\n", style="dim italic")

            response = get_response(conversation, target_path, console)
            display_response(console, response)


if __name__ == "__main__":
    main()