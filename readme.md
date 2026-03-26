# 🎮 Miscrits-Random-Arena-Helper

A browser-based tool for **Miscrits** players that analyzes Random Arena team pickup lobbies using image recognition and recommends the best possible team composition.

---

## 🧩 What It Does

1. **Screenshot Analysis** — Upload a screenshot of a Random Arena team pickup lobby and the tool automatically identifies each Miscrit's name and type using visual recognition.
2. **Team Recommendation** — Based on the detected Miscrits, the Oracle suggests optimal team compositions ranked by synergy, type coverage, rarity, and speed.

---

## ✨ Features

- 📸 **Drag-and-drop screenshot upload** — supports image pasting directly into the browser
- 🔍 **Visual Miscrit detection** — maps arena lobby sprites to known Miscrit data
- 🏆 **Team builder** — generates and ranks multiple team options with synergy scoring
- 📊 **Stat mini-bars** — view HP, Attack, Defense, and Speed at a glance for each candidate
- 🏷️ **Type & rarity tags** — instantly see elemental type and rarity for every Miscrit
- 👑 **Lead recommendation** — highlights the best lead Miscrit for each suggested team
- 📋 **One-click copy** — copy any team lineup to clipboard instantly
- 🌑 **Dark fantasy UI** — styled with a rich RPG aesthetic using Cinzel and Crimson Pro fonts

---

## 📁 Repository Structure

```
Miscrits/
├── index.html                        # Main single-file web application
├── miscrits.json                     # Base Miscrit dataset
├── miscrits_updated.json             # Updated Miscrit dataset with latest entries
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

2. **Open in your browser:**

   ```bash
   # Simply open the file in any modern browser
   open index.html
   ```

   Or drag `index.html` directly into your browser window.

3. **Use the tool:**
   - Take a screenshot of your Random Arena lobby in Miscrits
   - Drag and drop (or paste) the screenshot into the upload zone
   - Click **Scan** and wait for detection to complete
   - Browse the suggested team compositions and copy your favorite

---

## 🐍 Python Scripts

The `SCRIPTS/` folder contains Python utilities used for data preparation:

- Scraping Miscrit images from Miscripedia (the Miscrits wiki)
- Processing and formatting the Miscrit dataset into JSON
- Any preprocessing needed for arena sprite matching

These scripts are used for development/data updates and are not required to run the web app.

---

## 🗃️ Data

- **`miscrits.json`** — Core dataset of all Miscrits including names, types, stats, and rarity
- **`miscrits_updated.json`** — Extended/corrected version of the dataset
- **`Images_random_arena/`** — Reference sprites captured from Random Arena lobby screens, used by the scanner to match detected regions
- **`images_scraped_from_miscripedia/`** — Full Miscrit artwork sourced from the community wiki

---

## 🛠️ Tech Stack

| Layer          | Technology                         |
| -------------- | ---------------------------------- |
| Frontend       | HTML, CSS, Vanilla JavaScript      |
| Fonts          | Cinzel, Crimson Pro (Google Fonts) |
| Data           | JSON                               |
| Scraping       | Python                             |
| Image matching | Canvas API + pixel comparison      |

---

## 🤝 Contributing

Contributions are welcome! Ideas for improvement:

- Add more Miscrit entries to the dataset
- Improve image matching accuracy
- Add win-rate statistics or meta-tier rankings
- Support for additional game modes

Feel free to open an issue or submit a pull request.

---

## 📄 License

This project is unofficial and fan-made. Miscrits is a property of Broken Bulb Studios. All game assets belong to their respective owners.
