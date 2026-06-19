import os
import json
import google.generativeai as genai
from typing import Dict, Any

def generate_script(topic: str, context: str = "") -> Dict[str, Any]:
    """Generates a structured video script using Google Gemini.
    If context (news summary) is provided, it'll generate based on the news article.
    Otherwise, it generates a topic overview.
    Falls back to a local rule-based generator if API key is missing or calls fail.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    prompt = f"""You are a creative director for viral social media content (TikTok, YouTube Shorts, Reels).
Your job is to write an engaging, high-impact 30-45 second video script about the following topic.

Topic: {topic}
Context/News detail: {context}

You must respond with a JSON object containing the script structure. Follow these rules:
1. Provide exactly 4 to 5 scenes.
2. The tone must be engaging, informative, and fast-paced.
3. For each scene, provide:
   - "scene_num": integer (1, 2, ...)
   - "narration": The actual spoken voiceover text (approx 15-25 words per scene).
   - "visual_prompt": A descriptive search query to find a stock photo/image on a service like Unsplash (e.g. "futuristic city silhouette", "smart watch running display"). Keep it search-friendly (2-4 words, descriptive).
   - "overlay_text": A short, catchy text snippet to show on the screen (3-5 words, capital letters).

JSON Response Schema:
{{
  "title": "Short catchy video title",
  "scenes": [
    {{
      "scene_num": 1,
      "narration": "First scene narration",
      "visual_prompt": "First scene visual query",
      "overlay_text": "FIRST OVERLAY"
    }},
    ...
  ]
}}
"""

    if api_key and not api_key.startswith("your_"):
        # List of candidate models to try
        models_to_try = ["gemini-2.5-flash", "gemini-3.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro-latest"]
        genai.configure(api_key=api_key)
        
        for model_name in models_to_try:
            try:
                print(f"[script_gen] Attempting script generation with model '{model_name}'...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                data = json.loads(response.text)
                if "scenes" in data and len(data["scenes"]) > 0:
                    print(f"[script_gen] Script generated successfully using '{model_name}'")
                    return data
            except Exception as e:
                print(f"[script_gen] Call with '{model_name}' failed: {e}")
                continue
            
        print("[script_gen] All Gemini models failed. Falling back to rule-based script.")
            
    # Local fallback script generator
    clean_topic = topic.replace('"', '').replace("'", "")
    fallback = {
        "title": f"The Truth About {clean_topic}",
        "scenes": [
            {
                "scene_num": 1,
                "narration": f"Have you heard the latest about {clean_topic}? Here is why it's trending everywhere right now.",
                "visual_prompt": "trending global news",
                "overlay_text": "TRENDING NOW"
            },
            {
                "scene_num": 2,
                "narration": "People are talking about the massive impact and the shifts we are starting to see.",
                "visual_prompt": "impact growth puzzle",
                "overlay_text": "MASSIVE SHIFT"
            },
            {
                "scene_num": 3,
                "narration": "Here are the top key facts you need to know about this major change.",
                "visual_prompt": "facts explanation keys",
                "overlay_text": "KEY FACTS"
            },
            {
                "scene_num": 4,
                "narration": "What do you think? Let us know your thoughts in the comments below, and don't forget to follow for more updates.",
                "visual_prompt": "comments discussion smartphone",
                "overlay_text": "WHAT DO YOU THINK?"
            }
        ]
    }
    return fallback

if __name__ == "__main__":
    # Test fallback
    print(generate_script("Artificial Intelligence"))
