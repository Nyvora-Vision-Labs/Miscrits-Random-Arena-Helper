"""
update_miscrits_json.py
=======================
Scrapes https://www.worldofmiscrits.com/miscripedia/1 → /670
and updates miscrits.json with:
  - type          (Fire, Water, Nature, etc.)
  - rarity        (Common, Uncommon, Rare, Epic, Legendary, Exotic)
  - speed         (1–5)
  - physical_attack, elemental_attack, physical_defense, elemental_defense, health
  - miscripedia_url

Matches each scraped page to miscrits.json by name (case-insensitive).
All existing fields are preserved.

Requirements:
    pip install selenium requests webdriver-manager

Usage:
    python update_miscrits_json.py
"""

import json
import re
import time
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# ── Try to auto-manage the browser driver ─────────────────────────────────────
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WDM_AVAILABLE = True
except ImportError:
    WDM_AVAILABLE = False

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL        = "https://www.worldofmiscrits.com/miscripedia"
ID_START        = 1
ID_END          = 670
MISCRITS_JSON   = "miscrits.json"          # path to your existing JSON
OUTPUT_JSON     = "miscrits_updated.json"  # output file (safe – doesn't overwrite original)

BROWSER         = "chrome"
HEADLESS        = True
PAGE_TIMEOUT    = 15     # seconds to wait for JS render
DELAY_BETWEEN   = 0.3    # seconds between pages

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

def make_driver() -> webdriver.Chrome:
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument(f"user-agent={HEADERS['User-Agent']}")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)

    if WDM_AVAILABLE:
        import os
        from selenium.webdriver.chrome.service import Service
        local_cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".wdm")
        os.makedirs(local_cache, exist_ok=True)
        os.environ["WDM_LOCAL"]      = "1"
        os.environ["WDM_CACHE_PATH"] = local_cache
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=opts)
    else:
        # Selenium 4.6+ ships its own driver manager
        return webdriver.Chrome(options=opts)


# ── Helpers ───────────────────────────────────────────────────────────────────

def is_not_found(driver) -> bool:
    try:
        driver.find_element(By.XPATH, "//*[contains(text(),'Miscrit Not Found')]")
        return True
    except Exception:
        return False


def wait_for_content(driver, timeout: int = PAGE_TIMEOUT) -> bool:
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


def count_filled_bars(bar_div) -> int:
    """
    Count the number of 'filled' stat segments in a bar div.
    A segment is considered EMPTY if its class contains 'bg-amber-50/50'.
    Any other background color (bg-yellow-500, bg-red-500, etc.) counts as filled.
    """
    segments = bar_div.find_elements(By.XPATH, "./div")
    filled = 0
    for seg in segments:
        classes = seg.get_attribute("class") or ""
        if "bg-amber-50/50" not in classes:
            filled += 1
    return filled


