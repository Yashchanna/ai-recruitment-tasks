from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import re
from typing import Dict, Any

# Dynamic imports with fallback for Vercel deployment paths
try:
    from src.product_scraper import scrape_products
    from src.keyword_research import select_seo_keywords
    from src.blog_generator import generate_blog
except ImportError:
    try:
        from task3_architecture_pipeline.src.product_scraper import scrape_products
        from task3_architecture_pipeline.src.keyword_research import select_seo_keywords
        from task3_architecture_pipeline.src.blog_generator import generate_blog
    except ImportError:
        scrape_products = None
        select_seo_keywords = None
        generate_blog = None

try:
    from src.video_scraper import get_trending_news
    from src.video_script_gen import generate_script
    from src.video_asset_fetcher import get_scene_image_url
    from src.video_tts import generate_voiceover_base64
except ImportError:
    try:
        from task3_architecture_pipeline.src.video_scraper import get_trending_news
        from task3_architecture_pipeline.src.video_script_gen import generate_script
        from task3_architecture_pipeline.src.video_asset_fetcher import get_scene_image_url
        from task3_architecture_pipeline.src.video_tts import generate_voiceover_base64
    except ImportError:
        get_trending_news = None
        generate_script = None
        get_scene_image_url = None
        generate_voiceover_base64 = None

app = FastAPI()

# -------------------------------------------------------------
# SHARED NAV HEADER HTML & CSS
# -------------------------------------------------------------
SHARED_HEADER = """
<header class="app-header">
  <div class="nav-brand">🤖 GenAI Recruitment Suite</div>
  <nav class="nav-links">
    <a href="/task1" id="nav-t1">Task 1: AI Video Studio</a>
    <a href="/task2" id="nav-t2">Task 2: Blog Creator</a>
    <a href="/" id="nav-t3">Task 3: Architecture Spec</a>
  </nav>
</header>
"""

SHARED_NAV_STYLE = """
:root {
  --bg: #090d16;
  --card-bg: rgba(17, 24, 39, 0.6);
  --border: rgba(255, 255, 255, 0.08);
  --primary: #6366f1;
  --primary-hover: #4f46e5;
  --text: #f3f4f6;
  --text-secondary: #9ca3af;
  --success: #10b981;
}
body {
  background-color: var(--bg);
  color: var(--text);
  font-family: 'Inter', sans-serif;
  max-width: 1080px;
  margin: 32px auto;
  padding: 0 24px;
  line-height: 1.6;
  background-image: radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 60%);
}
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 28px;
  background: rgba(17, 24, 39, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: 16px;
  margin-bottom: 40px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
}
.nav-brand {
  font-family: 'Outfit', sans-serif;
  font-weight: 700;
  font-size: 1.3rem;
  background: linear-gradient(135deg, #a78bfa 0%, #6366f1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.nav-links a {
  font-weight: 600;
  color: var(--text-secondary);
  text-decoration: none;
  margin-left: 28px;
  font-size: 0.95rem;
  transition: color 0.2s, text-shadow 0.2s;
}
.nav-links a:hover {
  color: #a78bfa;
}
.nav-links a.active {
  color: #818cf8;
  text-shadow: 0 0 10px rgba(129, 140, 248, 0.4);
}
.card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
  transition: border-color 0.2s ease, transform 0.2s ease;
}
.card:hover {
  border-color: rgba(99, 102, 241, 0.3);
}
button {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  font-size: 1rem;
  transition: opacity 0.2s, transform 0.1s;
}
button:hover {
  opacity: 0.95;
  transform: translateY(-1px);
}
button:active {
  transform: translateY(0);
}
"""

