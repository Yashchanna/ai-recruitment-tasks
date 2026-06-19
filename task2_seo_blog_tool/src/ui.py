import streamlit as st
from pathlib import Path
import sys
import os

# Ensure project root is in python path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from task2_seo_blog_tool.src.product_scraper import scrape_products
from task2_seo_blog_tool.src.keyword_research import select_seo_keywords
from task2_seo_blog_tool.src.blog_generator import generate_blog
from task2_seo_blog_tool.src.publisher import publish_to_devto
from task2_seo_blog_tool.src.config import DEVTO_API_KEY, is_token_valid

st.set_page_config(page_title='SEO Blog Creator & Publisher', layout='centered')
st.title('🤖 SEO Blog Creator')
st.markdown('''
This tool automates the creation of SEO-optimized product reviews and buying guides. 
It scrapes top products from eBay, researches target keywords using Google suggest APIs, and writes a professional 150-200 word review using **Gemini**.
''')

product = st.text_input('Product keyword (e.g. smart watch, wireless earbuds)', value='smart watch')
blogs_dir = st.text_input('Output Directory', value='./task2_seo_blog_tool/blogs')

if st.button('Generate Blog Post'):
    with st.spinner('Scraping trending listings...'):
        products = scrape_products(product)
        st.subheader('🛍️ Scraped Products')
        for idx, p in enumerate(products, 1):
            st.markdown(f"**{idx}. [{p['title']}]({p['link']})** — {p['price']}")
            
    with st.spinner('Analyzing SEO search suggestions...'):
        keywords = select_seo_keywords(product)
        st.subheader('🔑 Target SEO Keywords')
        st.write(", ".join(keywords))
        
    with st.spinner('Writing article with Gemini...'):
        # Generate the blog post
        out_path = Path(ROOT / blogs_dir.strip("./"))
        fn = generate_blog(product, out_path, products=products, keywords=keywords)
        
        with open(fn, 'r', encoding='utf-8') as f:
            blog_content = f.read()
            
        st.success(f'Saved to local blog: {fn.name}')
        st.subheader('📝 Blog Preview')
        st.markdown(blog_content)
        
        # Download button
        st.download_button(
            label="Download Markdown File",
            data=blog_content,
            file_name=fn.name,
            mime="text/markdown"
        )
        
        # Keep details in session state for publishing
        st.session_state['last_blog_title'] = blog_content.splitlines()[0].lstrip('# ').strip() if blog_content else product
        st.session_state['last_blog_body'] = blog_content
        st.session_state['last_blog_product'] = product

# Dev.to Publisher
st.markdown('---')
st.subheader('📤 Publish to Dev.to')

if 'last_blog_body' in st.session_state:
    if is_token_valid(DEVTO_API_KEY):
        st.write(f"Article: **{st.session_state['last_blog_title']}** is ready to publish.")
        if st.button('Publish Now'):
            with st.spinner('Publishing...'):
                success, resp = publish_to_devto(
                    title=st.session_state['last_blog_title'],
                    body_markdown=st.session_state['last_blog_body'],
                    tags=[st.session_state['last_blog_product'].replace(" ", "")[:10], "seo", "review"]
                )
                if success:
                    st.success(f"🎉 Published successfully! Live URL: {resp.get('url')}")
                else:
                    st.error(f"Failed to publish: {resp}")
    else:
        st.warning('Please configure a valid `DEVTO_API_KEY` in your `.env` file to publish to Dev.to.')
else:
    st.info('Generate a blog post first to enable publishing options.')
