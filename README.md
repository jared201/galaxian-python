# Galaxian

A retro-style Galaxian arcade game built with Python and Pygame CE.

## Features
- Classic 8-bit arcade gameplay.
- Enemy formation with "hive" movement.
- Dynamic diving maneuvers and AI logic.
- Scoring system with bonuses for diving enemies and flagship escorts.
- Scrolling starfield background.
- Scaled virtual resolution for a pixel-perfect look.

## Requirements
- Python 3.x
- [Pygame CE](https://github.com/pygame-community/pygame-ce) (Community Edition)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd Galaxian
   ```

2. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

Launch the game by running the `main.py` script:

```bash
python main.py
```

## Controls

- **Left/Right Arrow Keys:** Move the Galaxip ship horizontally.
- **Spacebar:** Shoot (only one bullet can be active at a time, consistent with the original arcade game).
- **Any Key:** Start the game from the title screen or restart after a "Game Over".

## Scoring

- **Drones (Purple):** 30 points (60 when diving).
- **Emissaries (Red):** 40 points (80 when diving).
- **Hornets (Yellow):** 50 points (100 when diving).
- **Flagships (White):** 60 points (120 when diving).
- **Special Bonus:** Destroying a Flagship along with its two Hornet escorts during a single dive awards a significant point bonus (up to 800 extra points).
