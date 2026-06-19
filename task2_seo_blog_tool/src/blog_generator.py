from pathlib import Path
import datetime
import os
from typing import List, Dict, Any
from task2_seo_blog_tool.src.config import is_token_valid

TEMPLATE = """# Best {product} — Guide & Review

Looking for the best {product}? You've come to the right place. Selecting the right model can elevate your daily experience, whether you prioritize features, durability, or overall value. 

Here are the top options available right now:
{product_list}

When purchasing, keep in mind key search terms like **{keywords}** to find guides, reviews, and competitive pricing online. Always check user feedback and compare warranty options to get the most out of your purchase.

---
*Generated on {date}*
"""

def generate_blog(product: str, out_dir: str, products: List[Dict[str, Any]] = None, keywords: List[str] = None) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    slug = product.lower().replace(' ', '-')
    fn = out / f"{slug}.md"
    
    if not products:
        products = []
    if not keywords:
        keywords = ["buying guide", "best price", "product review"]

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if is_token_valid(api_key):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Format product details for the prompt
            prod_info = ""
            for p in products:
                prod_info += f"- Name: {p['title']}\n  Price: {p['price']}\n  Link: {p['link']}\n"
                
            prompt = (
                f"Write an engaging, SEO-optimized blog post about '{product}'.\n"
                f"Target length: 150-200 words.\n\n"
                f"SEO Keywords to naturally incorporate:\n{', '.join(keywords)}\n\n"
                f"Top Products to feature/highlight (include their names, prices, and links as markdown hyper-links):\n{prod_info}\n\n"
                f"Requirements:\n"
                f"1. Start with a single '# Title' representing the blog title.\n"
                f"2. Incorporate the SEO keywords naturally.\n"
                f"3. Highlight/feature the products.\n"
                f"4. Be professional and persuasive.\n"
                f"5. Return only the markdown blog content."
            )
            resp = model.generate_content(prompt)
            text = resp.text.strip()
            
            with open(fn, 'w', encoding='utf-8') as f:
                f.write(text)
            return fn
        except Exception as e:
            print(f"Gemini blog generation failed: {e}")

    # Fallback template-based generation
    prod_lines = ""
    for p in products:
        prod_lines += f"- **[{p['title']}]({p['link']})** - {p['price']}\n"
        
    fallback_text = TEMPLATE.format(
        product=product,
        product_list=prod_lines or f"- Premium {product}\n",
        keywords=", ".join(keywords),
        date=datetime.date.today().strftime("%B %d, %Y")
    )
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(fallback_text)
    return fn
