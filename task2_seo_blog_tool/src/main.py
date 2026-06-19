"""SEO Blog Creator Pipeline Runner."""
import argparse
from pathlib import Path
import os
from task2_seo_blog_tool.src.product_scraper import scrape_products
from task2_seo_blog_tool.src.keyword_research import select_seo_keywords
from task2_seo_blog_tool.src.blog_generator import generate_blog
from task2_seo_blog_tool.src.config import ROOT

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--product", required=True, help="Product keyword to base the blog on")
    p.add_argument("--publish", choices=["local","devto","both"], default="local", help="Where to publish the generated blog")
    args = p.parse_args()

    blogs_dir = Path(ROOT / "task2_seo_blog_tool" / "blogs")
    blogs_dir.mkdir(parents=True, exist_ok=True)

    print(f"[task2] Base Product Category: '{args.product}'")
    
    # 1. Scrape Products
    print("[task2] Scraping top products from eBay...")
    products = scrape_products(args.product)
    for idx, prod in enumerate(products, 1):
        print(f"  {idx}. {prod['title']} ({prod['price']})")

    # 2. Keyword Research
    print("[task2] Performing SEO keyword research...")
    keywords = select_seo_keywords(args.product)
    print(f"  Target Keywords: {', '.join(keywords)}")

    # 3. Generate Blog
    print("[task2] Generating SEO-optimized blog using Gemini...")
    fn = generate_blog(args.product, blogs_dir, products=products, keywords=keywords)
    print(f"[task2] Blog successfully generated at: {fn.resolve()}")

    # 4. Optional Publishing to Dev.to
    if args.publish in ("devto","both"):
        try:
            from task2_seo_blog_tool.src.publisher import publish_to_devto
        except Exception:
            print("[task2] Publisher module missing; cannot publish to Dev.to.")
            return

        with open(fn, 'r', encoding='utf-8') as f:
            content = f.read()
        title = content.splitlines()[0].lstrip('# ').strip() if content else args.product

        print("[task2] Publishing article to Dev.to...")
        success, resp = publish_to_devto(title, content, tags=[args.product.replace(" ", "")[:10], "seo", "review"])
        if success:
            url = resp.get('url') if isinstance(resp, dict) else 'unknown'
            print(f"[task2] 🎉 Published successfully! Live URL: {url}")
        else:
            print(f"[task2] Dev.to publishing skipped/failed: {resp}")


if __name__ == "__main__":
    main()
