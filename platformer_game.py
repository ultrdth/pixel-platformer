#!/usr/bin/env python3
"""
Pixel Platformer - Enhanced 3-Level Edition
A complete terminal platformer with 3 levels, power-ups, moving platforms, and sub-cell rendering.
"""

import curses
import sys
from dataclasses import dataclass
from typing import List, Tuple
import time
import json
import os
import random

@dataclass
class Vec2:
    x: float
    y: float

class Player:
    def __init__(self, x: float, y: float):
        self.pos = Vec2(x, y)
        self.vel = Vec2(0, 0)
        self.prev_pos = Vec2(x, y)
        self.on_ground = False
        self.width = 1
        self.height = 1
        
        # Tight, responsive movement tuning
        self.accel = 0.25       # Instant burst acceleration
        self.friction = 0.25    # Strong damping to stop instantly on release
        self.max_speed = 0.60   # Fast top speed
        self.jump_power = 0.85  # Clean jump height
        self.gravity = 0.04     # Snappy downward gravity
        self.max_fall = 1.00    # Solid terminal velocity
        
        self.coyote_frames = 0
        self.max_coyote = 8
        self.jump_held = False
        self.jump_reduce_gravity = 0.02
        
        self.shield = False
        self.shield_time = 0
        self.speed_boost = False
        self.speed_boost_time = 0
        self.invuln_time = 0
        
    def update(self, platforms: List['Platform'], move_dir: float, jump_pressed: bool, spikes: List['Spike']):
        self.prev_pos = Vec2(self.pos.x, self.pos.y)
        current_max_speed = self.max_speed * 1.4 if self.speed_boost else self.max_speed
        
        if move_dir != 0:
            self.vel.x += move_dir * self.accel
            if self.vel.x > current_max_speed:
                self.vel.x = current_max_speed
            elif self.vel.x < -current_max_speed:
                self.vel.x = -current_max_speed
        else:
            self.vel.x *= self.friction
            if abs(self.vel.x) < 0.01:
                self.vel.x = 0

        self.pos.x += self.vel.x
        self.pos.x = max(0, min(self.pos.x, 200))

        if self.jump_held and self.vel.y < 0:
            self.vel.y += self.jump_reduce_gravity
        else:
            self.vel.y += self.gravity
            
        if self.vel.y > self.max_fall:
            self.vel.y = self.max_fall
        
        self.pos.y += self.vel.y
        
        self.on_ground = False
        for platform in platforms:
            if platform.check_player_landing(self):
                self.on_ground = True
                self.vel.y = 0
                self.coyote_frames = self.max_coyote
                break
        
        if not self.on_ground:
            self.coyote_frames -= 1
        
        for spike in spikes:
            if spike.check_collision(self.pos):
                if self.shield:
                    self.shield = False
                    self.shield_time = 0
                elif self.invuln_time <= 0:
                    return True
        
        if self.shield_time > 0:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.shield = False
        
        if self.speed_boost_time > 0:
            self.speed_boost_time -= 1
            self.speed_boost = self.speed_boost_time > 0
        
        if self.invuln_time > 0:
            self.invuln_time -= 1
        
        if self.pos.y > 100:
            return True
        
        return False
    
    def jump(self):
        if self.on_ground or self.coyote_frames > 0:
            self.vel.y = -self.jump_power
            self.coyote_frames = 0
            self.jump_held = True
    
    def release_jump(self):
        self.jump_held = False
    
    def activate_shield(self):
        self.shield = True
        self.shield_time = 300
    
    def activate_speed_boost(self):
        self.speed_boost = True
        self.speed_boost_time = 200
    
    def get_rect(self) -> Tuple[int, int]:
        return (int(self.pos.x), int(self.pos.y))

class Platform:
    def __init__(self, x: int, y: int, width: int, char: str = "="):
        self.x = x
        self.y = y
        self.width = width
        self.char = char
    
    def check_player_landing(self, player: Player) -> bool:
        if not (player.pos.x + player.width > self.x and player.pos.x < self.x + self.width):
            return False
        
        prev_bottom = player.prev_pos.y + player.height
        curr_bottom = player.pos.y + player.height
        
        if player.vel.y >= 0 and prev_bottom <= self.y + 0.5 and curr_bottom >= self.y:
            player.pos.y = self.y - player.height
            return True
        return False

    def draw(self, win, offset: int = 0):
        x = int(self.x) - offset
        y = int(self.y)  # Cast y to integer explicitly for curses
        max_y, max_x = win.getmaxyx()
        if 0 <= y < max_y:
            for i in range(self.width):
                px = x + i
                if 0 <= px < max_x - 1:
                    win.addch(y, px, ord(self.char), curses.color_pair(1))

