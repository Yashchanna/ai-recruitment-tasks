import asyncio
import edge_tts
from pathlib import Path

async def _generate_audio_async(text: str, out_path: str, voice: str) -> None:
    """Invokes edge-tts library to perform text-to-speech rendering."""
    # Create the communication object
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)

def generate_voiceover(text: str, out_file: str, voice: str = "en-US-JennyNeural") -> str:
    """Uses free Edge TTS service via edge-tts to generate realistic voice narration.
    Returns path of generated audio file or None if it failed.
    """
    out_p = Path(out_file)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    
    # We clean the text slightly to avoid speech hiccups
    cleaned_text = text.replace('\n', ' ').strip()
    
    try:
        print(f"[tts] Speaking (Voice: {voice}): '{cleaned_text[:60]}...'")
        asyncio.run(_generate_audio_async(cleaned_text, str(out_p), voice))
        if out_p.exists() and out_p.stat().st_size > 0:
            print(f"[tts] Audio saved successfully to: {out_p}")
            return str(out_p)
    except Exception as e:
        print(f"[tts] Text to speech failed: {e}")
        
    return None

if __name__ == "__main__":
    # Test TTS output
    import tempfile
    test_out = Path(tempfile.gettempdir()) / "test_tts.mp3"
    res = generate_voiceover("Welcome to the AI Video Generation Tool demonstration.", str(test_out))
    print(f"Result: {res}")
