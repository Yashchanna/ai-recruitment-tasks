import os
import math
from pathlib import Path
from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

def load_font(size: int) -> ImageFont.ImageFont:
    """Safely load a font from the system, falling back to default if unavailable."""
    font_names = ["arialbd.ttf", "arial.ttf", "calibrib.ttf", "calibri.ttf", "segoeuib.ttf"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
            
    # Check absolute windows font folder
    paths = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\Calibrib.ttf",
        r"C:\Windows\Fonts\Calibri.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
                
    return ImageFont.load_default()

def resize_and_crop(image_path: Path, target_w: int = 1080, target_h: int = 1920) -> Image.Image:
    """Crop and resize image from center to match target dimensions."""
    img = Image.open(image_path).convert('RGB')
    img_w, img_h = img.size
    
    img_ratio = img_w / img_h
    target_ratio = target_w / target_h
    
    if img_ratio > target_ratio:
        # Image is wider: crop sides
        new_w = int(img_h * target_ratio)
        left = (img_w - new_w) // 2
        right = left + new_w
        top = 0
        bottom = img_h
        img = img.crop((left, top, right, bottom))
    else:
        # Image is taller: crop top/bottom
        new_h = int(img_w / target_ratio)
        top = (img_h - new_h) // 2
        bottom = top + new_h
        left = 0
        right = img_w
        img = img.crop((left, top, right, bottom))
        
    return img.resize((target_w, target_h), Image.Resampling.LANCZOS)

def wrap_text(text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
    """Helper to split string into multiple lines that fit within max_width."""
    words = text.split()
    lines = []
    current_line = []
    
    # Simple dummy drawing object for text length measurement
    dummy_img = Image.new('RGB', (10, 10))
    draw = ImageDraw.Draw(dummy_img)
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        wbox = draw.textbbox((0, 0), test_line, font=font)
        line_w = wbox[2] - wbox[0]
        if line_w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                
    if current_line:
        lines.append(' '.join(current_line))
    return lines

def annotate_image(image_path: Path, text: str, output_path: Path) -> Path:
    """Crop image to portrait and draw a premium text overlay on the bottom."""
    # Resize and crop to 1080x1920 (TikTok/Shorts ratio)
    img = resize_and_crop(image_path, 1080, 1920)
    
    # Create overlay drawing context
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw_ol = ImageDraw.Draw(overlay)
    
    # Load fonts
    font_title = load_font(46)
    
    # Dimensions for text box
    box_margin = 60
    box_w = 1080 - (box_margin * 2)
    
    # Wrap text to fit inside the box
    lines = wrap_text(text.upper(), font_title, box_w - 40)
    
    # Calculate box height based on number of lines
    line_spacing = 15
    char_h = 50
    total_text_h = len(lines) * char_h + (len(lines) - 1) * line_spacing
    
    box_h = max(180, total_text_h + 50)
    box_y = 1920 - box_h - 150  # 150px safety margin at the bottom
    
    # Draw premium semi-transparent slate card
    draw_ol.rounded_rectangle(
        [box_margin, box_y, 1080 - box_margin, box_y + box_h],
        radius=24,
        fill=(15, 23, 42, 210),  # Dark Slate Blue with high opacity
        outline=(255, 255, 255, 30),
        width=2
    )
    
    # Draw text lines centered
    y_text = box_y + (box_h - total_text_h) // 2
    for line in lines:
        wbox = draw_ol.textbbox((0, 0), line, font=font_title)
        line_w = wbox[2] - wbox[0]
        x_text = 540 - (line_w // 2)
        
        # Draw text shadow
        draw_ol.text((x_text + 2, y_text + 2), line, fill=(0, 0, 0, 180), font=font_title)
        # Draw white text
        draw_ol.text((x_text, y_text), line, fill=(255, 255, 255, 255), font=font_title)
        y_text += char_h + line_spacing
        
    # Combine original image with overlay card
    combined = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    combined.save(output_path, 'JPEG', quality=95)
    return output_path

def build_video_from_scenes(scenes: List[Dict[str, str]], output_file: str) -> str:
    """Assembles video from list of scenes with image assets, narration audio, and text overlays.
    Returns path of final generated MP4.
    """
    out_p = Path(output_file)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    
    clips = []
    temp_files = []
    
    try:
        for idx, scene in enumerate(scenes):
            image_path = Path(scene["image_path"])
            audio_path = Path(scene["audio_path"])
            overlay_text = scene["overlay_text"]
            
            # Step 1: Generate annotated image frame
            temp_annotated = out_p.parent / f"temp_scene_{idx}_annotated.jpg"
            annotate_image(image_path, overlay_text, temp_annotated)
            temp_files.append(temp_annotated)
            
            # Step 2: Load audio clip to extract duration
            audio_clip = AudioFileClip(str(audio_path))
            duration = audio_clip.duration
            
            # Step 3: Create video clip from image synchronized with audio
            video_clip = ImageClip(str(temp_annotated)).with_duration(duration)
            video_clip = video_clip.with_audio(audio_clip)
            
            clips.append(video_clip)
            print(f"[video_builder] Scene {idx+1} built: {duration:.2f} seconds")
            
        print("[video_builder] Concatenating clips...")
        final_video = concatenate_videoclips(clips, method="compose")
        
        print(f"[video_builder] Exporting final video to {out_p}...")
        final_video.write_videofile(
            str(out_p),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            logger=None
        )
        
        # Close clips to release resources
        final_video.close()
        for c in clips:
            c.close()
            
    finally:
        # Clean up temporary frames
        for f in temp_files:
            if f.exists():
                try:
                    f.unlink()
                except Exception:
                    pass
                    
    return str(out_p)

if __name__ == "__main__":
    # Standard dummy test
    pass
