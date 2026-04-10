# GeoGrid Helper

An analytical companion tool for players of [GeoGrid](https://www.geogridgame.com/) that helps identify valid countries based on multiple simultaneous category filters.

Built to streamline the decision-making process by narrowing down country options through an interactive filtering system.

---

## Features

- 🌍 Filter countries by multiple GeoGrid categories simultaneously  
- 🔍 Instantly view all valid matching countries  
- 📊 Uses a structured country dataset with rich metadata  
- ⚡ Fast local processing for real-time filtering  
- 🧠 Designed to improve strategy and optimize guesses  
- 🛠 Modular dataset/build scripts for validation and updates  

---

## How It Works

GeoGrid Helper allows users to select from available GeoGrid-style categories and applies those filters across a country dataset to return every valid country matching the selected criteria.

This makes it easier to:

- Analyze intersections between multiple country traits  
- Narrow down difficult GeoGrid answers  
- Learn country patterns and improve game knowledge over time  

---

## Tech Stack

- **Python**
- **Pandas**
- Custom country dataset processing scripts
- Local desktop execution via batch/VBS launcher

---

## Project Structure

```bash
GeoGrid-Helper/
│
├── app.py                     # Main application
├── build_dataset.py           # Dataset generation / preprocessing
├── validate_dataset.py        # Dataset validation checks
├── flag_color_sets.py         # Country flag/color logic
├── build_flag_color_sets.py   # Flag color preprocessing
├── countries_master.csv       # Master country dataset
├── geogrid.bat               # Windows launcher
└── GeoGrid.vbs               # Silent launcher wrapper
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/charliezan/GeoGrid-Helper.git
cd GeoGrid-Helper
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the application with:

```bash
python app.py
```

Or use the provided launcher:

```bash
geogrid.bat
```

---

## Why I Built This

GeoGrid combines geography knowledge with logic and pattern recognition.  
I built this project to create a smarter way to analyze the puzzle by turning country metadata into an interactive filtering engine.

It also served as a practical exercise in:

- Data modeling  
- Dataset validation  
- UI/UX for filtering systems  
- Python scripting and automation  

---

## Future Improvements

- [ ] Add more GeoGrid-compatible categories  
- [ ] Improve UI/UX design  
- [ ] Add probability/scoring suggestions  
- [ ] Support automatic puzzle import  
- [ ] Deploy web-based version  

---

## Disclaimer

This project is an independent fan-made helper tool and is **not affiliated with GeoGrid**.

It is intended for educational, analytical, and entertainment purposes.

---

## Author

**Matias Camacho**

GitHub: [@charliezan](https://github.com/charliezan)

---
