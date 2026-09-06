# Pixel Platformer - Enhanced Edition 🎮

A feature-rich terminal platformer with multiple levels, power-ups, obstacles, and challenging gameplay.

![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows%20WSL-orange.svg)

## 🎮 Features

### Core Gameplay
- ⭐ **3 Progressive Levels** - From beginner to expert
- 🏃 **Smooth Physics** - Acceleration, friction, gravity simulation
- 🪂 **Variable Jump Height** - Hold space longer for higher jumps
- ⏱️ **Coyote Time** - Jump briefly after leaving platforms
- 💫 **Screen Shake** - Visual feedback on hits and events

### Level Elements
- **Platforms** - Static platforms to jump across
- **Moving Platforms** - Platforms that move side-to-side
- **Spikes (^)** - Instant damage obstacles
- **Enemies (E)** - Patrol and knock you back
- **Collectibles (★)** - Each worth +10 points
- **Flag (F)** - Reach to complete the level

### Power-ups
- **Shield (S)** - Absorbs one hit (glowing borders)
- **Speed Boost (P)** - 50% faster movement for limited time

### Game Systems
- 🛡️ **Lives System** - Start with 3 lives
- 📊 **Scoring** - Track points per level
- 💾 **High Scores** - Saved to `highscores.json`
- ⏸️ **Pause/Resume** - Press P anytime
- 🎨 **Color Support** - Vibrant ASCII visuals
- 📱 **Main Menu** - Instructions included

---

## 🕹️ Controls

```
Arrow Keys / A & D  - Move left/right
Space / W           - Jump (hold for height)
P                   - Pause/Resume
Q                   - Quit to menu
```

---

## 🚀 Getting Started

### Requirements
- Python 3.6+
- Terminal with color support
- Linux, macOS, or Windows (with Windows Terminal/WSL)

### Installation & Play

```bash
# Clone the repo
git clone https://github.com/ultrdth/pixel-platformer.git
cd pixel-platformer

# Run the game
python3 platformer_game.py
```

### First Time Playing?
1. Start at main menu
2. Press [I] to see instructions
3. Press [P] to play
4. Beat all 3 levels!

---

## 🎯 Level Progression

### Level 1: Tutorial
- Gentle introduction with basic platforms
- Simple enemy patterns
- 4 collectibles
- 1 shield power-up
- No moving platforms or spikes

### Level 2: Intermediate
- Moving platforms introduced
- Spike obstacles
- More complex enemy patterns
- Speed boost power-up
- 5 collectibles

### Level 3: Expert
- Multiple moving platforms
- Dense spike fields
- 3 enemies patrolling
- Strategic power-up placement
- 6 collectibles

---

## 📊 Game Mechanics

### Physics
- **Acceleration** - Smooth movement buildup
- **Friction** - Natural deceleration
- **Gravity** - Realistic falling
- **Terminal Velocity** - Max fall speed

### Damage System
- **Hit by enemy:** -1 life, 5-second invulnerability
- **Hit by spike:** -1 life, instant reset
- **Shield powerup:** Blocks one hit
- **Fall off bottom:** -1 life

### Power-ups
- **Shield** - Lasts 5 seconds, blocks next hit
- **Speed Boost** - Lasts ~3 seconds, 50% faster movement
- Spawn on platforms, grab to activate

---

## 🗺️ Level Map Visualizer

The `render_map.py` utility lets you view full ASCII maps of all levels without running the game. Perfect for level design, planning changes, or understanding enemy/platform placement!

### Usage

```bash
# View maps of all 3 levels in terminal
python3 render_map.py
```

### Output Example
The visualizer displays all level elements with a legend:
- `=` Static platforms
- `-` Moving platforms
- `^` Spikes
- `★` Collectibles (stars)
- `S/P` Power-ups (Shield/Speed)
- `E` Enemies
- `F` Goal flag

### Use Cases
- **Design new levels** - See exact platform placement
- **Test level changes** - Visualize before playing
- **Debug collision issues** - Check platform coordinates
- **Plan speedruns** - Study enemy patterns and platform layouts
- **Document levels** - Screenshot maps for guides/wikis

