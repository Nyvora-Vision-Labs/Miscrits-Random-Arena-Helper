# 🎮 Miscrits-Random-Arena-Helper

A browser-based tool for **Miscrits** players that analyzes Random Arena team pickup lobbies using image recognition and displays a ranked draft pool to help you build the best possible team.

> Built by **Nyvora Vision Labs**

---

## 🧩 What It Does

1. **Screenshot Analysis** — Upload a screenshot of a Random Arena team pickup lobby and the tool automatically identifies each Miscrit's name, type, and speed tier using visual recognition.
2. **Draft Pool Display** — Detected Miscrits are split into two columns — **Green Speed** (fast) and **Red Speed** (slow) — sorted by meta tier first, then rarity, so you can pick the strongest options at a glance.

---

## ✨ Features

- 📸 **Drag-and-drop screenshot upload** — supports image pasting directly into the browser
- 🔍 **Visual Miscrit detection** — maps arena lobby sprites to known Miscrit data
- ⚡ **Two-column draft pool** — Green Speed and Red Speed miscrits displayed side by side
- 🏅 **Meta tier sorting** — S / A+ / A tier miscrits (from `meta.json`) float to the top of each column
- 🏷️ **Element & rarity tags** — instantly see elemental type and rarity for every Miscrit in the draft pool
- 📊 **Stat mini-bars** — view HP, Attack, Defense, and Speed at a glance in the detail modal
- 📖 **Miscrit Tome** — browse the full Miscrit roster with search and type filters
- 🌑 **Dark fantasy UI** — styled with a rich RPG aesthetic using Cinzel and Crimson Pro fonts

---

## 📁 Repository Structure

```
Miscrits/
├── index.html                        # Main single-file web application
├── miscrits.json                     # Base Miscrit dataset
├── miscrits_updated.json             # Updated Miscrit dataset with latest entries
├── meta.json                         # Meta tier rankings (S / A+ / A)
├── SCRIPTS/                          # Python utility scripts
├── Images_random_arena/              # Arena lobby sprite images used for matching
└── images_scraped_from_miscripedia/  # Miscrit images scraped from the Miscrits wiki
```

---

## 🚀 Getting Started

No installation or build step required — this is a fully self-contained HTML application.

1. **Clone the repository:**

   ```bash
   git clone https://github.com/TempGaurab/Miscrits.git
   cd Miscrits
   ```

2. **Serve locally** (required for JSON and image loading):

   ```bash
   python -m http.server
   ```

   Then open `http://localhost:8000` in your browser.

3. **Use the tool:**
   - Take a screenshot of your Random Arena lobby in Miscrits
   - Drag and drop (or paste) the screenshot into the upload zone
   - Click **Identify Miscrits** and wait for detection to complete
   - Browse the **Green Speed** and **Red Speed** draft columns to plan your picks

---

## 🗂️ Meta Tiers (`meta.json`)

The draft pool is sorted using `meta.json`, a simple tier list file placed in the root of the project:

```json
{
  "miscrits": [
    { "name": "Geneseed", "meta_rarity": "S" },
    { "name": "Aquarion", "meta_rarity": "A+" },
    { "name": "Rexie", "meta_rarity": "A" }
  ]
}
```

\*\*Meta Details as of Version 2.4.0.

| Tier         | Meaning                              |
| ------------ | ------------------------------------ |
| `S`          | Top meta — highest priority picks    |
| `A+`         | Strong — consistently competitive    |
| `A`          | Solid — reliable picks               |
| _(unlisted)_ | Off-meta — sorted by rarity fallback |

If `meta.json` is absent, the draft pool falls back to rarity ordering (Legendary → Exotic → Epic → Rare → Common).

---

## 🐍 Python Scripts

The `SCRIPTS/` folder contains Python utilities used for data preparation:

- Scraping Miscrit images from Miscripedia (the Miscrits wiki)
- Processing and formatting the Miscrit dataset into JSON
- Preprocessing for arena sprite matching

These scripts are used for development and data updates and are not required to run the web app.

---

## 🗃️ Data

- **`miscrits_updated.json`** — Extended/corrected dataset of all Miscrits including names, types, stats, speed, and rarity
- **`meta.json`** — Community meta tier rankings used to sort the draft pool
- **`Images_random_arena/`** — Reference sprites captured from Random Arena lobby screens, used by the scanner to match detected regions
- **`images_scraped_from_miscripedia/`** — Full Miscrit artwork sourced from the community wiki

---

## 🛠️ Tech Stack

| Layer          | Technology                              |
| -------------- | --------------------------------------- |
| Frontend       | HTML, CSS, Vanilla JavaScript           |
| Fonts          | Cinzel, Crimson Pro (Google Fonts)      |
| Data           | JSON                                    |
| Scraping       | Python                                  |
| Image matching | Canvas API + pixel histogram comparison |

---

## 🤝 Contributing

Contributions are welcome! Ideas for improvement:

- Add more Miscrit entries to the dataset
- Improve image matching accuracy
- Expand or refine the `meta.json` tier list
- Support for additional game modes

Feel free to open an issue or submit a pull request.

---

## 🏢 Built By

**Nyvora Vision Labs**

---

## 📄 License

This project is unofficial and fan-made. Miscrits is a property of Broken Bulb Studios. All game assets belong to their respective owners.