class MovingPlatform(Platform):
    def __init__(self, x: int, y: int, width: int, move_dist: int = 10, speed: float = 0.08):
        super().__init__(x, y, width, "-")
        self.start_x = x
        self.move_dist = move_dist
        self.speed = speed
        self.direction = 1
    
    def update(self):
        self.x += self.direction * self.speed
        if self.x <= self.start_x - self.move_dist or self.x >= self.start_x + self.move_dist:
            self.direction *= -1

class Spike:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def draw(self, win, offset: int = 0):
        x = self.x - offset
        max_y, max_x = win.getmaxyx()
        if 0 <= x < max_x - 1 and 0 <= self.y < max_y:
            win.addch(self.y, x, ord('^'), curses.color_pair(3))
    
    def check_collision(self, pos: Vec2) -> bool:
        return abs(int(pos.x) - self.x) < 1 and abs(int(pos.y) - self.y) < 1

class Enemy:
    def __init__(self, x: int, y: int, patrol_left: int, patrol_right: int):
        self.x = float(x)
        self.y = y
        self.direction = 1
        self.speed = 0.10
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
    
    def update(self):
        self.x += self.direction * self.speed
        if self.x <= self.patrol_left or self.x >= self.patrol_right:
            self.direction *= -1
    
    def draw(self, win, offset: int = 0):
        x = int(self.x) - offset
        max_y, max_x = win.getmaxyx()
        if 0 <= x < max_x - 1 and 0 <= self.y < max_y:
            win.addch(self.y, x, ord('E'), curses.color_pair(3))

class Collectible:
    def __init__(self, x: int, y: int, is_goal: bool = False):
        self.x = x
        self.y = y
        self.collected = False
        self.blink = 0
        self.is_goal = is_goal
    
    def update(self):
        self.blink = (self.blink + 1) % 30
    
    def draw(self, win, offset: int = 0):
        if not self.collected:
            x = self.x - offset
            max_y, max_x = win.getmaxyx()
            if 0 <= x < max_x - 1 and 0 <= self.y < max_y:
                if self.is_goal:
                    if self.blink < 25:
                        win.addch(self.y, x, ord('F'), curses.color_pair(2) | curses.A_BOLD)
                else:
                    if self.blink < 22:
                        win.addch(self.y, x, ord('★'), curses.color_pair(2))
    
    def check_collision(self, pos: Vec2) -> bool:
        if self.collected:
            return False
        return abs(int(pos.x) - self.x) <= 1 and abs(int(pos.y) - self.y) <= 1

class PowerUp:
    SHIELD = 1
    SPEED = 2
    
    def __init__(self, x: int, y: int, ptype: int):
        self.x = x
        self.y = y
        self.type = ptype
        self.collected = False
        self.blink = 0
    
    def update(self):
        self.blink = (self.blink + 1) % 20
    
    def draw(self, win, offset: int = 0):
        if not self.collected and self.blink < 15:
            x = self.x - offset
            max_y, max_x = win.getmaxyx()
            if 0 <= x < max_x - 1 and 0 <= self.y < max_y:
                char = 'S' if self.type == PowerUp.SHIELD else 'P'
                win.addch(self.y, x, ord(char), curses.color_pair(4))
    
    def check_collision(self, pos: Vec2) -> bool:
        if self.collected:
            return False
        return abs(int(pos.x) - self.x) <= 1 and abs(int(pos.y) - self.y) <= 1

