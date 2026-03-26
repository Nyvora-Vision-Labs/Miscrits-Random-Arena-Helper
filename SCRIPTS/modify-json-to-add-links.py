import json
import os

JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "miscrits.json")
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "images_scraped_from_miscripedia")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    miscrits = json.load(f)

updated = 0
missing = 0

for miscrit in miscrits:
    name = miscrit.get("name", "")
    image_filename = f"{name}.png"
    image_path = os.path.join(IMAGES_DIR, image_filename)

    # Store a normalized relative path (forward slashes)
    relative_path = f"images_scraped_from_miscripedia/{image_filename}"

    if os.path.exists(image_path):
        miscrit["image_random_arena"] = relative_path
        updated += 1
    else:
        # Still store the expected path even if file is missing, set to null
        miscrit["image_random_arena"] = None
        missing += 1
        print(f"  [MISSING] No image found for: {name} (expected: {image_path})")

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(miscrits, f, indent=2, ensure_ascii=False)

print(f"\nDone! {updated} entries updated, {missing} missing images (set to null).")
print(f"JSON saved to: {os.path.abspath(JSON_PATH)}")