# -------------------------------------------------------------
# TASK 1: AI VIDEO GENERATION HTML
# -------------------------------------------------------------
HTML_CONTENT_TASK1 = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>ViralReels AI — Video Generator Studio</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
      __SHARED_NAV_STYLE__
      
      .row {
        display: flex;
        gap: 32px;
        flex-wrap: wrap;
      }
      .col-left {
        flex: 1 1 55%;
      }
      .col-right {
        flex: 1 1 35%;
        max-width: 420px;
      }
      .news-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 20px;
      }
      .news-item {
        background: rgba(255,255,255,0.02);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px;
        cursor: pointer;
        transition: background 0.2s, border-color 0.2s;
      }
      .news-item:hover {
        background: rgba(99, 102, 241, 0.08);
        border-color: rgba(99, 102, 241, 0.3);
      }
      .news-item.active {
        background: rgba(99, 102, 241, 0.15);
        border-color: var(--primary);
      }
      .news-title {
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 6px;
        color: #fff;
      }
      .news-desc {
        font-size: 0.8rem;
        color: var(--text-secondary);
        line-height: 1.4;
      }
      label {
        font-weight: 500;
        font-size: 0.95rem;
        color: var(--text-secondary);
        display: block;
        margin-bottom: 8px;
      }
      input[type="text"], select {
        width: 100%;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid var(--border);
        background: rgba(10, 15, 25, 0.8);
        color: var(--text);
        font-family: inherit;
        font-size: 1rem;
        box-sizing: border-box;
        margin-bottom: 16px;
      }
      input:focus, select:focus {
        outline: none;
        border-color: var(--primary);
      }
      
      /* Web Player Styles */
      .player-card {
        background: #0f172a;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 20px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
      }
      .video-viewport {
        position: relative;
        width: 100%;
        aspect-ratio: 9/16;
        background: #020617;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.05);
      }
      .video-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transform: scale(1.0);
        transition: transform 12s linear;
      }
      .video-img.zooming {
        transform: scale(1.18);
      }
      .caption-overlay {
        position: absolute;
        bottom: 40px;
        left: 20px;
        right: 20px;
        background: rgba(15, 23, 42, 0.92);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 16px;
        border-radius: 16px;
        text-align: center;
      }
      .caption-text {
        font-family: 'Outfit', sans-serif;
        color: #fff;
        font-weight: 700;
        font-size: 1.05rem;
        margin: 0;
        letter-spacing: 0.02em;
        text-transform: uppercase;
      }
      .player-controls {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-top: 16px;
      }
      .control-btn {
        background: rgba(255,255,255,0.06);
        border: 1px solid var(--border);
        color: #fff;
        border-radius: 50%;
        width: 46px;
        height: 46px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
      }
      .control-btn:hover {
        background: rgba(99, 102, 241, 0.2);
        border-color: var(--primary);
      }
      .progress-container {
        width: 100%;
        height: 6px;
        background: rgba(255,255,255,0.1);
        border-radius: 3px;
        margin-top: 12px;
        overflow: hidden;
      }
      .progress-bar {
        width: 0%;
        height: 100%;
        background: var(--primary);
        transition: width 0.1s linear;
      }
    </style>
  </head>
  <body>
    __SHARED_HEADER__
    
    <div class="row">
      <div class="col-left">
        <div class="card">
          <h2 style="font-family:Outfit; margin-top:0;">📰 Trending Stories</h2>
          <p style="color:var(--text-secondary); font-size:0.9rem;">Select a trending article below, or type a custom topic to generate a short narrative reel.</p>
          
          <div style="margin-bottom:16px;">
            <button id="scrape-btn">🔄 Scrape Trending News</button>
          </div>
          
          <div id="news-container" class="news-grid">
            <div style="grid-column: span 2; text-align: center; padding: 20px; color: var(--text-secondary);">Click button to retrieve live news.</div>
          </div>
          
          <label for="topic">Selected Video Topic</label>
          <input type="text" id="topic" value="Self-driving Cars Revolution">
          
          <label for="voice">Edge Narration Voice</label>
          <select id="voice">
            <option value="en-US-JennyNeural">en-US-JennyNeural (Female - Conversational)</option>
            <option value="en-US-GuyNeural">en-US-GuyNeural (Male - Professional)</option>
            <option value="en-US-AriaNeural">en-US-AriaNeural (Female - News Reader)</option>
            <option value="en-GB-SoniaNeural">en-GB-SoniaNeural (UK Female)</option>
          </select>
          
          <button id="generate-btn" style="width:100%;">🎬 Create Virtual AI Video</button>
        </div>
        
        <div id="script-card" class="card" style="display:none;">
          <h3 style="font-family:Outfit; margin-top:0;">📄 Generated Storyboard Script</h3>
          <div id="script-content"></div>
        </div>
      </div>
      
      <div class="col-right">
        <div class="player-card">
          <h3 style="font-family:Outfit; margin-top:0; color:#fff; text-align:center;">📺 Sandbox Video Player</h3>
          
          <div class="video-viewport">
            <img id="player-img" class="video-img" src="https://picsum.photos/1080/1920?random=1" />
            <div class="caption-overlay">
              <p id="player-text" class="caption-text">VIDEO PLAYER IDLE</p>
            </div>
          </div>
          
          <div class="progress-container">
            <div id="player-progress" class="progress-bar"></div>
          </div>
          
          <div class="player-controls">
            <button class="control-btn" id="play-pause" title="Play/Pause">▶</button>
            <button class="control-btn" id="prev-scene" title="Prev Scene">⏮</button>
            <button class="control-btn" id="next-scene" title="Next Scene">⏭</button>
          </div>
          
          <div id="scene-tracker" style="text-align:center; color:var(--text-secondary); margin-top:10px; font-size:0.85rem;">Scene 0 / 0</div>
          
          <audio id="player-audio" style="display:none;"></audio>
        </div>
      </div>
    </div>
    
    <script>
      document.getElementById("nav-t1").classList.add("active");
      
      let trendingArticles = [];
      let scenes = [];
      let currentSceneIdx = 0;
      let isPlaying = false;
      let progressInterval = null;
      
      const audioEl = document.getElementById("player-audio");
      const imgEl = document.getElementById("player-img");
      const textEl = document.getElementById("player-text");
      const playBtn = document.getElementById("play-pause");
      const trackerEl = document.getElementById("scene-tracker");
      const progressEl = document.getElementById("player-progress");
      
      // Scrape news articles
      document.getElementById("scrape-btn").addEventListener("click", async () => {
        const grid = document.getElementById("news-container");
        grid.innerHTML = '<div style="grid-column: span 2; text-align: center; padding: 20px;">Fetching headlines...</div>';
        try {
          const resp = await fetch("/api/task1/scrape-news");
          const data = await resp.json();
          trendingArticles = data.articles || [];
          grid.innerHTML = "";
          
          if(trendingArticles.length === 0) {
            grid.innerHTML = '<div style="grid-column: span 2; text-align: center; padding: 20px; color: var(--text-secondary);">No stories scraped.</div>';
            return;
          }
          
          trendingArticles.forEach((art, idx) => {
            const el = document.createElement("div");
            el.className = "news-item";
            el.innerHTML = `
              <div class="news-title">${art.title}</div>
              <div class="news-desc">${art.summary.substring(0, 100)}...</div>
            `;
            el.onclick = () => {
              document.querySelectorAll(".news-item").forEach(item => item.classList.remove("active"));
              el.classList.add("active");
              document.getElementById("topic").value = art.title;
              window.selectedContext = art.summary;
            };
            grid.appendChild(el);
          });
        } catch (e) {
          grid.innerHTML = `<div style="grid-column: span 2; text-align: center; padding: 20px; color: #ef4444;">Scraper error: ${e}</div>`;
        }
      });
      
      // Load scene asset and set up browser player components
      function loadScene(idx) {
        if (!scenes || scenes.length === 0) return;
        if (idx < 0) idx = 0;
        if (idx >= scenes.length) idx = scenes.length - 1;
        
        currentSceneIdx = idx;
        const scene = scenes[idx];
        
        // Reset transitions
        imgEl.classList.remove("zooming");
        void imgEl.offsetWidth; // trigger reflow
        
        imgEl.src = scene.image_url;
        textEl.textContent = scene.overlay_text;
        audioEl.src = scene.audio_base64;
        
        trackerEl.textContent = `Scene ${idx + 1} / ${scenes.length}`;
        progressEl.style.width = "0%";
        
        if (isPlaying) {
          audioEl.play().catch(e => console.log("Audio play deferred", e));
          imgEl.classList.add("zooming");
          startProgressTracking();
        }
      }
      
      function startProgressTracking() {
        clearInterval(progressInterval);
        progressInterval = setInterval(() => {
          if(audioEl.duration) {
            const pct = (audioEl.currentTime / audioEl.duration) * 100;
            progressEl.style.width = pct + "%";
          }
        }, 100);
      }
      
      // Controls hookups
      playBtn.addEventListener("click", () => {
        if(scenes.length === 0) return;
        isPlaying = !isPlaying;
        if (isPlaying) {
          playBtn.textContent = "⏸";
          audioEl.play().catch(e => console.log(e));
          imgEl.classList.add("zooming");
          startProgressTracking();
        } else {
          playBtn.textContent = "▶";
          audioEl.pause();
          imgEl.classList.remove("zooming");
          clearInterval(progressInterval);
        }
      });
      
      document.getElementById("prev-scene").addEventListener("click", () => {
        if(currentSceneIdx > 0) loadScene(currentSceneIdx - 1);
      });
      
      document.getElementById("next-scene").addEventListener("click", () => {
        if(currentSceneIdx + 1 < scenes.length) loadScene(currentSceneIdx + 1);
      });
      
      audioEl.onended = () => {
        if(currentSceneIdx + 1 < scenes.length) {
          loadScene(currentSceneIdx + 1);
        } else {
          isPlaying = false;
          playBtn.textContent = "▶";
          imgEl.classList.remove("zooming");
          progressEl.style.width = "100%";
          clearInterval(progressInterval);
        }
      };
      
      // Generate reel
      document.getElementById("generate-btn").addEventListener("click", async () => {
        const topic = document.getElementById("topic").value;
        const voice = document.getElementById("voice").value;
        const context = window.selectedContext || "";
        
        const genBtn = document.getElementById("generate-btn");
        genBtn.disabled = true;
        genBtn.textContent = "⏳ Generating Storyboard & Narration...";
        
        try {
          const resp = await fetch("/api/task1/generate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({topic, voice, context})
          });
          const data = await resp.json();
          
          if(data.error) {
            alert("Generation failed: " + data.error);
            return;
          }
          
          scenes = data.scenes || [];
          
          // Display script content
          const scriptDiv = document.getElementById("script-card");
          const scriptContent = document.getElementById("script-content");
          scriptDiv.style.display = "block";
          scriptContent.innerHTML = `<h4>Reel Title: ${data.title}</h4>` + scenes.map(s => `
            <div style="border-left:3px solid var(--primary); padding-left:14px; margin-bottom:14px;">
              <strong>Scene ${s.scene_num} Text Overlay:</strong> <span style="color:#f43f5e">${s.overlay_text}</span><br>
              <strong>Narration:</strong> <em>"${s.narration}"</em>
            </div>
          `).join("");
          
          // Start player
          isPlaying = true;
          playBtn.textContent = "⏸";
          loadScene(0);
          
        } catch(e) {
          alert("Server error: " + e);
        } finally {
          genBtn.disabled = false;
          genBtn.textContent = "🎬 Create Virtual AI Video";
        }
      });
    </script>
  </body>
