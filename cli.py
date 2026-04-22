import json
import requests
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule

# Configuration
# Uses KoboldCPP's API endpoint, which is typically at localhost:5001
endpoint = "http://localhost:5001/v1/chat/completions"
# Headers for the HTTP request
headers = {"Content-Type": "application/json"}

def get_ai_response(prompt):
    """Send prompt to AI and return cleaned response."""
    payload = {
        "model": "koboldcpp",
        "messages": [
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 200,
        "temperature": 0.7,
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()  # Raises HTTPError for bad responses

        data = response.json()
        # Extract the actual generated text
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content'].strip()
        else:
            return "No response text found."
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Setup rich console
    console = Console()

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
        user_input = console.input("[bold cyan]You:[/] ").strip()

        if user_input.lower() == 'quit' or user_input.lower() == 'exit':
            console.print("Goodbye!\n", style="bold dark_orange")
            break
        elif not user_input:
            console.print("Please enter a valid input.", style="dim")
            continue
        
        console.print("Thinking...\n", style="dim italic")
    
        ai_response = get_ai_response(user_input)

        # Format the AI response as Markdown for better readability
        formatted_response = Markdown(ai_response)
        console.rule("AI Response: ", style="dark_orange", align="left")
        console.print()
        console.print(formatted_response)
        console.print()
        console.rule(style="dark_orange")

if __name__ == "__main__":
    main()