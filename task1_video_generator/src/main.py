import os
import argparse
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
    print(f"[main] Path refresh warning: {e}")

# Load environment variables from workspace root .env
workspace_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(workspace_root / '.env')

from task1_video_generator.src.scraper import get_trending_news
from task1_video_generator.src.script_gen import generate_script
from task1_video_generator.src.asset_fetcher import fetch_scene_image
from task1_video_generator.src.tts import generate_voiceover
from task1_video_generator.src.video_builder import build_video_from_scenes

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--topic", help="Topic to generate video. If omitted, uses top trending news.", default=None)
    p.add_argument("--voice", help="Edge TTS Voice name", default="en-US-JennyNeural")
    p.add_argument("--output", help="Output folder", default="./task1_video_generator/output/")
    args = p.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    topic = args.topic
    context = ""

    # Step 1: Scrape trending news if no topic provided
    if not topic:
        print("[task1] No topic provided. Fetching trending news articles...")
        try:
            articles = get_trending_news(5)
            if articles:
                # Pick the top story
                top_story = articles[0]
                topic = top_story["title"]
                context = top_story["summary"]
                print(f"[task1] Selected top trending news: '{topic}'")
            else:
                topic = "Artificial Intelligence breakthroughs"
                print(f"[task1] No articles found. Using fallback topic: '{topic}'")
        except Exception as e:
            topic = "Artificial Intelligence breakthroughs"
            print(f"[task1] Scraper error: {e}. Using fallback topic: '{topic}'")
    else:
        print(f"[task1] Generating video for user-defined topic: '{topic}'")

    # Step 2: Generate the Scene-by-Scene Script using Gemini or fallback
    print("[task1] Generating video script...")
    script_data = generate_script(topic, context)
    title = script_data.get("title", "AI News Update")
    scenes = script_data.get("scenes", [])
    
    print(f"\n[task1] Script Ready! Video Title: '{title}'")
    print(f"[task1] Total scenes to process: {len(scenes)}")

    # Step 3: Fetch assets and voiceovers for each scene
    scene_assets = []
    
    for idx, scene in enumerate(scenes):
        scene_num = scene.get("scene_num", idx + 1)
        narration = scene.get("narration", "")
        visual_prompt = scene.get("visual_prompt", "news")
        overlay_text = scene.get("overlay_text", "")
        
        print(f"\n--- Processing Scene {scene_num}/{len(scenes)} ---")
        
        # Download matching stock image
        image_path = fetch_scene_image(visual_prompt, out_dir / "temp_assets", scene_num)
        
        # Generate Edge TTS Voice narration MP3
        audio_path = out_dir / "temp_assets" / f"scene_{scene_num}.mp3"
        generate_voiceover(narration, str(audio_path), voice=args.voice)
        
        if image_path.exists() and audio_path.exists():
            scene_assets.append({
                "image_path": str(image_path),
                "audio_path": str(audio_path),
                "overlay_text": overlay_text
            })
        else:
            print(f"[task1] Warning: Skipping scene {scene_num} due to missing assets.")

    # Step 4: Compile scenes using MoviePy into a high-quality vertical MP4
    if not scene_assets:
        print("[task1] Error: No valid scenes could be built. Aborting.")
        return

    print("\n[task1] Compiling scenes and rendering final video...")
    final_video_name = out_dir / f"generated_video_{Path(image_path).stem}.mp4"
    # Fallback name if title is messy
    clean_title = "".join([c if c.isalnum() else "_" for c in title]).strip("_")[:30]
    final_video_name = out_dir / f"video_{clean_title}.mp4"
    
    try:
        build_video_from_scenes(scene_assets, str(final_video_name))
        print(f"\n[task1] Success! Deployed AI Video file: {final_video_name.resolve()}")
    except Exception as e:
        print(f"[task1] Rendering failed: {e}")

    # Clean up scene-specific temporary assets
    print("[task1] Cleaning up temporary scene assets...")
    for asset in scene_assets:
        try:
            Path(asset["image_path"]).unlink(missing_ok=True)
            Path(asset["audio_path"]).unlink(missing_ok=True)
        except Exception:
            pass
    try:
        Path(out_dir / "temp_assets").rmdir()
    except Exception:
        pass

if __name__ == "__main__":
    main()
