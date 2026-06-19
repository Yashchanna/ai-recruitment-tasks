import streamlit as st
import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Dynamically refresh Windows PATH inside current session to pick up newly installed winget dependencies (FFmpeg)
try:
    path_result = subprocess.run(
        ["powershell", "-Command", "[System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')"],
        capture_output=True,
        text=True,
        check=True
    )
    if path_result.stdout.strip():
        os.environ["PATH"] = path_result.stdout.strip()
except Exception as e:
    st.warning(f"Path refresh warning: {e}")

# Set paths
workspace_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(workspace_root))
load_dotenv(workspace_root / '.env')

from task1_video_generator.src.scraper import get_trending_news
from task1_video_generator.src.script_gen import generate_script
from task1_video_generator.src.asset_fetcher import fetch_scene_image
from task1_video_generator.src.tts import generate_voiceover
from task1_video_generator.src.video_builder import build_video_from_scenes

# UI Configuration
st.set_page_config(
    page_title="ViralReels AI — Video Generator Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium UI CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 3rem;
        background: linear-gradient(135deg, #a78bfa 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    
    .subtitle {
        color: #64748b;
        font-size: 1.15rem;
        margin-bottom: 30px;
    }
    
    .section-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .section-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }
    
    .news-badge {
        background-color: #f1f5f9;
        color: #475569;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .news-card-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: #1e293b;
        margin-top: 8px;
        margin-bottom: 6px;
    }
    
    .news-card-desc {
        color: #475569;
        font-size: 0.9rem;
        margin-bottom: 12px;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar settings
st.sidebar.markdown("<h2 style='font-family:Outfit; font-weight:700;'>⚙️ Video Settings</h2>", unsafe_allow_html=True)

tts_voice = st.sidebar.selectbox(
    "Narration Voice (Edge TTS)",
    options=[
        "en-US-JennyNeural (US Female - Clear & Conversational)",
        "en-US-GuyNeural (US Male - Professional)",
        "en-US-AriaNeural (US Female - News Reporter Style)",
        "en-US-ChristopherNeural (US Male - Warm)",
        "en-GB-SoniaNeural (UK Female)",
        "en-GB-RyanNeural (UK Male)"
    ],
    index=0
)
voice_id = tts_voice.split(" ")[0]

out_directory = st.sidebar.text_input("Output Directory", value="./task1_video_generator/output/")

# Load API Key indicators
gemini_key_ok = bool(os.getenv("GEMINI_API_KEY"))
pexels_key_ok = bool(os.getenv("PEXELS_API_KEY") and not os.getenv("PEXELS_API_KEY").startswith("your_"))

st.sidebar.markdown("### 🔑 API Key Status")
if gemini_key_ok:
    st.sidebar.success("Gemini API: Connected")
else:
    st.sidebar.error("Gemini API: Missing (Using local fallback script maker)")
    
if pexels_key_ok:
    st.sidebar.success("Pexels API: Connected")
else:
    st.sidebar.info("Pexels API: Off (Using Unsplash fallback)")

# Main Layout
st.markdown("<h1 class='main-title'>🎬 ViralReels AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Scrape viral news stories, auto-write production scripts, and generate high-impact social media short videos in seconds.</p>", unsafe_allow_html=True)

# Session state initialization
if "selected_headline" not in st.session_state:
    st.session_state.selected_headline = ""
if "selected_context" not in st.session_state:
    st.session_state.selected_context = ""

col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("<h3 style='font-family:Outfit;'>📰 Step 1: Select Trending Topic</h3>", unsafe_allow_html=True)
    
    # Load news action
    if st.button("🔄 Scrape Latest Trending News"):
        with st.spinner("Fetching trending RSS articles..."):
            try:
                st.session_state.news_articles = get_trending_news(6)
            except Exception as e:
                st.error(f"Failed to fetch news: {e}")
                
    articles = st.session_state.get("news_articles", [])
    
    if articles:
        # Display articles in 2-column card grid
        grid_cols = st.columns(2)
        for idx, art in enumerate(articles):
            col_target = grid_cols[idx % 2]
            with col_target:
                # Wrap each card cleanly
                st.markdown(f"""
                <div class='section-card'>
                    <span class='news-badge'>Trending #{idx+1}</span>
                    <div class='news-card-title'>{art['title']}</div>
                    <div class='news-card-desc'>{art['summary'][:150]}...</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Button to select
                if st.button(f"Use Article #{idx+1}", key=f"select_art_{idx}"):
                    st.session_state.selected_headline = art['title']
                    st.session_state.selected_context = art['summary']
                    st.success(f"Selected Article: {art['title']}")
                    
    # Custom query fallback
    st.markdown("<h4 style='margin-top:20px; font-family:Outfit;'>Or type a custom topic or keyword:</h4>", unsafe_allow_html=True)
    custom_topic = st.text_input(
        "Enter custom topic/news idea",
        value=st.session_state.selected_headline if st.session_state.selected_headline else "Artificial Intelligence breakthroughs in 2026"
    )
    
    # Run Generation Button
    st.markdown("---")
    generate_clicked = st.button("🚀 Generate AI Short Video", type="primary")

with col_right:
    st.markdown("<h3 style='font-family:Outfit;'>🎥 Generated Output</h3>", unsafe_allow_html=True)
    
    if generate_clicked:
        out_path = Path(out_directory)
        out_path.mkdir(parents=True, exist_ok=True)
        
        topic_to_use = custom_topic if custom_topic else st.session_state.selected_headline
        context_to_use = st.session_state.selected_context if custom_topic == st.session_state.selected_headline else ""
        
        # 1. Script writing progress
        progress_bar = st.progress(10)
        status_text = st.empty()
        
        status_text.write("🤖 Writing scene-by-scene script with Gemini...")
        try:
            script_data = generate_script(topic_to_use, context_to_use)
            title = script_data.get("title", "AI Video")
            scenes = script_data.get("scenes", [])
            progress_bar.progress(30)
            
            st.info(f"**Video Title:** {title}")
            
            # Show script preview
            with st.expander("📄 View Detailed Scene Script"):
                for s in scenes:
                    st.markdown(f"**Scene {s['scene_num']}**: *{s['narration']}*")
                    st.markdown(f"- Visual Prompt: `{s['visual_prompt']}`")
                    st.markdown(f"- Screen Text: `{s['overlay_text']}`")
                    st.markdown("---")
                    
        except Exception as e:
            st.error(f"Script creation failed: {e}")
            st.stop()
            
        # 2. Asset Sourcing & voice narration
        status_text.write("📸 Downloading visual stock images and generating speech voiceovers...")
        scene_assets = []
        
        for idx, scene in enumerate(scenes):
            scene_num = scene.get("scene_num", idx + 1)
            narration = scene.get("narration", "")
            visual_prompt = scene.get("visual_prompt", "news")
            overlay_text = scene.get("overlay_text", "")
            
            status_text.write(f"⏳ Downloading matching visuals and voicing Scene {scene_num}/{len(scenes)}...")
            
            # Fetch scene image
            image_path = fetch_scene_image(visual_prompt, out_path / "temp_assets", scene_num)
            
            # Generate speech
            audio_path = out_path / "temp_assets" / f"scene_{scene_num}.mp3"
            generate_voiceover(narration, str(audio_path), voice=voice_id)
            
            if image_path.exists() and audio_path.exists():
                scene_assets.append({
                    "image_path": str(image_path),
                    "audio_path": str(audio_path),
                    "overlay_text": overlay_text
                })
                
        progress_bar.progress(60)
        
        # 3. Compile MoviePy Video
        status_text.write("🎬 Assembling scenes and writing output MP4 video file...")
        clean_title = "".join([c if c.isalnum() else "_" for c in title]).strip("_")[:30]
        final_video_name = out_path / f"video_{clean_title}.mp4"
        
        try:
            build_video_from_scenes(scene_assets, str(final_video_name))
            progress_bar.progress(100)
            status_text.success("🎉 Video generated successfully!")
            
            # Show video player
            st.video(str(final_video_name))
            
            # Download button
            with open(final_video_name, "rb") as f:
                st.download_button(
                    label="💾 Download Output MP4 Video",
                    data=f,
                    file_name=final_video_name.name,
                    mime="video/mp4"
                )
        except Exception as e:
            st.error(f"MoviePy assembly failed: {e}")
            st.write("Ensure FFmpeg is installed and added to the PATH.")
            
        finally:
            # Cleanup temp assets
            status_text.write("🧹 Cleaning up scene caches...")
            for asset in scene_assets:
                try:
                    Path(asset["image_path"]).unlink(missing_ok=True)
                    Path(asset["audio_path"]).unlink(missing_ok=True)
                except Exception:
                    pass
            try:
                Path(out_path / "temp_assets").rmdir()
            except Exception:
                pass
            status_text.success("🎉 Video generated successfully!")
    else:
        st.info("Select a trending story or write a custom topic on the left and click 'Generate AI Short Video' to build.")
