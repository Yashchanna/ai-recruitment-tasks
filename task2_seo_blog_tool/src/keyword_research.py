import requests
import urllib.parse
import os
from typing import List
from task2_seo_blog_tool.src.config import is_token_valid

def get_suggested_keywords(query: str) -> List[str]:
    """Retrieve search suggestions from Google autocomplete API."""
    encoded_query = urllib.parse.quote_plus(query)
    url = f"http://suggestqueries.google.com/complete/search?client=chrome&q={encoded_query}"
    
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            # Google Suggest format: [original_query, [suggestion1, suggestion2, ...]]
            if len(data) > 1 and isinstance(data[1], list):
                return data[1]
    except Exception as e:
        print(f"Keyword autocomplete API error: {e}")
    return []

def select_seo_keywords(query: str) -> List[str]:
    """Perform keyword research and return the top 4 SEO keywords."""
    suggestions = get_suggested_keywords(query)
    
    # Use Gemini to pick/format the best keywords if API key is set
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if is_token_valid(api_key) and suggestions:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            prompt = (
                f"Given the product '{query}' and these Google search suggestions:\n"
                f"{', '.join(suggestions)}\n\n"
                f"Choose or generate the top 4 highly-relevant SEO keywords/phrases (comma-separated, no numbering, no prefix). "
                f"They should have high commercial intent. Example output format: keyword1, keyword2, keyword3, keyword4"
            )
            resp = model.generate_content(prompt)
            text = resp.text.strip()
            keywords = [k.strip() for k in text.split(",") if k.strip()]
            if len(keywords) >= 3:
                return keywords[:4]
        except Exception as e:
            print(f"Gemini keyword ranking failed: {e}")
            
    # Fallback default keywords
    default_keywords = [
        f"best {query}",
        f"buy {query}",
        f"{query} review",
        f"cheap {query}"
    ]
    
    # Mix autocomplete suggestions with defaults if available
    if suggestions:
        refined = [s for s in suggestions if len(s.split()) < 5] # keep short phrases
        if refined:
            return (refined[:2] + default_keywords[:2])[:4]
            
    return default_keywords
