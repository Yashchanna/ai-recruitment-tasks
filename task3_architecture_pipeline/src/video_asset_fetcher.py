import os
import requests
import urllib.parse
from bs4 import BeautifulSoup

def get_scene_image_url(query: str, scene_num: int) -> str:
    """Return a high-quality vertical stock photo URL for a scene.
    Tries Pexels first, then Unsplash search scraping, and falls back to Picsum.
    Does not download the file to preserve serverless bandwidth.
    """
    # 1. Pexels
    api_key = os.getenv("PEXELS_API_KEY", "").strip()
    if api_key and not api_key.startswith("your_"):
        try:
            url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=1"
            resp = requests.get(url, headers={"Authorization": api_key}, timeout=10)
            if resp.status_code == 200:
                photos = resp.json().get("photos") or []
                if photos:
                    url_found = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
                    if url_found:
                        return url_found
        except Exception:
            pass
            
    # 2. Unsplash
    try:
        clean_query = query.replace("-", " ").strip()
        search_url = f"https://unsplash.com/s/photos/{urllib.parse.quote(clean_query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        resp = requests.get(search_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src', '')
                if 'images.unsplash.com/photo-' in src:
                    base_url = src.split('?')[0]
                    return f"{base_url}?auto=format&fit=crop&w=1080&h=1920&q=80"
    except Exception:
        pass
        
    # 3. Fallback Picsum
    rand_seed = abs(hash(query)) % 1000
    return f"https://picsum.photos/1080/1920?random={rand_seed}"
