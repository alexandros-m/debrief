import csv
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

def load_settings():
    """Load settings from settings.json"""
    print("[INFO] Loading settings from settings.json...")
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            print("[DEBUG] Settings loaded successfully.")
            return settings
    except Exception as e:
        print(f"[ERROR] Error loading settings.json: {str(e)}")
        return None

def get_link_preview(url):
    """Fetch Open Graph metadata from a URL"""
    print(f"[INFO] Fetching preview for URL: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        print(f"[DEBUG] Sending request to {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"[DEBUG] Response received with status code: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')
        print("[DEBUG] Parsing HTML content for metadata...")

        domain = urlparse(url).netloc
        preview = {
            'image': soup.find("meta", property="og:image")['content'] if soup.find("meta", property="og:image") else None,
            'description': soup.find("meta", property="og:description")['content'] if soup.find("meta", property="og:description") else None,
            'favicon': f"https://www.google.com/s2/favicons?domain={domain}",
            'url': url
        }
        return preview
    except Exception as e:
        print(f"[ERROR] Error fetching {url}: {str(e)}")
        return None

def generate_html(articles, settings):
    """Generate HTML page with theme from settings"""
    print("[INFO] Generating HTML page...")

    # Fixed: Add default theme and validate extension
    theme = settings.get('theme', 'aero.css')
    if not theme.endswith('.css'):
        theme = 'aero.css'
    theme = "style/" + theme
    print(f"[DEBUG] Using theme: {theme}")

    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Debrief</title>
        <link rel="stylesheet" href="{theme}">
        <link href="https://fonts.googleapis.com/css2?family=GFS+Didot&display=swap" rel="stylesheet">

    </head>
    <body>
        <div class="mode-toggle" onclick="toggleDarkMode()">🌓 Toggle Mode</div>
        <div class="container">
            <div class="header">
                <h1>Debrief</h1>
                <p style="font-style: italic; color: var(--border-color);">Open Source, AI Powered News Aggregator</p>
            </div>
        <script>
            function toggleDarkMode() {{
                document.body.classList.toggle('dark-mode');
            }}
        </script>
    '''

    for article in articles:
        preview = article['preview']
        # Fixed: Properly handle preview-sites setting
        show_preview = settings.get('preview-sites', True)
        if isinstance(show_preview, str):  # Handle string values
            show_preview = show_preview.lower() == 'true'

        html += f'''
        <div class="article-card">
            <div class="content">
                <div class="rating">Rating: {article['rating']}</div>
                <h2 class="title">
                    {f'<img class="favicon" src="{preview["favicon"]}" alt="Favicon">' if preview and show_preview else ''}
                    <a href="{article['article_link']}" target="_blank">{article['title']}</a>
                </h2>
                {f'<p class="description">{preview["description"]}</p>' if preview and preview["description"] and show_preview else ''}
                {f'<img class="preview-image" src="{preview["image"]}" alt="Preview image">' if preview and preview["image"] and show_preview else ''}
            </div>
        </div>
        '''

    html += '''
        </div>
    </body>
    </html>
    '''

    try:
        with open('debrief.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("[INFO] HTML page generated successfully: debrief.html")
    except Exception as e:
        print(f"[ERROR] Error writing HTML file: {str(e)}")

def build_html():
    print("=== debrief - creating html file ===")

    settings = load_settings()
    if not settings:
        print("[ERROR] Failed to load settings. Exiting program.")
        return

    csv_file = settings.get('output_file', 'results.csv')
    print(f"[INFO] Using CSV file: {csv_file}")

    articles = []

    try:
        print(f"[INFO] Reading CSV file: {csv_file}")
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            print("[DEBUG] CSV headers detected:", reader.fieldnames)

            for row in reader:
                print(f"[DEBUG] Processing row: {row}")
                # Fixed: Handle string values for preview-sites
                get_preview = settings.get('preview-sites', True)
                if isinstance(get_preview, str):
                    get_preview = get_preview.lower() == 'true'

                preview = get_link_preview(row['article_link']) if get_preview else None
                articles.append({
                    'title': row['title'],
                    'article_link': row['article_link'],
                    'rating': row['rating'],
                    'preview': preview
                })
    except Exception as e:
        print(f"[ERROR] Error reading {csv_file}: {str(e)}")
        return

    print(f"[INFO] Processed {len(articles)} articles.")
    generate_html(articles, settings)
    print("[INFO] Program completed successfully.")
    print("\nOpen result in your browser: file://" + os.path.abspath("debrief.html\n"))

if __name__ == "__main__":
    build_html()
