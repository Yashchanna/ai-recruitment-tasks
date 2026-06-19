#  GenAI Suite — Unified Recruitment Tasks Dashboard

Welcome to the **GenAI Recruitment Tasks Suite**! This repository houses three state-of-the-art AI automation tools built to demonstrate modular Python engineering, data scraping, speech synthesis, generative content modeling, and serverless deployment capabilities. 

All three tasks are accessible through a single, unified web interface deployed live on Vercel.

---

##  Live Production Deployments
You can interact with the live working prototypes directly in your browser:

*   ** Task 1: AI Video Studio** — [https://task3architecturepipeline.vercel.app/task1](https://task3architecturepipeline.vercel.app/task1)
*   ** Task 2: SEO Blog Creator** — [https://task3architecturepipeline.vercel.app/task2](https://task3architecturepipeline.vercel.app/task2)
*   ** Task 3: DevSpec Spec Studio** — [https://task3architecturepipeline.vercel.app/](https://task3architecturepipeline.vercel.app/)

---

## 📂 Project Structure

```text
workspace-root/
├── .env.example              # Template for API keys
├── .gitignore                # Standard repository exclusion rules
├── requirements.txt          # Python global project requirements
├── setup.py                  # CLI API key collection setup wizard
├── task1_video_generator/    # Task 1: Scraper, TTS Voice, & MoviePy Builder
│   ├── README.md             # Sub-project details
│   ├── process_report.md     # Pipeline execution report
│   ├── src/                  # Source files (scraper, script_gen, ui, etc.)
│   └── output/               # Local compiled video target directory
├── task2_seo_blog_tool/      # Task 2: Listing Crawler, Keyword harvester & blog creator
│   ├── process_report.md     # Pipeline execution report
│   ├── src/                  # Source files (product_scraper, keyword_research, etc.)
│   └── blogs/                # Locally published markdown reviews
└── task3_architecture_pipeline/ # Task 3: Unified FastAPI web app & spec generator
    ├── process_report.md     # Pipeline execution report
    ├── vercel.json           # Vercel Serverless configurations
    ├── api/                  # Main serverless entry point (generate.py)
    └── src/                  # Co-located dependencies for serverless routes
```

---

##  Task Deep Dives & Execution Workflows

###  Task 1: AI Video Studio
*   **Objective:** Create an AI tool that scrapes trending news headlines, generates short narrated scripts, and builds 30–60 second video clips.
*   **Workflow:**
    1.  **News Scraper:** Extracts real-time trending news summaries from the Google News RSS feed using `feedparser`.
    2.  **Storyboard Generator:** Prompts Google Gemini API (`gemini-3.5-flash`) to generate a JSON storyboard (spoken script, keyword visual queries, and subtitle text).
    3.  **Speech Synthesis:** Generates high-fidelity human speech voiceovers using `edge-tts`.
    4.  **Visual Sourcing:** queries Unsplash/Pexels for high-quality vertical visuals matching the storyboard scenes.
    5.  **Text Overlay:** Annotates text boxes onto the frames natively via Pillow to avoid system-level ImageMagick dependencies.
    6.  **MoviePy Compilation (Local):** Crops to portrait 9:16 vertical shorts layout, syncs clips with TTS sound length, and renders the H.264/AAC `.mp4` video.
    7.  **Virtual Web Player (Serverless):** Implements a Ken-Burns slideshow video player on Vercel utilizing base64 data-uris.
*   **Detailed Process Report:** [task1_video_generator/process_report.md](file:///E:/Syn%20Assesment/task1_video_generator/process_report.md)

###  Task 2: SEO Blog Creator
*   **Objective:** Crawl popular e-commerce listings, scrape autocomplete Google search queries, and draft a 150-200 word review blog post naturally incorporating target SEO keywords.
*   **Workflow:**
    1.  **Marketplace Scraper:** Queries eBay for product keywords and parses listings (title, price, link) using `BeautifulSoup`.
    2.  **Keyword Research:** Scrapes autocomplete keywords from Google Suggest search suggestions.
    3.  **Generator:** Prompt Gemini to craft a markdown blog review featuring catalog elements and incorporating the SEO phrases.
    4.  **Publisher:** Saves files locally and pushes live articles via the Dev.to Articles API.
*   **Detailed Process Report:** [task2_seo_blog_tool/process_report.md](file:///E:/Syn%20Assesment/task2_seo_blog_tool/process_report.md)

### 📐 Task 3: DevSpec Spec Studio
*   **Objective:** Simplify technical project modeling by automatically converting high-level business requirements into low-level technical specifications.
*   **Workflow:**
    1.  **Parser:** Evaluates functional requirements to identify modules, schemas, database tables, and API routes.
    2.  **Platform Override:** Dynamically alters technological recommendations based on platform keywords (e.g. Flutter, React Native).
    3.  **Export:** Generates database schemas (with UUID/Timestamp types), FastAPI routing pseudocode, and lets users download spec files directly as markdown.
*   **Detailed Process Report:** [task3_architecture_pipeline/process_report.md](file:///E:/Syn%20Assesment/task3_architecture_pipeline/process_report.md)

---

##  Installation & Local Execution

### 1. Prerequisite Installations
Ensure you have Python 3.11+, Node.js (LTS), and Git installed. 

Install **FFmpeg** on your machine for MoviePy video generation:
*   **Windows (PowerShell as Admin):**
    ```powershell
    winget install Gyan.FFmpeg
    ```

### 2. Install Project Dependencies
Initialize a virtual environment and install dependencies:
```powershell
# Create & Activate Virtual Environment
python -m venv .venv
& .venv\Scripts\Activate.ps1

# Install global requirements
pip install -r requirements.txt
```

### 3. Run the Key Setup Wizard
Run the setup script to configure your `.env` keys (Gemini API, Dev.to key, Pexels API):
```powershell
python setup.py
```

### 4. Launching the Local App
*   **Task 1 Streamlit App:**
    ```powershell
    streamlit run task1_video_generator/src/ui.py
    ```
*   **Task 2 Streamlit App:**
    ```powershell
    streamlit run task2_seo_blog_tool/src/ui.py
    ```
*   **Task 3 Local Web Server:**
    ```powershell
    uvicorn task3_architecture_pipeline.api.generate:app --reload
    ```