</html>
"""

# -------------------------------------------------------------
# TASK 2: SEO BLOG CREATOR HTML
# -------------------------------------------------------------
HTML_CONTENT_TASK2 = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>ContentEngine Pro — SEO Blog Creator</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
      __SHARED_NAV_STYLE__
      
      label {
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text-secondary);
        display: block;
        margin-bottom: 10px;
      }
      input[type="text"] {
        width: 100%;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid var(--border);
        background: rgba(10, 15, 25, 0.8);
        color: var(--text);
        font-family: inherit;
        font-size: 1rem;
        box-sizing: border-box;
        transition: border-color 0.2s;
      }
      input[type="text"]:focus {
        outline: none;
        border-color: var(--primary);
      }
      pre {
        background: #0b0f19;
        color: #f8fafc;
        border: 1px solid var(--border);
        padding: 20px;
        border-radius: 8px;
        overflow: auto;
        font-family: 'Fira Code', monospace;
        font-size: 0.9rem;
        white-space: pre-wrap;
        word-break: break-word;
      }
      .product-item {
        border-left: 3px solid var(--primary);
        padding-left: 16px;
        margin: 16px 0;
      }
      .product-name a {
        font-weight: 600;
        font-size: 1.1rem;
        color: var(--primary);
        text-decoration: none;
      }
      .product-name a:hover {
        text-decoration: underline;
      }
      .product-price {
        font-weight: 700;
        color: var(--success);
        font-size: 0.95rem;
      }
      .keyword-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.1);
        color: var(--primary);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
      }
      .controls-btn {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--text);
        margin-right: 12px;
      }
      .controls-btn:hover {
        background: rgba(255,255,255,0.04);
      }
    </style>
  </head>
  <body>
    __SHARED_HEADER__
    
    <h1>ContentEngine Pro</h1>
    <p class="subtitle" style="color:var(--text-secondary);">Scrape trending marketplaces, analyze SEO keywords, and draft professional copy using state-of-the-art AI.</p>

    <div class="card">
      <label for="prod">Product Keyword</label>
      <input type="text" id="prod" value="smart watch">
      <div style="margin-top:14px">
        <button id="go">Create Blog Post</button>
      </div>
    </div>

    <div id="result"></div>

    <script>
      document.getElementById("nav-t2").classList.add("active");
      
      function renderResult(data){
        const r = document.getElementById('result');
        r.innerHTML = '';

        // Products Section
        const prodCard = document.createElement('div');
        prodCard.className = 'card';
        prodCard.innerHTML = '<h2>🛍️ Scraped Products</h2>' + data.products.map(p => `
          <div class="product-item">
            <div class="product-name"><a href="${p.link}" target="_blank">${p.title}</a></div>
            <div class="product-price">${p.price}</div>
          </div>
        `).join('');
        r.appendChild(prodCard);

        // Keywords Section
        const kwCard = document.createElement('div');
        kwCard.className = 'card';
        kwCard.innerHTML = '<h2>🔑 Target SEO Keywords</h2>' + data.keywords.map(k => `
          <span class="keyword-badge">${k}</span>
        `).join('');
        r.appendChild(kwCard);

        // Blog Section
        const blogCard = document.createElement('div');
        blogCard.className = 'card';
        blogCard.innerHTML = '<h2>📝 Generated Blog Post</h2><pre>' + data.blog + '</pre>';
        r.appendChild(blogCard);

        // Controls Section
        const controls = document.createElement('div');
        controls.style.marginTop = '16px';
        
        const copyBtn = document.createElement('button');
        copyBtn.textContent = 'Copy Markdown';
        copyBtn.className = 'controls-btn';
        copyBtn.onclick = () => {
          navigator.clipboard.writeText(data.blog).then(() => alert('Markdown copied to clipboard'));
        };
        controls.appendChild(copyBtn);

        const dlBtn = document.createElement('button');
        dlBtn.textContent = 'Download Markdown';
        dlBtn.onclick = () => {
          const blob = new Blob([data.blog], {type: 'text/markdown'});
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = data.product.toLowerCase().replace(/\\s+/g, '-') + '.md';
          a.click();
          URL.revokeObjectURL(url);
        };
        controls.appendChild(dlBtn);

        r.appendChild(controls);
      }

      document.getElementById('go').addEventListener('click', async ()=>{
        const prod = document.getElementById('prod').value;
        document.getElementById('result').innerHTML = '<div class="card"><em>Searching listings, discovering Google search suggestions, and drafting product review...</em></div>';
        try{
          const apiBase = window.location.origin;
          const resp = await fetch(`${apiBase}/api/task2/generate`, {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({product:prod})
          });
          if(!resp.ok){
            const txt = await resp.text();
            document.getElementById('result').innerHTML = `<div class="card">Error ${resp.status}: ${txt}</div>`;
            return;
          }
          const data = await resp.json();
          renderResult(data);
        }catch(e){
          document.getElementById('result').innerHTML = `<div class="card">Error: ${e}</div>`;
        }
      });
    </script>
  </body>
</html>
"""

