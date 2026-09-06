#!/usr/bin/env python3
"""
Level Visualizer - Render full ASCII minimaps for all levels
"""

from platformer_game import Level, MovingPlatform, PowerUp

def render_level_map(level_num: int):
    level = Level(level_num)
    
    # Grid dimensions (max width of levels is ~140, height ~25)
    max_x = 135
    max_y = 22
    
    # Create empty canvas filled with spaces
    grid = [[" " for _ in range(max_x)] for _ in range(max_y)]
    
    # 1. Draw Static Platforms
    for p in level.platforms:
        if not isinstance(p, MovingPlatform):
            for i in range(p.width):
                if 0 <= p.x + i < max_x and 0 <= p.y < max_y:
                    grid[p.y][p.x + i] = "="
                    
    # 2. Draw Moving Platforms
    for p in level.platforms:
        if isinstance(p, MovingPlatform):
            for i in range(p.width):
                if 0 <= int(p.x) + i < max_x and 0 <= p.y < max_y:
                    grid[p.y][int(p.x) + i] = "-"

    # 3. Draw Spikes
    for s in level.spikes:
        if 0 <= s.x < max_x and 0 <= s.y < max_y:
            grid[s.y][s.x] = "^"

    # 4. Draw Collectibles
    for c in level.collectibles:
        if 0 <= c.x < max_x and 0 <= c.y < max_y:
            grid[c.y][c.x] = "★"

    # 5. Draw Power-Ups
    for pu in level.powerups:
        if 0 <= pu.x < max_x and 0 <= pu.y < max_y:
            grid[pu.y][pu.x] = "S" if pu.type == PowerUp.SHIELD else "P"

    # 6. Draw Enemies
    for e in level.enemies:
        ex = int(e.x)
        if 0 <= ex < max_x and 0 <= e.y < max_y:
            grid[e.y][ex] = "E"

    # 7. Draw Goal
    if level.goal and 0 <= level.goal.x < max_x and 0 <= level.goal.y < max_y:
        grid[level.goal.y][level.goal.x] = "F"

    # Print Header
    print("\n" + "=" * max_x)
    print(f"                                   LEVEL {level_num} VISUAL MAP")
    print("  Legend:  [=] Platform  [-] Moving Platform  [^] Spike  [★] Star  [S/P] Power-up  [E] Enemy  [F] Goal")
    print("=" * max_x)

    # Print Grid with Y-axis markers
    for y in range(max_y):
        row_str = "".join(grid[y])
        print(f"{y:02d} | {row_str}")

if __name__ == "__main__":
    for level_id in range(1, 4):
        render_level_map(level_id)
