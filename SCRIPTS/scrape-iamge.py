"""
scrape_miscripedia_selenium.py
==============================
Scrapes https://www.worldofmiscrits.com/miscripedia/1 → /670
using Selenium so JavaScript-rendered content is fully loaded.

For each valid page it extracts:
  - The miscrit's base name  (from the <h2> next to the element icon)
  - The LAST evolution avatar image  (last img in the evolution grid)

Saves everything to:  images_scraped_from_miscripedia/
  └─ <Name>.png        e.g. Wyndasia.png

Also writes:  images_scraped_from_miscripedia/index.csv
  id, name, image_url

Requirements:
    pip install selenium requests

  AND one of:
    - Chrome  + pip install webdriver-manager
    - Firefox + pip install webdriver-manager

Usage:
    python scrape_miscripedia_selenium.py
"""

import re
import csv
import time
import logging
import requests
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# ── Try to auto-manage the browser driver ─────────────────────────────────────
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    WDM_AVAILABLE = True
except ImportError:
    WDM_AVAILABLE = False

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL      = "https://www.worldofmiscrits.com/miscripedia"
ID_START      = 1
ID_END        = 670
OUTPUT_FOLDER = "images_scraped_from_miscripedia"

BROWSER       = "chrome"    # "chrome" or "firefox"
HEADLESS      = True        # False = show the browser window while scraping
PAGE_TIMEOUT  = 15          # seconds to wait for page content to appear
DELAY_BETWEEN = 0.3         # seconds to pause between pages

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Driver factory ────────────────────────────────────────────────────────────

def make_chrome_driver() -> webdriver.Chrome:
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument(f"user-agent={HEADERS['User-Agent']}")
    # Suppress DevTools / logging noise
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)

    if WDM_AVAILABLE:
        import os
        from selenium.webdriver.chrome.service import Service
        # Store the driver cache next to this script to avoid Windows
        # permission errors when the home folder is on OneDrive.
        local_cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".wdm")
        os.makedirs(local_cache, exist_ok=True)
        os.environ["WDM_LOCAL"]      = "1"
        os.environ["WDM_CACHE_PATH"] = local_cache
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=opts)
    else:
        # Selenium 4.6+ ships its own driver manager - works with no extras.
        return webdriver.Chrome(options=opts)


def make_firefox_driver() -> webdriver.Firefox:
    opts = webdriver.FirefoxOptions()
    if HEADLESS:
        opts.add_argument("--headless")
    opts.set_preference("general.useragent.override", HEADERS["User-Agent"])

    if WDM_AVAILABLE:
        from selenium.webdriver.firefox.service import Service
        service = Service(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=opts)
    else:
        return webdriver.Firefox(options=opts)


def make_driver():
    try:
        if BROWSER == "firefox":
            return make_firefox_driver()
        return make_chrome_driver()
    except Exception as e:
        log.error(f"Could not start {BROWSER}: {e}")
        log.error("Make sure Chrome/Firefox is installed and chromedriver/geckodriver is on PATH,")
        log.error("or run:  pip install webdriver-manager")
        raise


# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "", name).strip()


def is_not_found(driver: webdriver.Remote) -> bool:
    """Return True if the page shows 'Miscrit Not Found'."""
    try:
        driver.find_element(By.XPATH, "//*[contains(text(),'Miscrit Not Found')]")
        return True
    except Exception:
        return False