# -------------------------------------------------------------
# TASK 3: ARCHITECTURE SPECS HTML
# -------------------------------------------------------------
HTML_CONTENT = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>DevSpec Studio — Architecture Pipeline</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
      __SHARED_NAV_STYLE__
      
      p.subtitle {
        color: var(--text-secondary);
        font-size: 1.1rem;
        margin-top: 0;
        margin-bottom: 32px;
      }
      label {
        font-weight: 500;
        font-size: 0.95rem;
        color: var(--text-secondary);
        display: block;
        margin-bottom: 10px;
      }
      textarea {
        width: 100%;
        min-height: 120px;
        padding: 14px;
        border-radius: 8px;
        border: 1px solid var(--border);
        background: rgba(10, 15, 25, 0.8);
        color: var(--text);
        font-family: inherit;
        font-size: 1rem;
        resize: vertical;
        box-sizing: border-box;
        transition: border-color 0.2s;
      }
      textarea:focus {
        outline: none;
        border-color: var(--primary);
      }
      pre {
        background: rgba(10, 15, 25, 0.8);
        border: 1px solid var(--border);
        padding: 16px;
        border-radius: 8px;
        overflow: auto;
        font-family: 'Fira Code', monospace;
        font-size: 0.9rem;
        color: #e5e7eb;
      }
      .module-item {
        border-left: 3px solid var(--primary);
        padding-left: 16px;
        margin: 16px 0;
      }
      .module-name {
        font-weight: 600;
        font-size: 1.1rem;
        color: #818cf8;
      }
      .module-purpose {
        color: var(--text-secondary);
        font-size: 0.95rem;
      }
      .module-tech {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        color: var(--success);
        font-size: 0.9rem;
      }
      .controls-btn {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--text);
        margin-right: 12px;
      }
      .controls-btn:hover {
        background: rgba(255,255,255,0.04);
      }
    </style>
  </head>
  <body>
    __SHARED_HEADER__
    
    <h1>DevSpec Studio</h1>
    <p class="subtitle" style="color:var(--text-secondary);">Convert high-level business requirements into low-level technical specifications instantly.</p>

    <div class="card">
      <label for="req">Business requirement</label>
      <textarea id="req">Small web app for products, orders, and payments with user auth</textarea>
      <div style="margin-top:14px">
        <button id="go">Generate Architecture Spec</button>
      </div>
    </div>

    <div id="result"></div>

    <script>
      document.getElementById("nav-t3").classList.add("active");
      
      async function renderResult(data){
        const r = document.getElementById('result');
        r.innerHTML = '';

        if (!data || data.raw || (!data.modules && !data.schemas && !data.pseudocode)) {
          const rawCard = document.createElement('div'); rawCard.className = 'card';
          rawCard.innerHTML = `<h3>Specification Output</h3><pre style="white-space:pre-wrap;word-break:break-word;">${data && data.raw ? data.raw : JSON.stringify(data, null, 2)}</pre>`;
          r.appendChild(rawCard);
          return;
        }

        const intro = document.createElement('div'); intro.className='card';
        intro.innerHTML = '<h3>Result Specification</h3><p>Below are the inferred architectural modules, database schemas, and pseudocode flows.</p>';
        r.appendChild(intro);

        // override logic
        const reqText = (document.getElementById('req')||{value:''}).value.toLowerCase();
        const modulesData = (data.modules||[]).map(m => ({...m}));
        let overrideTech = null;
        if (reqText.includes('react native') || reqText.includes('react-native')) overrideTech = 'React Native';
        else if (reqText.includes('flutter') || reqText.includes('dart')) overrideTech = 'Flutter (Dart)';
        else if (reqText.includes('android') || reqText.includes('kotlin') || reqText.includes('java')) overrideTech = 'Android (Kotlin/Java)';
        else if (reqText.includes('ios') || reqText.includes('swift') || reqText.includes('objective-c')) overrideTech = 'iOS (Swift)';
        else if (reqText.includes('mobile')) overrideTech = 'Mobile (React Native / Flutter)';
        if (overrideTech) {
          let found=false;
          for (let m of modulesData) {
            if (m.name && m.name.toLowerCase()==='frontend') { m.tech = overrideTech; found=true; break; }
          }
          if (!found) modulesData.unshift({name:'frontend', purpose:'User interface', tech:overrideTech});
        }
        
        if (modulesData.length > 0) {
          const modules = document.createElement('div'); modules.className='card';
          modules.innerHTML = '<h2>System Modules</h2>' + modulesData.map(m=>`
            <div class="module-item">
              <div class="module-name">${m.name || 'Unnamed Module'}</div>
              <div class="module-purpose">${m.purpose || 'No purpose defined.'}</div>
              <div class="module-tech">Technology Stack: ${Array.isArray(m.tech) ? m.tech.join(', ') : (m.tech || 'Not specified')}</div>
            </div>
          `).join('');
          r.appendChild(modules);
        }

        const schemasData = data.schemas || {};
        if (Object.keys(schemasData).length > 0) {
          const schemas = document.createElement('div'); schemas.className='card';
          schemas.innerHTML = '<h2>Database Schema Specifications</h2>' + Object.keys(schemasData).map(k=>`<h4>Entity: ${k}</h4><pre>${JSON.stringify(schemasData[k],null,2)}</pre>`).join('');
          r.appendChild(schemas);
        }

        const pseudoData = data.pseudocode || {};
        if (Object.keys(pseudoData).length > 0) {
          const pseudo = document.createElement('div'); pseudo.className='card';
          pseudo.innerHTML = '<h2>Process Flow Pseudocode</h2>' + Object.keys(pseudoData).map(k=>`<h4>Flow: ${k}</h4><pre>${Array.isArray(pseudoData[k]) ? pseudoData[k].join('\\n') : pseudoData[k]}</pre>`).join('');
          r.appendChild(pseudo);
        }

        if (data.notes) {
          const notesCard = document.createElement('div'); notesCard.className='card';
          notesCard.innerHTML = '<h2>Additional Notes</h2>' + (Array.isArray(data.notes) ? `<ul>${data.notes.map(n=>`<li>${n}</li>`).join('')}</ul>` : `<p>${data.notes}</p>`);
          r.appendChild(notesCard);
        }

        const controls = document.createElement('div'); controls.style.marginTop='16px';
        
        const jsonBtn = document.createElement('button'); 
        jsonBtn.textContent='Copy Specification JSON'; 
        jsonBtn.className='controls-btn';
        jsonBtn.onclick = ()=>{ navigator.clipboard.writeText(JSON.stringify(data,null,2)).then(()=>alert('Specification JSON copied to clipboard')); };
        controls.appendChild(jsonBtn);

        const mdBtn = document.createElement('button'); 
        mdBtn.textContent='Export Markdown Spec';
        mdBtn.onclick = ()=>{
          const mdParts = [];
          if (data.modules) {
            mdParts.push('### Modules\\n');
            mdParts.push(data.modules.map(m=>`- **${m.name || 'Unnamed Module'}**: ${m.purpose || ''} — *${Array.isArray(m.tech) ? m.tech.join(', ') : (m.tech || '')}*`).join('\\n'));
          }
          if (data.schemas) {
            mdParts.push('\\n\\n### Schemas\\n');
            for(const k of Object.keys(data.schemas)){
              mdParts.push('#### '+k+'\\n```json\\n'+JSON.stringify(data.schemas[k],null,2)+'\\n```');
            }
          }
          if (data.pseudocode) {
            mdParts.push('\\n\\n### Pseudocode\\n');
            for(const k of Object.keys(data.pseudocode)){
              mdParts.push('#### '+k+'\\n```\\n'+(Array.isArray(data.pseudocode[k]) ? data.pseudocode[k].join('\\n') : data.pseudocode[k])+'\\n```');
            }
          }
          if (data.notes) {
            mdParts.push('\\n\\n### Notes\\n');
            mdParts.push(Array.isArray(data.notes) ? data.notes.map(n=>`- ${n}`).join('\\n') : data.notes);
          }
          const blob = new Blob([mdParts.join('\\n\\n')], {type:'text/markdown'});
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a'); a.href=url; a.download='architecture_spec.md'; a.click();
          URL.revokeObjectURL(url);
        };
        controls.appendChild(mdBtn);

        r.appendChild(controls);
      }

      document.getElementById('go').addEventListener('click', async ()=>{
        const req = document.getElementById('req').value;
        document.getElementById('result').innerHTML = '<div class="card"><em>Analyzing requirements and compiling system architecture specifications...</em></div>';
        try{
          const apiBase = window.location.origin;
          const resp = await fetch(`${apiBase}/api/generate`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({requirements:req})});
          if(!resp.ok){ const txt = await resp.text(); document.getElementById('result').innerHTML = `<div class="card">Error ${resp.status}: ${txt}</div>`; return; }
          const data = await resp.json();
          renderResult(data);
        }catch(e){
          document.getElementById('result').innerHTML = `<div class="card">Error: ${e}</div>`;
        }
      });
    </script>
  </body>
