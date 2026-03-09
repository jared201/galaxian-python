# Galaxian: Python Development Design Strategy

This document outlines a strategy for developing a Galaxian-style arcade game using Python and the Pygame library.

## 1. Core Technology Selection
- **Programming Language:** Python 3.x
- **Gaming Library:** **Pygame CE** (Community Edition) for its performance improvements and robust features for 2D arcade games.
- **Why?** Pygame provides simplified access to hardware (graphics, sound, input) and is the industry standard for 2D games in Python.

## 2. Architecture: Object-Oriented Design
To manage complexity, the game will follow an OOP approach:

### A. Game Manager (`Game` class)
- Manages the main game loop (Handle Events -> Update -> Draw).
- Handles state transitions (Main Menu, Playing, Game Over).
- Manages global resources (Screen surface, Clock, High scores).

### B. Entity System (`Sprite` based)
- **Base Entity:** All game objects (Player, Enemy, Projectile) inherit from `pygame.sprite.Sprite`.
- **Player (Galaxip):** Handles horizontal movement, single-bullet cooldowns, and life management.
- **Enemy (Aliens):** Handles movement patterns, formation positioning, and the "diving" attack logic.
    - **Drone:** Basic purple aliens.
    - **Emissary:** Red aliens.
    - **Hornets:** Yellow aliens.
    - **Flagships (Boss):** Top-row aliens that dive with two escorts.
- **Projectile:** Handles linear movement and screen-boundary cleanup.

## 3. Key Systems and Mechanics

### A. Formation & Movement
- **The Hive:** Enemies should exist in a grid-based formation (Rank and File).
- **The Sway:** The entire formation oscillates horizontally while slowly descending, creating a "breathing" effect.
- **Diving Maneuvers:** 
    - Random selection of enemies break formation.
    - Drones/Emissaries dive in simple loops or arcs.
    - Flagships dive accompanied by two escorting aliens, creating a more dangerous threat.
    - Enemies fire projectiles only during dives.
- **AI Logic:** Use state machines (Formation, Diving, Returning) and Bezier curves for smooth flight paths.

### B. Scoring System
- Base points for destroying enemies in formation.
- Double points for destroying enemies while they are diving.
- Special bonus for destroying a Flagship and its escorts in a single dive.
### C. Collision Detection
- Utilize `pygame.sprite.groupcollide` for efficient management of many-to-many collisions (e.g., Player Bullets vs. Enemies).
- Use circular or mask-based collisions for more precise hitboxes on the Player ship.

### D. Asset Management
- **Graphics:** Use 8-bit style pixel art. Implement a `SpriteSheet` loader to manage animations efficiently.
- **Sound:** Utilize `pygame.mixer` for retro "pew-pew" effects, explosions, and the continuous background hum of the alien fleet.

## 4. Development Phases

1. **Phase 1: Basic Mechanics**
   - Setup window, player movement, and simple bullet firing.
2. **Phase 2: The Fleet**
   - Implement the enemy formation logic and basic lateral movement.
3. **Phase 3: Enemy AI**
   - Script the "diving" behavior and enemy weapon firing.
4. **Phase 4: Game Flow**
   - Add level transitions, scoring system, and health/lives.
5. **Phase 5: Polish & SFX**
   - Add background starfield (parallax scrolling), explosion animations, and audio effects.

## 5. Challenges and Solutions
- **Performance:** For many entities, use `pygame.sprite.LayeredUpdates` to optimize rendering.
- **Resolution:** Use a fixed virtual resolution (e.g., 224x288, original arcade ratio) and scale it up to maintain the pixel-perfect retro look on modern monitors.