def parse_page(driver):
    """
    Returns a dict with keys:
        name, type, rarity, speed, physical_attack, elemental_attack,
        physical_defense, elemental_defense, health
    or None if the page is not found / unparseable.
    """
    if is_not_found(driver):
        return None

    result = {}

    # ── Name + Element type ───────────────────────────────────────────────────
    try:
        header = driver.find_element(
            By.XPATH,
            "//div[contains(@class,'flex') and contains(@class,'items-center') "
            "and contains(@class,'mb-4')]"
        )
        # Element icon: <img alt="Fire element" ...>
        try:
            icon = header.find_element(By.TAG_NAME, "img")
            alt  = icon.get_attribute("alt") or ""
            # e.g. "Fire element" → "Fire"
            result["type"] = alt.replace(" element", "").strip() or "unknown"
        except Exception:
            result["type"] = "unknown"

        h2 = header.find_element(By.TAG_NAME, "h2")
        result["name"] = h2.text.strip()
    except Exception:
        # Fallback: just grab first h2
        try:
            result["name"] = driver.find_element(By.TAG_NAME, "h2").text.strip()
        except Exception:
            return None
        result["type"] = "unknown"

    if not result.get("name"):
        return None

    # ── Rarity ────────────────────────────────────────────────────────────────
    # Targets: <p class="text-lg font-bold" style="color: ...">Common</p>
    RARITY_VALUES = {"Common", "Uncommon", "Rare", "Epic", "Legendary", "Exotic"}
    result["rarity"] = None
    try:
        candidates = driver.find_elements(
            By.XPATH,
            "//p[contains(@class,'text-lg') and contains(@class,'font-bold')]"
        )
        for candidate in candidates:
            text = candidate.text.strip()
            if text in RARITY_VALUES:
                result["rarity"] = text
                break
            elif text:
                log.debug(f"  Unrecognized rarity text: '{text}'")
    except Exception as e:
        log.warning(f"  Rarity parsing error for '{result.get('name')}': {e}")

    # ── Stats ─────────────────────────────────────────────────────────────────
    # Stat labels live in divs with class "text-right font-medium text-miscrits-brown"
    # The bar div immediately follows the label div in the DOM.
    stat_map = {
        "Speed":              "speed",
        "Physical Attack":    "physical_attack",
        "Elemental Attack":   "elemental_attack",
        "Physical Defense":   "physical_defense",
        "Elemental Defense":  "elemental_defense",
        "Health":             "health",
    }

    # Initialize all stats to None so they appear in the output even if not found
    for key in stat_map.values():
        result[key] = None

    try:
        # Find all stat label divs
        label_divs = driver.find_elements(
            By.XPATH,
            "//div[contains(@class,'text-right') and "
            "contains(@class,'font-medium') and "
            "contains(@class,'text-miscrits-brown')]"
        )

        for label_div in label_divs:
            label_text = label_div.text.strip()
            json_key   = stat_map.get(label_text)
            if json_key is None:
                continue  # unknown stat, skip

            # The bar div is the next sibling element
            try:
                bar_div = label_div.find_element(
                    By.XPATH, "following-sibling::div[1]"
                )
                result[json_key] = count_filled_bars(bar_div)
            except Exception:
                pass  # leave as None

    except Exception as e:
        log.warning(f"  Stats parsing error for '{result.get('name')}': {e}")

    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Load existing miscrits.json
    json_path = Path(MISCRITS_JSON)
    if not json_path.exists():
        log.error(f"'{MISCRITS_JSON}' not found. Put it next to this script.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        miscrits = json.load(f)

    # Build a lookup: lowercase name → list index
    name_index = {m["name"].lower(): i for i, m in enumerate(miscrits)}

    total     = ID_END - ID_START + 1
    matched   = 0
    not_found = 0
    no_match  = 0
    errors    = 0

    log.info(f"Loaded {len(miscrits)} miscrits from '{MISCRITS_JSON}'")
    log.info(f"Starting Selenium ({BROWSER}, headless={HEADLESS})")
    log.info(f"Scraping #{ID_START} → #{ID_END}  ({total} pages)\n")

    driver = make_driver()

    try:
        for miscrit_id in range(ID_START, ID_END + 1):
            url = f"{BASE_URL}/{miscrit_id}"

            # Navigate
            try:
                driver.get(url)
            except WebDriverException as e:
                log.warning(f"#{miscrit_id:>4}  [NAV ERROR] {e}")
                errors += 1
                time.sleep(DELAY_BETWEEN)
                continue

            # Wait for JS render
            if not wait_for_content(driver):
                log.warning(f"#{miscrit_id:>4}  [TIMEOUT]")
                errors += 1
                time.sleep(DELAY_BETWEEN)
                continue

            # Parse page
            data = parse_page(driver)

            if data is None:
                not_found += 1
                log.debug(f"#{miscrit_id:>4}  [not found]")
                time.sleep(DELAY_BETWEEN)
                continue

            scraped_name = data["name"]
            idx = name_index.get(scraped_name.lower())

            if idx is None:
                no_match += 1
                log.warning(f"#{miscrit_id:>4}  '{scraped_name}' — NOT in miscrits.json, skipping")
                time.sleep(DELAY_BETWEEN)
                continue

            # ── Update the JSON entry ──────────────────────────────────────
            entry = miscrits[idx]

            entry["type"]              = data["type"]
            entry["rarity"]            = data["rarity"]
            entry["speed"]             = data["speed"]
            entry["physical_attack"]   = data["physical_attack"]
            entry["elemental_attack"]  = data["elemental_attack"]
            entry["physical_defense"]  = data["physical_defense"]
            entry["elemental_defense"] = data["elemental_defense"]
            entry["health"]            = data["health"]
            entry["miscripedia_url"]   = url

            matched += 1
            log.info(
                f"#{miscrit_id:>4}  ✓  {scraped_name:<25}  "
                f"type={data['type']:<10}  "
                f"rarity={str(data['rarity']):<12}  "
                f"spd={data['speed']}  "
                f"patk={data['physical_attack']}  "
                f"eatk={data['elemental_attack']}  "
                f"pdef={data['physical_defense']}  "
                f"edef={data['elemental_defense']}  "
                f"hp={data['health']}"
            )

            time.sleep(DELAY_BETWEEN)

    finally:
        driver.quit()

    # Save updated JSON
    out_path = Path(OUTPUT_JSON)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(miscrits, f, indent=2, ensure_ascii=False)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  Update complete")
    print(f"{'='*55}")
    print(f"  Pages scraped    : {total}")
    print(f"  Matched + updated: {matched}")
    print(f"  Not found (404)  : {not_found}")
    print(f"  No JSON match    : {no_match}")
    print(f"  Fetch errors     : {errors}")
    print(f"  Output saved to  : {out_path.resolve()}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()