import os
from pathlib import Path
import argparse

import re

import json
import requests
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule

from .build_context import *

# Configuration
# Uses KoboldCPP's API endpoint, which is typically at localhost:5001
endpoint = "http://localhost:5001/v1/chat/completions"
# Headers for the HTTP request
headers = {"Content-Type": "application/json"}

def get_ai_response(conversation: list) -> str:
    """Send prompt to AI and return cleaned response."""

    payload = {
        "model": "koboldcpp",
        "messages": conversation,
        "max_tokens": 500,
        "temperature": 0.7,
    }

    try:
        # posts to API and raises an error if request fails
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status() 

        data = response.json()
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content'].strip()
        else:
            return "No response text found."
    except Exception as e:
        return f"Error: {str(e)}"




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
    conversation = []

    system_context = build_system_context(target_path)
    conversation.append({"role": "user", "content": system_context})
    conversation.append({"role": "assistant", "content": 
                         "Understood. I have your directory structure and will " +
                         "request specific files as needed."})

    console.print()
    console.print(
        Panel(
            "Enter your question or message (type 'quit' or 'exit' to exit):\n\n" +
            "[bold dark_orange]BugGPT[/] is powered by [bold cyan]KoboldCPP[/], an application for running local LLMs.", 
            title="Welcome to BugGPT!",
            border_style="bold dark_orange",
        ),

    )
    
    while True:
        console.print()

        # user input
        user_input = console.input("[bold cyan]You:[/] ").strip()

        # exit program
        if user_input.lower() in ('quit', 'exit'):
            console.print("Goodbye!\n", style="bold dark_orange")
            break
        # invalid input
        elif not user_input:
            console.print("Please enter a valid input.", style="dim")
            continue
        
        conversation.append({"role": "user", "content": user_input})
        console.print("Thinking...\n", style="dim italic")

        MAX_FILE_READS = 10
        file_reads = 0
        
        # file request loop
        while True:
            # looping behavior for read requests from the AI
            response = get_ai_response(conversation)
            filepath = extract_filepath(response)

            if filepath:
                console.print(f"[dim]Reading file: {filepath}[/]")
                contents = read_file_safe(target_path / filepath)
                file_message = f"Contents of {filepath}:\n\n```\n{contents}\n```"
                conversation.append({"role": "assistant", "content": response})
                conversation.append({"role": "user", "content": file_message})
            else:
                conversation.append({"role": "assistant", "content": response})
                break


        display_response(console, response)


def extract_filepath(response: str) -> str | None:
    """Extract a valid filepath from a READ_FILE: response, or return None."""
    if "READ_FILE:" not in response:
        return None
    
    candidate = response[response.index("READ_FILE:"):] \
            .removeprefix("READ_FILE:") \
            .strip() \
            .splitlines()[0] \
            .strip("`\"' ")
    
    # Valid path: only normal path characters, must end with a file extension
    if re.match(r'^[\w./\-]+\.\w+$', candidate):
        return candidate
    return None


def display_response(console: Console, response: str):
    # Format the AI response as Markdown for better readability
    formatted_response = Markdown(response)
    console.rule("AI Response: ", style="dark_orange", align="left")
    console.print()
    console.print(formatted_response)
    console.print()
    console.rule(style="dark_orange")


if __name__ == "__main__":
    main()