class Level:
    def __init__(self, level_num: int):
        self.level_num = level_num
        self.platforms = []
        self.enemies = []
        self.collectibles = []
        self.powerups = []
        self.spikes = []
        self.goal = None
        self._generate_level(level_num)
    
    def _generate_level(self, level_num: int):
        if level_num == 1:
            self._level_1()
        elif level_num == 2:
            self._level_2()
        elif level_num == 3:
            self._level_3()

    def _level_1(self):
        self.platforms = [
            Platform(0, 20, 15), Platform(20, 18, 10), Platform(35, 15, 12),
            Platform(50, 16, 10), Platform(64, 12, 14), Platform(80, 17, 10), Platform(92, 13, 18),
        ]
        self.enemies = [Enemy(25, 17, 20, 35), Enemy(55, 15, 50, 70)]
        self.collectibles = [Collectible(26, 16), Collectible(40, 13), Collectible(70, 10), Collectible(85, 15)]
        self.powerups = [PowerUp(42, 13, PowerUp.SHIELD)]
        self.goal = Collectible(100, 11, is_goal=True)

    def _level_2(self):
        self.platforms = [
            Platform(0, 20, 12), Platform(15, 17, 8), MovingPlatform(30, 15, 10, move_dist=8),
            Platform(48, 14, 10), Platform(62, 11, 12), MovingPlatform(80, 16, 8, move_dist=6), Platform(100, 12, 15),
        ]
        self.spikes = [Spike(20, 16), Spike(55, 13), Spike(70, 10), Spike(85, 15)]
        self.enemies = [Enemy(20, 18, 15, 40), Enemy(60, 12, 55, 75)]
        self.collectibles = [Collectible(18, 16), Collectible(45, 12), Collectible(65, 9), Collectible(95, 10)]
        self.powerups = [PowerUp(35, 13, PowerUp.SPEED), PowerUp(65, 9, PowerUp.SHIELD)]
        self.goal = Collectible(115, 10, is_goal=True)

    def _level_3(self):
        self.platforms = [
            Platform(0, 20, 10), Platform(15, 18, 8), MovingPlatform(28, 16, 9, move_dist=10, speed=0.07),
            Platform(42, 13, 8), Platform(55, 11, 10), MovingPlatform(70, 14, 10, move_dist=8, speed=0.06),
            Platform(88, 10, 12), Platform(105, 15, 10), Platform(120, 11, 12),
        ]
        self.spikes = [
            Spike(20, 17), Spike(35, 13), Spike(60, 10),
            Spike(75, 13), Spike(95, 9), Spike(110, 14),
        ]
        self.enemies = [
            Enemy(22, 17, 15, 35), Enemy(50, 12, 45, 65), Enemy(90, 11, 85, 110),
        ]
        self.collectibles = [
            Collectible(18, 17), Collectible(32, 14), Collectible(48, 11),
            Collectible(68, 12), Collectible(85, 8), Collectible(110, 9),
        ]
        self.powerups = [
            PowerUp(45, 11, PowerUp.SHIELD), PowerUp(75, 12, PowerUp.SPEED), PowerUp(100, 13, PowerUp.SHIELD),
        ]
        self.goal = Collectible(125, 9, is_goal=True)

