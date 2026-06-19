import asyncio
import edge_tts
import base64
import os
import tempfile
from pathlib import Path

async def _generate_audio_async(text: str, out_path: str, voice: str) -> None:
    """Invoke edge-tts to generate voiceover file."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)

def generate_voiceover_base64(text: str, voice: str = "en-US-JennyNeural") -> str:
    """Generate speech using edge-tts, base64 encode it, and clean up the temporary file.
    Returns data-uri string format ready for browser playback.
    """
    # Create temporary path
    fd, temp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    
    cleaned_text = text.replace('\n', ' ').strip()
    try:
        # Run async loop to generate audio file
        asyncio.run(_generate_audio_async(cleaned_text, temp_path, voice))
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            with open(temp_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:audio/mp3;base64,{encoded}"
    except Exception as e:
        print(f"[video_tts] TTS failed on server: {e}")
    finally:
        # Guarantee cleanup
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
    return ""
