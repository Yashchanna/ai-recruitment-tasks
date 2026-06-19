import os
import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import urllib.parse

def fetch_scene_image(query: str, out_dir: Path, scene_num: int) -> Path:
    """Download a high-quality vertical stock image for a scene.
    First tries Pexels (if API key is present).
    Second tries public Unsplash search scraping.
    Falls back to Picsum generator if everything else fails.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"scene_{scene_num}.jpg"
    
    # Try Pexels first
    api_key = os.getenv("PEXELS_API_KEY", "").strip()
    img_url = None
    
    if api_key and not api_key.startswith("your_"):
        try:
            url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5"
            resp = requests.get(url, headers={"Authorization": api_key}, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                photos = data.get("photos") or []
                if photos:
                    # Pick an image, preferably portrait size if available, or just original
                    img_url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
                    print(f"[asset_fetcher] Found image on Pexels for '{query}'")
        except Exception as e:
            print(f"[asset_fetcher] Pexels check failed: {e}")
            
    # Try Unsplash Scraping second
    if not img_url:
        try:
            clean_query = query.replace("-", " ").strip()
            print(f"[asset_fetcher] Searching Unsplash for '{clean_query}'...")
            search_url = f"https://unsplash.com/s/photos/{urllib.parse.quote(clean_query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            resp = requests.get(search_url, headers=headers, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                img_tags = soup.find_all('img')
                for img in img_tags:
                    src = img.get('src', '')
                    if 'images.unsplash.com/photo-' in src and 'photo-' in src:
                        # Clean query parameters to get high quality size 1080x1920
                        base_url = src.split('?')[0]
                        img_url = f"{base_url}?auto=format&fit=crop&w=1080&h=1920&q=80"
                        print(f"[asset_fetcher] Found image on Unsplash for '{query}'")
                        break
        except Exception as e:
            print(f"[asset_fetcher] Unsplash scraping failed: {e}")

    # Fallback to Picsum
    if not img_url:
        # We append a random hash/number so it doesn't download the exact same image if query is similar
        rand_seed = abs(hash(query)) % 1000
        img_url = f"https://picsum.photos/1080/1920?random={rand_seed}"
        print(f"[asset_fetcher] Using Picsum fallback for '{query}'")

    # Download the image
    try:
        r = requests.get(img_url, stream=True, timeout=30)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1024*8):
                if chunk:
                    f.write(chunk)
        print(f"[asset_fetcher] Downloaded image: {dest}")
        return dest
    except Exception as e:
        # Emergency backup image
        print(f"[asset_fetcher] Image download failed: {e}. Creating placeholder image.")
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (1080, 1920), color = (30, 41, 59))
        d = ImageDraw.Draw(img)
        d.text((540, 960), f"Scene {scene_num}", fill=(255,255,255))
        img.save(dest)
        return dest

if __name__ == "__main__":
    # Test fetch
    import tempfile
    tmp = Path(tempfile.gettempdir())
    fetch_scene_image("artificial intelligence brain", tmp, 1)