def wait_for_content(driver: webdriver.Remote, timeout: int = PAGE_TIMEOUT) -> bool:
    """
    Wait until either the miscrit name header OR the not-found message appears.
    Returns True when content is ready, False on timeout.
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//*[contains(@class,'mb-4')]//h2 | "
                "//*[contains(text(),'Miscrit Not Found')]"
            ))
        )
        return True
    except TimeoutException:
        return False


def parse_page(driver: webdriver.Remote):
    """
    Extract (name, avatar_url) from the loaded page.
    Returns (None, None) if the page is 'not found' or parsing fails.
    """
    if is_not_found(driver):
        return None, None

    # ── Name ──────────────────────────────────────────────────────────────────
    name = None
    try:
        # The header div contains the element icon + name h2
        header = driver.find_element(
            By.XPATH,
            "//div[contains(@class,'flex') and contains(@class,'items-center') "
            "and contains(@class,'mb-4')]"
        )
        h2 = header.find_element(By.TAG_NAME, "h2")
        name = h2.text.strip()
    except Exception:
        pass

    if not name:
        try:
            name = driver.find_element(By.TAG_NAME, "h2").text.strip()
        except Exception:
            pass

    if not name:
        return None, None

    # ── Last evolution avatar ─────────────────────────────────────────────────
    avatar_url = None
    try:
        # Evolution grid: div with grid-cols-4
        evo_grid = driver.find_element(
            By.XPATH,
            "//div[contains(@class,'grid') and contains(@class,'grid-cols-4')]"
        )
        # All avatar images inside the grid
        imgs = evo_grid.find_elements(
            By.XPATH,
            ".//img[contains(@src,'cdn.worldofmiscrits.com/avatars/')]"
        )
        if imgs:
            avatar_url = imgs[-1].get_attribute("src")
    except Exception:
        pass

    return name, avatar_url


def download_image(url: str, dest: Path) -> bool:
    """Download image via requests (much faster than Selenium for binary files)."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        log.warning(f"  Image download failed ({url}): {e}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    out = Path(OUTPUT_FOLDER)
    out.mkdir(exist_ok=True)

    csv_path   = out / "index.csv"
    csv_file   = open(csv_path, "w", newline="", encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["id", "name", "image_url"])

    total     = ID_END - ID_START + 1
    found     = 0
    not_found = 0
    errors    = 0
    img_saved = 0

    log.info(f"Starting Selenium ({BROWSER}, headless={HEADLESS})")
    log.info(f"Scraping #{ID_START} → #{ID_END}  ({total} pages)")
    log.info(f"Output: {out.resolve()}\n")

    driver = make_driver()

    try:
        for miscrit_id in range(ID_START, ID_END + 1):
            url = f"{BASE_URL}/{miscrit_id}"

            # ── Navigate ──
            try:
                driver.get(url)
            except WebDriverException as e:
                log.warning(f"#{miscrit_id:>4}  [NAV ERROR] {e}")
                errors += 1
                time.sleep(DELAY_BETWEEN)
                continue

            # ── Wait for JS render ──
            ready = wait_for_content(driver)
            if not ready:
                log.warning(f"#{miscrit_id:>4}  [TIMEOUT] page did not render in time")
                errors += 1
                time.sleep(DELAY_BETWEEN)
                continue

            # ── Parse ──
            name, avatar_url = parse_page(driver)

            if name is None:
                not_found += 1
                log.debug(f"#{miscrit_id:>4}  [not found]")
                time.sleep(DELAY_BETWEEN)
                continue

            found += 1

            # ── Download image ──
            if avatar_url:
                ext      = Path(avatar_url.split("?")[0]).suffix or ".png"
                filename = f"{safe_filename(name)}{ext}"
                dest     = out / filename

                success = download_image(avatar_url, dest)
                if success:
                    img_saved += 1
                    log.info(f"#{miscrit_id:>4}  ✓  {name:<25}  → {filename}")
                else:
                    log.warning(f"#{miscrit_id:>4}  ✗  {name:<25}  (image download failed)")
            else:
                log.warning(f"#{miscrit_id:>4}  ?  {name:<25}  (no avatar found on page)")

            csv_writer.writerow([miscrit_id, name, avatar_url or ""])
            csv_file.flush()

            time.sleep(DELAY_BETWEEN)

    finally:
        driver.quit()
        csv_file.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*52}")
    print(f"  Scrape complete")
    print(f"{'='*52}")
    print(f"  Pages checked  : {total}")
    print(f"  Miscrits found : {found}")
    print(f"  Not found/skip : {not_found}")
    print(f"  Fetch errors   : {errors}")
    print(f"  Images saved   : {img_saved}")
    print(f"  Index CSV      : {csv_path.resolve()}")
    print(f"{'='*52}\n")


if __name__ == "__main__":
    main()