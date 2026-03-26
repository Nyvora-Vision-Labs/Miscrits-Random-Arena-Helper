#!/usr/bin/env python3
"""
Miscrits Scraper
----------------
Fetches all miscrit names from https://worldofmiscrits.com/miscripedia
and generates a miscrits.json with name filled in and template
placeholders for type, speed, and image.

Requirements:
    pip install requests beautifulsoup4 selenium
    (selenium is the fallback since the page is JS-rendered)

Usage:
    python fetch_miscrits.py

Output:
    miscrits.json in the same folder
"""

import json
import re
import sys
import time

# ── Try requests + BeautifulSoup first (fast, no browser needed) ──
def try_requests(url):
    try:
        import requests
        from bs4 import BeautifulSoup

        print("[1/3] Trying requests + BeautifulSoup...")
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        names = extract_names_from_soup(soup)
        if names:
            print(f"    ✓ Found {len(names)} miscrits via requests")
            return names

        print("    ✗ Page loaded but no miscrits found (likely JS-rendered)")
        return None

    except Exception as e:
        print(f"    ✗ requests failed: {e}")
        return None


# ── Parse names out of whatever HTML we have ──
def extract_names_from_soup(soup):
    names = []

    # Strategy 1: <h3> tags inside miscrit cards (matches the HTML you showed)
    h3_tags = soup.find_all("h3")
    for tag in h3_tags:
        name = tag.get_text(strip=True)
        if name and 2 < len(name) < 40:
            names.append(name)

    if names:
        return sorted(set(names))

    # Strategy 2: anchor links to /miscripedia/<id>
    links = soup.find_all("a", href=re.compile(r"/miscripedia/\d+"))
    for link in links:
        h3 = link.find("h3")
        if h3:
            name = h3.get_text(strip=True)
            if name:
                names.append(name)

    if names:
        return sorted(set(names))

    # Strategy 3: alt text on miscrit images from CDN
    imgs = soup.find_all("img", src=re.compile(r"cdn\.worldofmiscrits\.com/miscrits/"))
    for img in imgs:
        alt = img.get("alt", "").strip()
        if alt and 2 < len(alt) < 40:
            names.append(alt)

    return sorted(set(names))


# ── Fallback: Selenium (headless Chrome) for JS-rendered pages ──
def try_selenium(url):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from bs4 import BeautifulSoup

        print("[2/3] Trying Selenium (headless Chrome)...")
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1280,900")

        driver = webdriver.Chrome(options=opts)
        driver.get(url)

        # Wait for miscrit cards to appear
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "h3"))
            )
        except Exception:
            pass  # Try anyway with whatever loaded

        time.sleep(2)  # Let any late JS finish
        html = driver.page_source
        driver.quit()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        names = extract_names_from_soup(soup)

        if names:
            print(f"    ✓ Found {len(names)} miscrits via Selenium")
            return names

        print("    ✗ Selenium loaded page but found no miscrits")
        return None

    except ImportError:
        print("    ✗ Selenium not installed — run: pip install selenium")
        return None
    except Exception as e:
        print(f"    ✗ Selenium failed: {e}")
        return None


# ── Last resort: ask the user to paste HTML ──
def try_manual_html():
    print("\n[3/3] Manual fallback:")
    print("  The site requires a browser to render. Please:")
    print("  1. Open https://worldofmiscrits.com/miscripedia in Chrome")
    print("  2. Press Ctrl+U (View Source) OR open DevTools → Elements")
    print("  3. Select all (Ctrl+A), copy, and paste below.")
    print("  4. Press Enter twice when done.\n")

    lines = []
    try:
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
    except EOFError:
        pass

    if not lines:
        return None

    from bs4 import BeautifulSoup
    soup = BeautifulSoup("\n".join(lines), "html.parser")
    names = extract_names_from_soup(soup)
    if names:
        print(f"    ✓ Found {len(names)} miscrits from pasted HTML")
        return names

    print("    ✗ Could not extract names from pasted HTML")
    return None


# ── Build the JSON template ──
def build_json(names):
    entries = []
    for name in names:
        # Derive image filename: lowercase, spaces → underscores, append _back.png
        slug = name.lower().replace(" ", "_").replace("'", "")
        entries.append({
            "name":  name,
            "type":  "unknown",    # TODO: fill in (fire/water/nature/earth/lightning/wind)
            "speed": None,         # TODO: fill in numeric speed (25/45/65/85)
            "image": f"https://cdn.worldofmiscrits.com/miscrits/{slug}_back.png"
        })
    return entries


# ── Main ──
def main():
    url = "https://worldofmiscrits.com/miscripedia"
    print(f"Fetching miscrits from {url}\n")

    names = (
        try_requests(url)
        or try_selenium(url)
        or try_manual_html()
    )

    if not names:
        print("\n✗ Could not fetch miscrit names through any method.")
        print("  Install selenium:  pip install selenium")
        print("  Or paste the page HTML when prompted above.")
        sys.exit(1)

    data = build_json(names)

    output_file = "miscrits.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {len(data)} miscrits to {output_file}")
    print("\nSample entries:")
    for entry in data[:3]:
        print(f"  {json.dumps(entry)}")
    print(f"  ... ({len(data) - 3} more)\n")
    print("Next steps:")
    print("  1. Open miscrits.json")
    print('  2. Fill in "type" for each miscrit (fire/water/nature/earth/lightning/wind)')
    print('  3. Fill in "speed" (25=Weak, 45=Mod, 65=Strong, 85=Max)')
    print("  4. Verify image URLs load correctly in a browser")


if __name__ == "__main__":
    main()