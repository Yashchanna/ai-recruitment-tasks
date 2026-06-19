# 🤖 Windows AI-CLI Executable Master Build Plan
## Gen AI Recruitment Tasks — Full Deployment Blueprint (Windows/PowerShell)

> **CRITICAL INSTRUCTION FOR THE EXECUTION AGENT:** 
> You are instructed to build and deploy this entire project with **zero manual user interaction**. You must automatically execute all installation commands in **Phase 0** (including `winget` packages, Node.js, Vercel CLI, GitHub CLI, and python packages) using silent/non-interactive flags. Do not ask the user for confirmation to install these tools—proceed automatically to bootstrap the environment.

---

## ⚙️ PHASE 0 — Environment Bootstrap & Dependency Installation (Windows)

> **AI AGENT INSTRUCTION:** Execute all commands in this phase in a **PowerShell** environment running as Administrator (if needed for installs). Use Windows `winget` and `npm` to install all system level packages and CLIs automatically.

### 0.1 — System Package Requirements (via winget)

```powershell
# Automatically install Git, Python 3, Node.js, and FFmpeg (essential for MoviePy video generation)
winget install --id Git.Git -e --silent --accept-source-agreements --accept-package-agreements
winget install --id Python.Python.3.11 -e --silent --accept-source-agreements --accept-package-agreements
winget install --id OpenJS.NodeJS.LTS -e --silent --accept-source-agreements --accept-package-agreements
winget install --id Gyan.FFmpeg -e --silent --accept-source-agreements --accept-package-agreements

# Refresh environment variables so newly installed tools are visible in current session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify installations
python --version
ffmpeg -version
git --version
node --version
npm --version
```

### 0.2 — Vercel CLI & GitHub CLI (Windows)

```powershell
# Install Vercel CLI globally (automatic install)
npm install -g vercel --yes

# Install GitHub CLI via winget
winget install --id GitHub.cli -e --silent --accept-source-agreements --accept-package-agreements

# Refresh path again for GH CLI
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
gh --version
```

### 0.3 — Python Virtual Environment & Packages (Windows)

```powershell
# Navigate to the workspace (adapt if workspace path is different)
cd C:\Users\dj\Desktop\bablu

# Create Python virtual environment using Windows syntax
python -m venv .venv

# Activate virtual environment in PowerShell
& .venv\Scripts\Activate.ps1

# Upgrade pip and install all Python dependencies
python -m pip install --upgrade pip
pip install `
  google-generativeai `
  feedparser `
  requests `
  beautifulsoup4 `
  moviepy `
  edge-tts `
  pillow `
  streamlit `
  python-dotenv `
  pytrends `
  gitpython `
  fastapi `
  uvicorn `
  jinja2 `
  rich `
  typer `
  httpx

# Save dependencies to requirements.txt
pip freeze > requirements.txt
```

---

## 🔑 PHASE 1 — API Key Collection (Interactive Setup Wizard)

> **AI AGENT INSTRUCTION:** Before writing any task code, create `setup.py` to collect keys and save them to `.env`. Code paths in Python must use `pathlib.Path` for system-agnostic path handling.

### 1.1 — Create the Setup Wizard (`setup.py`)

Create `/home/dj/Desktop/bablu/setup.py` (which translates to `C:\Users\dj\Desktop\bablu\setup.py` on Windows):

```python
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
        console.print(f"  Get it at: [link={key['url']}]{key['url']}[/link]")
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
```

### 1.2 — Create `.gitignore`

```
.env
.venv/
__pycache__/
*.pyc
*.mp4
*.mp3
*.wav
task1_video_generator/output/
node_modules/
.vercel/
*.log
Thumbs.db
```

---

## 📁 PHASE 2 — Directory Scaffold (Windows)

Use standard paths. The Python script structures should remain cross-platform by using `Path` from `pathlib` for all file reads, writes, and creations.

```
workspace-root\
├── .env
├── .env.example
├── .gitignore
├── setup.py
├── requirements.txt
├── README.md
├── task1_video_generator\
│   ├── README.md
│   ├── src\
│   │   ├── config.py
│   │   ├── scraper.py
│   │   ├── script_gen.py
│   │   ├── asset_fetcher.py
│   │   ├── tts.py
│   │   ├── video_builder.py
│   │   └── main.py
│   └── output\
├── task2_seo_blog_tool\
│   ├── README.md
│   ├── src\
│   │   ├── config.py
│   │   ├── product_scraper.py
│   │   ├── keyword_research.py
│   │   ├── blog_generator.py
│   │   ├── publisher.py
│   │   └── main.py
│   └── blogs\
└── task3_architecture_pipeline\
    ├── README.md
    ├── vercel.json
    ├── api\
    │   └── generate.py
    ├── public\
    │   └── index.html
    └── output\