class Game:
    def __init__(self):
        self.level_num = 1
        self.level = Level(self.level_num)
        self.player = Player(5, 15)
        self.camera_x = 0.0
        self.score = 0
        self.lives = 3
        self.won = False
        self.game_over = False
        self.paused = False
        self.screen_shake = 0

    def next_level(self):
        if self.level_num < 3:
            self.level_num += 1
            self.level = Level(self.level_num)
            self.player = Player(5, 15)
            self.won = False
        else:
            self.won = True
            self.game_over = True

    def update(self, move_dir: float, jump_pressed: bool, jump_released: bool):
        if self.paused or self.won or self.game_over:
            return
        
        if jump_pressed: self.player.jump()
        if jump_released: self.player.release_jump()
        
        for platform in self.level.platforms:
            if isinstance(platform, MovingPlatform): platform.update()
        for enemy in self.level.enemies: enemy.update()
        for collectible in self.level.collectibles: collectible.update()
        for powerup in self.level.powerups: powerup.update()
        if self.level.goal: self.level.goal.update()
        
        took_damage = self.player.update(self.level.platforms, move_dir, jump_pressed, self.level.spikes)
        if took_damage:
            self.lives -= 1
            self.player.invuln_time = 60
            self.screen_shake = 10
            if self.lives <= 0:
                self.game_over = True
            else:
                self.player.pos = Vec2(5, 15)
                self.player.vel = Vec2(0, 0)
        
        for collectible in self.level.collectibles:
            if collectible.check_collision(self.player.pos): self.score += 10
        for powerup in self.level.powerups:
            if powerup.check_collision(self.player.pos):
                powerup.collected = True
                if powerup.type == PowerUp.SHIELD: self.player.activate_shield()
                elif powerup.type == PowerUp.SPEED: self.player.activate_speed_boost()
        
        for enemy in self.level.enemies:
            px, py = self.player.get_rect()
            if abs(px - int(enemy.x)) < 1 and abs(py - enemy.y) < 1:
                if self.player.shield:
                    self.player.shield = False
                    self.screen_shake = 5
                elif self.player.invuln_time <= 0:
                    self.lives -= 1
                    self.player.invuln_time = 60
                    self.screen_shake = 10
                    if self.lives <= 0: self.game_over = True
                    else:
                        self.player.pos = Vec2(5, 15)
                        self.player.vel = Vec2(0, 0)
        
        if self.level.goal and self.level.goal.check_collision(self.player.pos):
            self.won = True
        
        target_camera = max(0, self.player.pos.x - 20)
        self.camera_x += (target_camera - self.camera_x) * 0.12
        if self.screen_shake > 0: self.screen_shake -= 1

    def draw(self, win):
        win.erase()
        height, width = win.getmaxyx()
        offset = int(self.camera_x)
        
        shake_offset = random.randint(-1, 1) if self.screen_shake > 0 else 0
        
        for platform in self.level.platforms: platform.draw(win, offset)
        for spike in self.level.spikes: spike.draw(win, offset)
        if self.level.goal: self.level.goal.draw(win, offset)
        for collectible in self.level.collectibles: collectible.draw(win, offset)
        for powerup in self.level.powerups: powerup.draw(win, offset)
        for enemy in self.level.enemies: enemy.draw(win, offset)
        
        # --- Sub-Cell Player Drawing ---
        sub_y = int(self.player.pos.y * 2)
        cell_y = sub_y // 2
        is_bottom_half = (sub_y % 2 == 1)
        px = int(self.player.pos.x) - offset + shake_offset
        
        if 0 <= px < width - 1 and 0 <= cell_y < height:
            char = '▄' if is_bottom_half else '▀'
            if self.player.shield:
                win.addch(cell_y, px, ord(char), curses.color_pair(4) | curses.A_BOLD)
            elif self.player.invuln_time > 0 and self.player.invuln_time % 10 > 5:
                pass
            else:
                win.addch(cell_y, px, ord(char), curses.color_pair(4))
        
        hud1 = f" Level {self.level_num} | Score: {self.score} | Lives: {self.lives} "
        hud2 = f" P: Pause | Arrow/A/D: Move | Space: Jump | Q: Quit "
        win.addstr(0, 0, hud1[:width-1], curses.A_REVERSE)
        win.addstr(1, 0, hud2[:width-1])
        
        if self.won:
            if self.level_num < 3:
                msg = f" ★ LEVEL {self.level_num} COMPLETE! Press ANY KEY for Next Level ★ "
            else:
                msg = f" ★ YOU BEAT THE GAME! Final Score: {self.score} ★ "
            win.addstr(height // 2, max(0, (width - len(msg)) // 2), msg, curses.A_BOLD | curses.color_pair(2))

        if self.game_over and self.lives <= 0:
            msg = " GAME OVER - Press Any Key "
            win.addstr(height // 2, max(0, (width - len(msg)) // 2), msg, curses.A_BOLD | curses.color_pair(3))

        win.refresh()

def show_menu(stdscr):
    while True:
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        y = height // 2
        stdscr.addstr(y - 3, max(0, (width - 16) // 2), "PIXEL PLATFORMER", curses.A_BOLD | curses.color_pair(4))
        stdscr.addstr(y, max(0, (width - 10) // 2), "[P] Play")
        stdscr.addstr(y + 1, max(0, (width - 10) // 2), "[Q] Quit")
        stdscr.refresh()
        stdscr.nodelay(False)
        key = stdscr.getch()
        if key in (ord('P'), ord('p')): return True
        if key in (ord('Q'), ord('q')): return False

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)
    curses.init_pair(4, curses.COLOR_CYAN, -1)
    curses.curs_set(0)
    
    if not show_menu(stdscr): return
    curses.flushinp()
    
    stdscr.nodelay(True)
    stdscr.timeout(16)  # ~60 FPS
    
    game = Game()
    target_fps = 60
    frame_time = 1.0 / target_fps
    
    current_dir = 0.0
    jump_held = False
    last_move_time = 0.0
    last_jump_time = 0.0
    
    while True:
        start_loop = time.time()
        jump_pressed = False
        jump_released = False
        
        key = stdscr.getch()
        while key != -1:
            if key in (ord('q'), ord('Q')): return
            elif key in (ord('p'), ord('P')): game.paused = not game.paused
            elif key in (curses.KEY_LEFT, ord('a'), ord('A')):
                current_dir = -1.0
                last_move_time = time.time()
            elif key in (curses.KEY_RIGHT, ord('d'), ord('D')):
                current_dir = 1.0
                last_move_time = time.time()
            elif key in (curses.KEY_UP, ord('w'), ord('W'), ord(' ')):
                last_jump_time = time.time()
                if current_dir != 0: last_move_time = time.time()
                if not jump_held:
                    jump_pressed = True
                    jump_held = True
            key = stdscr.getch()
        
        if jump_held and time.time() - last_jump_time > 0.08:
            jump_released = True
            jump_held = False
        
        if time.time() - last_move_time > 0.08:
            current_dir = 0.0
        
        game.update(current_dir, jump_pressed, jump_released)
        game.draw(stdscr)
        
        # Smooth Level Transition
        if game.won:
            stdscr.nodelay(False)
            stdscr.getch()
            curses.flushinp()
            if game.level_num < 3:
                game.next_level()
                stdscr.nodelay(True)
                stdscr.timeout(16)
            else:
                return
        
        if game.game_over and game.lives <= 0:
            stdscr.nodelay(False)
            stdscr.getch()
            return
        
        elapsed = time.time() - start_loop
        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass