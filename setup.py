#!/usr/bin/env python3
"""
One-time API Key Setup Wizard for Gen AI Recruitment Tasks.
Run: python setup.py
"""
import os
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()
ENV_FILE = Path(".env")
ENV_EXAMPLE = Path(".env.example")

KEYS = [
    {
        "var": "GEMINI_API_KEY",
        "label": "Google Gemini API Key",
        "url": "https://aistudio.google.com/apikey",
        "required": True,
        "secret": True,
    },
    {
        "var": "PEXELS_API_KEY",
        "label": "Pexels Stock Video API Key (for Task 1)",
        "url": "https://www.pexels.com/api/",
        "required": True,
        "secret": True,
    },
    {
        "var": "DEVTO_API_KEY",
        "label": "Dev.to Blog Publishing API Key (for Task 2)",
        "url": "https://dev.to/settings/extensions",
        "required": True,
        "secret": True,
    },
    {
        "var": "GITHUB_TOKEN",
        "label": "GitHub Personal Access Token (for Task 2 GitHub Pages)",
        "url": "https://github.com/settings/tokens",
        "required": True,
        "secret": True,
    },
    {
        "var": "VERCEL_TOKEN",
        "label": "Vercel Deployment Token (for Task 3 live demo)",
        "url": "https://vercel.com/account/tokens",
        "required": True,
        "secret": True,
    },
]


def main():
    console.print(Panel.fit("🤖 Gen AI Task Suite — API Key Setup Wizard (Windows)", style="bold cyan"))
    
    env_values = {}
    example_values = {}
    
    for key in KEYS:
        console.print(f"\n[bold yellow]{key['label']}[/bold yellow]")
        console.print(f"  Get it at: [link={key['url']}] {key['url']}[/link]")
        value = Prompt.ask(f"  Enter {key['var']}", password=key["secret"], default="")
        
        if key["required"] and not value.strip():
            console.print("[bold red]  ⚠ This key is required. Leaving blank will disable that task.[/bold red]")
        
        env_values[key["var"]] = value.strip()
        example_values[key["var"]] = f"your_{key['var'].lower()}_here"
    
    # Write .env with Windows newline safety
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        for k, v in env_values.items():
            f.write(f'{k}="{v}"\n')
    
    # Write .env.example
    with open(ENV_EXAMPLE, "w", encoding="utf-8") as f:
        for k, v in example_values.items():
            f.write(f'{k}="{v}"\n')
    
    console.print(Panel.fit("✅ .env file saved. Run any task now!", style="bold green"))


if __name__ == "__main__":
    main()