```

---

## 📋 PHASE 3 — Task 1: AI Video Generation Tool

### Windows specific details:
- **FFmpeg Integration:** MoviePy uses FFmpeg. On Windows, installing FFmpeg via `winget` adds it to the system path. If MoviePy cannot find FFmpeg automatically, Python script must configure the path manually:
  ```python
  import os
  # Optional: Fallback configuration if MoviePy complains
  # os.environ["IMAGEIO_FFMPEG_EXE"] = r"C:\Path\To\ffmpeg.exe"
  ```
- **File System Paths:** Always use `pathlib.Path` dynamically instead of hardcoded `/` or `\` symbols to prevent pathing issues.

**Execute:**
```powershell
python -m task1_video_generator.src.main --topic "Artificial Intelligence" --output .\task1_video_generator\output\
```

---

## 📋 PHASE 4 — Task 2: SEO Blog Post Creation Tool

### Windows specific details:
- Python Git integration uses `GitPython`. On Windows, Git must be in the System environment variables (accomplished in Phase 0 via `winget`).
- Markdown paths should be written cleanly using `Path("task2_seo_blog_tool") / "blogs" / filename`.

**Execute:**
```powershell
python -m task2_seo_blog_tool.src.main --product "wireless earbuds" --publish both
```

---

## 📋 PHASE 5 — Task 3: Architecture Pipeline (Web App + Vercel)

Vercel configuration and code are unchanged because Vercel Serverless runs inside an isolated Linux execution environment. We build locally on Windows, configure `vercel.json` locally, and push using Vercel CLI.

### Vercel Deployment Commands (PowerShell)

```powershell
# Navigate to the subproject
cd task3_architecture_pipeline

# Login to Vercel with token
vercel login --token $env:VERCEL_TOKEN

# Deploy to production
vercel --prod --yes --token $env:VERCEL_TOKEN
```

---

## 🗂️ PHASE 6 — GitHub Repository Setup & Push (PowerShell)

```powershell
cd C:\Users\dj\Desktop\bablu

# Authenticate gh CLI with Token
$env:GITHUB_TOKEN | gh auth login --with-token

# Initialize git repo
git init
git add .
git commit -m "feat: initial project scaffold with all 3 tasks"

# Create public GitHub repository
gh repo create ai-internship-tasks `
  --public `
  --description "AI Video Generator, SEO Blog Tool, and Architecture Pipeline — Windows Build" `
  --source=. `
  --remote=origin `
  --push

# Make modular commits for each task
git add task1_video_generator\
git commit -m "feat(task1): complete video generation script using Pexels & MoviePy"

git add task2_seo_blog_tool\
git commit -m "feat(task2): complete SEO blog creation and posting automation"

git add task3_architecture_pipeline\
git commit -m "feat(task3): configure Vercel architecture pipeline integration"

git push origin main
```

---

## 📄 PHASE 7 & 8 — Master README & Submission

The markdown document output, Live links, and email submission template are exactly the same, but directory path instructions in the README should reflect Windows styling (`.\task1_video_generator\output\sample.mp4`).