</html>
"""

# -------------------------------------------------------------
# ROUTING & ENDPOINTS
# -------------------------------------------------------------
@app.get('/', response_class=HTMLResponse)
def ui_index():
    # Inject variables statically to prevent f-string issues with JavaScript braces
    content = HTML_CONTENT.replace("__SHARED_NAV_STYLE__", SHARED_NAV_STYLE).replace("__SHARED_HEADER__", SHARED_HEADER)
    return HTMLResponse(content=content, status_code=200)

@app.get('/task1', response_class=HTMLResponse)
def ui_task1():
    content = HTML_CONTENT_TASK1.replace("__SHARED_NAV_STYLE__", SHARED_NAV_STYLE).replace("__SHARED_HEADER__", SHARED_HEADER)
    return HTMLResponse(content=content, status_code=200)

@app.get('/task2', response_class=HTMLResponse)
def ui_task2():
    content = HTML_CONTENT_TASK2.replace("__SHARED_NAV_STYLE__", SHARED_NAV_STYLE).replace("__SHARED_HEADER__", SHARED_HEADER)
    return HTMLResponse(content=content, status_code=200)

# -------------------------------------------------------------
# TASK 1: API REQUEST SCHEMAS & LOGIC
# -------------------------------------------------------------
class Task1Request(BaseModel):
    topic: str
    voice: str
    context: str = ""

@app.get('/api/task1/scrape-news')
def api_task1_scrape_news():
    if not get_trending_news:
        return {"error": "Video news scraper not available."}
    try:
        articles = get_trending_news(6)
        return {"articles": articles}
    except Exception as e:
        return {"error": str(e), "articles": []}

@app.post('/api/task1/generate')
def api_task1_generate(payload: Task1Request):
    if not generate_script or not get_scene_image_url or not generate_voiceover_base64:
        return {"error": "Video generator modules not loaded properly on the server."}
        
    topic = payload.topic.strip()
    if not topic:
        return {"error": "Topic cannot be empty."}
        
    try:
        # 1. Script storyboard via Gemini
        script_data = generate_script(topic, payload.context)
        title = script_data.get("title", "AI Short Video")
        scenes = script_data.get("scenes", [])
        
        # 2. Get assets and voiceovers
        res_scenes = []
        for scene in scenes:
            scene_num = scene.get("scene_num", 1)
            narration = scene.get("narration", "")
            visual_prompt = scene.get("visual_prompt", "news")
            overlay_text = scene.get("overlay_text", "")
            
            # Fetch public image link
            img_url = get_scene_image_url(visual_prompt, scene_num)
            
            # Speak narration into base64 speech
            audio_b64 = generate_voiceover_base64(narration, voice=payload.voice)
            
            res_scenes.append({
                "scene_num": scene_num,
                "narration": narration,
                "overlay_text": overlay_text,
                "image_url": img_url,
                "audio_base64": audio_b64
            })
            
        return {
            "title": title,
            "scenes": res_scenes
        }
    except Exception as e:
        return {"error": f"Failed compiling virtual video storyboard: {e}"}

# -------------------------------------------------------------
# TASK 2: API REQUEST SCHEMAS & LOGIC
# -------------------------------------------------------------
class Task2Request(BaseModel):
    product: str

@app.post('/api/task2/generate')
def api_task2_generate(payload: Task2Request):
    if not scrape_products or not select_seo_keywords or not generate_blog:
        return {"error": "Task 2 modules not loaded correctly."}
        
    products = scrape_products(payload.product)
    keywords = select_seo_keywords(payload.product)
    
    import tempfile
    tmpdir = tempfile.gettempdir()
    fn = generate_blog(payload.product, tmpdir, products=products, keywords=keywords)
    
    with open(fn, 'r', encoding='utf-8') as f:
        blog_content = f.read()
        
    return {
        "product": payload.product,
        "products": products,
        "keywords": keywords,
        "blog": blog_content
    }

# -------------------------------------------------------------
# TASK 3: API REQUEST SCHEMAS & LOGIC
# -------------------------------------------------------------
class GenerateRequest(BaseModel):
    requirements: str

@app.get('/generate')
def generate(q: str = 'hello'):
    return {'message': f'This is a placeholder generate endpoint. q={q}'}

@app.post('/api/generate')
def api_generate(payload: GenerateRequest):
    import os
    try:
        try:
            from src.gemini_client import generate_plan_with_gemini
        except ImportError:
            from task3_architecture_pipeline.src.gemini_client import generate_plan_with_gemini
    except Exception:
        generate_plan_with_gemini = None

    def _adjust_frontend_for_platform(requirements: str, res: dict) -> dict:
        req = requirements.lower()
        frontend_tech = None
        if 'react native' in req or 'react-native' in req:
            frontend_tech = 'React Native'
        elif 'flutter' in req or 'dart' in req:
            frontend_tech = 'Flutter (Dart)'
        elif 'android' in req or 'kotlin' in req or 'java ' in req:
            frontend_tech = 'Android (Kotlin/Java)'
        elif 'ios' in req or 'swift' in req or 'objective-c' in req:
            frontend_tech = 'iOS (Swift)'
        elif 'mobile' in req:
            frontend_tech = 'Mobile (React Native / Flutter)'

        if frontend_tech:
            modules = res.get('modules') or []
            found = False
            for m in modules:
                if m.get('name') == 'frontend':
                    m['tech'] = frontend_tech
                    found = True
                    break
            if not found:
                modules.insert(0, {'name': 'frontend', 'purpose': 'User interface', 'tech': frontend_tech})
            res['modules'] = modules
        return res

    # Try Gemini
    if os.getenv('GEMINI_API_KEY') and generate_plan_with_gemini:
        try:
            res = generate_plan_with_gemini(payload.requirements)
            if isinstance(res, dict):
                res = _adjust_frontend_for_platform(payload.requirements, res)
                return res
            if isinstance(res, str):
                try:
                    import json
                    parsed = json.loads(res)
                    parsed = _adjust_frontend_for_platform(payload.requirements, parsed)
                    return parsed
                except Exception:
                    return {"title": "Gemini raw response", "raw": res}
        except Exception:
            pass

    # Local fallback
    res = analyze_requirements(payload.requirements)
    res = _adjust_frontend_for_platform(payload.requirements, res)
    return res

def analyze_requirements(req: str) -> Dict[str, Any]:
    req = req.strip()
    keywords = ['user','product','order','payment','auth','image','video','comment','review','profile','search']
    entities = []
    for k in keywords:
        if re.search(r'\b'+k+r"s?\b", req, re.I):
            entities.append(k)
    if not entities:
        entities = ['item']

    modules = [
        {"name":"frontend","purpose":"User interface","tech":"React (Vercel)"},
        {"name":"api","purpose":"Business logic & API","tech":"FastAPI"},
        {"name":"database","purpose":"Primary relational data store","tech":"Postgres"}
    ]
    if 'auth' in entities or 'auth' in req.lower():
        modules.append({"name":"auth","purpose":"Authentication/Authorization","tech":"JWT / OAuth2"})
    if 'image' in entities or 'video' in entities:
        modules.append({"name":"storage","purpose":"Blob storage for media","tech":"S3-compatible"})
    if 'order' in entities or 'payment' in entities:
        modules.append({"name":"payments","purpose":"Payment processing","tech":"Stripe / Payment gateway"})

    schemas: Dict[str, Dict[str, str]] = {}
    for e in set(entities):
        if e=='user':
            schemas['user'] = {"id":"uuid","email":"string","name":"string","password_hash":"string","created_at":"timestamp"}
        elif e=='product':
            schemas['product'] = {"id":"uuid","name":"string","description":"text","price":"decimal","created_at":"timestamp"}
        elif e=='order':
            schemas['order'] = {"id":"uuid","user_id":"uuid","total":"decimal","status":"string","created_at":"timestamp"}
        elif e=='payment':
            schemas['payment'] = {"id":"uuid","order_id":"uuid","amount":"decimal","provider":"string","status":"string","created_at":"timestamp"}
        elif e=='image':
            schemas['image'] = {"id":"uuid","url":"string","owner_id":"uuid","metadata":"json","created_at":"timestamp"}
        elif e=='video':
            schemas['video'] = {"id":"uuid","url":"string","title":"string","duration_seconds":"int","created_at":"timestamp"}
        elif e=='comment':
            schemas['comment'] = {"id":"uuid","user_id":"uuid","content":"text","created_at":"timestamp","parent_id":"uuid?"}
        elif e=='review':
            schemas['review'] = {"id":"uuid","product_id":"uuid","user_id":"uuid","rating":"int","content":"text","created_at":"timestamp"}
        else:
            schemas[e] = {"id":"uuid","name":"string","created_at":"timestamp"}

    pseudocode = {
        "user_signup": [
            "POST /api/signup -> validate payload",
            "hash password and store user",
            "return JWT"
        ],
        "create_product": [
            "POST /api/products -> auth required",
            "validate product payload",
            "insert into products table",
            "return product id"
        ],
        "place_order": [
            "POST /api/orders -> auth required",
            "create order row with status 'pending'",
            "create payment intent with provider",
            "on success update order status to 'paid'"
        ]
    }

    plan = {
        "title": f"Architecture plan for: {req[:80]}",
        "modules": modules,
        "schemas": schemas,
        "pseudocode": pseudocode,
        "notes": f"Starter architecture derived from: {req}"
    }
    return plan

@app.post('/generate')
def generate_post(payload: GenerateRequest):
    return analyze_requirements(payload.requirements)