### Example Output
```
=======================================================================================================================================
                                   LEVEL 1 VISUAL MAP
  Legend:  [=] Platform  [-] Moving Platform  [^] Spike  [★] Star  [S/P] Power-up  [E] Enemy  [F] Goal
=======================================================================================================================================
00 |                                                                                                                                        
01 |                                                                                                                                        
02 |                                                                                                                                        
03 |                                                                                                                                        
04 |                                                                                                                                        
05 |                                                                                                                                        
06 |                                                                                                                                        
07 |                                                                                                                                        
08 |                                                                                                                                        
09 |                                                                                                                                        
10 |                                                                       ★                                                                
11 |                                                                                                     F                                  
12 |                                                                 ==============                                                         
13 |                                         ★ S                                                 ==================                         
14 |                                                                                                                                        
15 |                                    ============        E                             ★                                                 
16 |                           ★                       ==========                                                                           
17 |                          E                                                      ==========                                             
18 |                     ==========                                                                                                         
19 |                                                                                                                                        
20 | ===============                                                                                                                        
21 |
...
```

---

## 📈 Strategy Tips

- **Collectibles Optional** - You can skip stars and just reach the flag
- **Plan Jumps** - Watch enemy patterns before committing
- **Use Power-ups Wisely** - Shields are most valuable near spikes
- **Speed Boost for Jumping** - Helps cross large gaps
- **Coyote Time is Forgiving** - Jump even after stepping off edges
- **Watch Moving Platforms** - Time jumps to match their movement

---

## 🏆 Scoring

- Each collectible: **+10 points**
- Each level completed: **Stored in high scores**
- Bonus: Collect all stars for maximum score

High scores are saved to `highscores.json` automatically.

---

## 🎨 Visual Reference

| Character | Meaning |
|-----------|---------|
| `@` | Player |
| `=` | Static Platform |
| `-` | Moving Platform |
| `E` | Enemy |
| `^` | Spike |
| `★` | Collectible |
| `F` | Flag/Goal |
| `S` | Shield powerup |
| `P` | Speed powerup |

---

## 🔧 Customization

### Physics Tuning

You can tweak physics values in the `Player` class:
```python
self.accel = 0.25           # Acceleration (higher = snappier)
self.friction = 0.25        # Damping (higher = stops faster)
self.max_speed = 0.60       # Top movement speed
self.jump_power = 0.85      # Jump height
self.gravity = 0.04         # Falling speed
self.max_fall = 1.00        # Terminal velocity
```

### Level Design

Modify level design in the `Level` class methods:
```python
def _level_1(self):
    self.platforms = [...]      # Add/remove platforms
    self.enemies = [...]        # Adjust enemy positions
    self.collectibles = [...]   # Place stars
    self.spikes = [...]         # Add spike obstacles
    self.powerups = [...]       # Place power-ups
```

Use `render_map.py` to visualize your changes immediately!

---

## 💡 Future Ideas

- Level editor UI
- Leaderboards (online scoring)
- More enemy types (flying, bouncing)
- Double jump power-up
- Dash ability
- Boss battles
- Sound effects (terminal beeps)
- Checkpoint system
- Time trial mode
- Custom themes/color schemes

---

## 🐛 Troubleshooting

**Game too fast/slow?**
- Adjust `target_fps` in main() function
- Try 30 FPS (slower) or 50 FPS (faster)
- Default is 40 FPS

**Colors not showing?**
- Terminal needs ANSI color support
- Try `xterm-256color` terminal emulator
- Update your terminal application

**Jumps feel weird?**
- Tweak `gravity`, `jump_power`, `accel` values
- Lower gravity = floatier, higher gravity = heavier
- Use render_map.py to check platform placement

**Enemies/platforms not where I expect?**
- Use `render_map.py` to visualize exact positions
- Check coordinate values in Level class

---

## 📁 Project Structure

```text
pixel-platformer/
├── LICENSE                  # MIT License
├── README.md                # Project documentation
├── platformer_game.py       # Main game executable
├── render_map.py            # Level visualizer utility tool
└── highscores.json          # Auto-generated high score tracking
```

---

## 📝 License

MIT License - Feel free to modify and share!

---

## 🤝 Contributing

Found a bug or have a feature idea? Feel free to:
- Report issues on GitHub
- Submit pull requests
- Suggest improvements

---

**Made with ❤️ in the terminal.** 🎮

Challenge yourself through all 3 levels and aim for maximum score!

**Play now:** `python3 platformer_game.py`  
**Visualize levels:** `python3 render_map.py`
