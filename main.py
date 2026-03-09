import pygame
import sys

# Constants
VIRTUAL_WIDTH = 224
VIRTUAL_HEIGHT = 288
SCALE = 3
SCREEN_WIDTH = VIRTUAL_WIDTH * SCALE
SCREEN_HEIGHT = VIRTUAL_HEIGHT * SCALE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color):
        super().__init__()
        self.image = pygame.Surface((2, 6))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > VIRTUAL_HEIGHT:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    FORMATION = 0
    DIVING = 1
    RETURNING = 2

    def __init__(self, x, y, color, points, row, col):
        super().__init__()
        self.image = pygame.Surface((13, 13), pygame.SRCALPHA)
        # Draw a simple triangular ship
        pygame.draw.polygon(self.image, color, [(6, 0), (12, 12), (0, 12)])
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.points = points
        self.row = row
        self.col = col
        self.color = color
        self.state = Enemy.FORMATION
        self.offset_x = x
        self.offset_y = y
        self.dive_speed = 1.5
        self.dive_vx = 0
        self.dive_vy = 0
        self.shoot_cooldown = 0

    def start_dive(self, escorts=None):
        self.state = Enemy.DIVING
        self.dive_vy = self.dive_speed
        self.escorts = escorts if escorts else []
        
        # Define Bezier points for a smooth dive path
        # Points: Start, Mid1, Mid2, End (bottom of screen)
        import random
        start_x = self.rect.x
        start_y = self.rect.y
        mid1_x = random.randint(0, VIRTUAL_WIDTH)
        mid1_y = start_y + 50
        mid2_x = random.randint(0, VIRTUAL_WIDTH)
        mid2_y = start_y + 150
        end_x = random.randint(0, VIRTUAL_WIDTH)
        end_y = VIRTUAL_HEIGHT + 20
        
        self.path_points = [(start_x, start_y), (mid1_x, mid1_y), (mid2_x, mid2_y), (end_x, end_y)]
        self.path_t = 0.0
        self.path_speed = 0.015 # Controls how fast it follows the curve

        for e in self.escorts:
            e.start_dive()

    def get_bezier_point(self, t, points):
        # Cubic Bezier: (1-t)^3*P0 + 3*(1-t)^2*t*P1 + 3*(1-t)*t^2*P2 + t^3*P3
        p0, p1, p2, p3 = points
        x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
        return x, y

    def shoot(self):
        if self.state == Enemy.DIVING and self.shoot_cooldown <= 0:
            import random
            if random.random() < 0.01: # Small chance to shoot each frame while diving
                self.shoot_cooldown = 60
                return Projectile(self.rect.centerx, self.rect.bottom, 3, YELLOW)
        return None

    def update(self, formation_x, formation_y):
        if self.state == Enemy.FORMATION:
            self.rect.x = formation_x + self.offset_x
            self.rect.y = formation_y + self.offset_y
        elif self.state == Enemy.DIVING:
            self.path_t += self.path_speed
            if self.path_t >= 1.0:
                self.rect.bottom = 0
                self.state = Enemy.RETURNING
            else:
                new_x, new_y = self.get_bezier_point(self.path_t, self.path_points)
                self.rect.x = new_x
                self.rect.y = new_y
        elif self.state == Enemy.RETURNING:
            target_x = formation_x + self.offset_x
            target_y = formation_y + self.offset_y
            dx = target_x - self.rect.x
            dy = target_y - self.rect.y
            dist = (dx**2 + dy**2)**0.5
            if dist < 5:
                self.state = Enemy.FORMATION
                self.rect.x = target_x
                self.rect.y = target_y
            else:
                self.rect.x += dx / dist * self.dive_speed
                self.rect.y += dy / dist * self.dive_speed
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

class Drone(Enemy):
    def __init__(self, x, y, row, col):
        super().__init__(x, y, PURPLE, 30, row, col)

class Emissary(Enemy):
    def __init__(self, x, y, row, col):
        super().__init__(x, y, RED, 40, row, col)

class Hornet(Enemy):
    def __init__(self, x, y, row, col):
        super().__init__(x, y, YELLOW, 50, row, col)

class Flagship(Enemy):
    def __init__(self, x, y, row, col):
        super().__init__(x, y, WHITE, 60, row, col)

    def start_dive(self, escorts=[]):
        super().start_dive(escorts)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.color = color
        self.timer = 0
        self.duration = 30 # Slightly longer
        self.particles = []
        import random
        for _ in range(12):
            self.particles.append({
                'x': 10, 'y': 10,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'size': random.randint(1, 3)
            })

    def update(self):
        self.timer += 1
        if self.timer >= self.duration:
            self.kill()
        else:
            self.image.fill((0, 0, 0, 0))
            alpha = int(255 * (1 - self.timer / self.duration))
            for p in self.particles:
                p['x'] += p['vx']
                p['y'] += p['vy']
                pygame.draw.rect(self.image, (*self.color, alpha), (p['x'], p['y'], p['size'], p['size']))

class Galaxip(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        # Draw a simple ship shape
        pygame.draw.polygon(self.image, GREEN, [(7, 0), (14, 14), (0, 14)])
        self.rect = self.image.get_rect(midbottom=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT - 10))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 2
        self.cooldown = 0
        self.lives = 3

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < VIRTUAL_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_SPACE] and self.cooldown == 0:
            self.shoot()

    def shoot(self):
        # In Galaxian, usually only one bullet at a time from player
        self.cooldown = 15
        return Projectile(self.rect.centerx, self.rect.top, -4, WHITE)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

class Star:
    def __init__(self):
        import random
        self.random = random
        self.reset()
        self.y = self.random.randint(0, VIRTUAL_HEIGHT)

    def reset(self):
        self.x = self.random.randint(0, VIRTUAL_WIDTH)
        self.y = 0
        self.layer = self.random.randint(1, 3)
        self.speed = self.layer * 0.2
        c = 85 * self.layer
        self.color = (c, c, c)

    def update(self):
        self.y += self.speed
        if self.y > VIRTUAL_HEIGHT:
            self.reset()

class Game:
    def __init__(self):
        pygame.init()
        # Initialize mixer for sound setup (even if no files provided)
        try:
            pygame.mixer.init()
        except:
            pass
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        pygame.display.set_caption("Galaxian")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.player_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        
        self.player = Galaxip()
        self.all_sprites.add(self.player)
        
        self.score = 0
        self.level = 1
        self.font = pygame.font.SysFont("Arial", 12)

        # Formation settings
        self.formation_x = 0
        self.formation_y = 30
        self.formation_dir = 1
        self.create_enemies()

        # Starfield
        self.stars = [Star() for _ in range(50)]
        self.dive_timer = 0
        self.flagship_escort_kills = 0
        self.state = "START"
        self.high_score = 0

    def create_enemies(self):
        self.enemies.empty()
        self.all_sprites.empty()
        self.all_sprites.add(self.player)
        # Formation: 6 rows
        # Row 0: Flagships (2)
        # Row 1: Hornets (8)
        # Row 2-3: Emissaries (10 per row)
        # Row 4-5: Drones (10 per row)
        
        enemy_types = [
            (Flagship, 2, 0),
            (Hornet, 8, 1),
            (Emissary, 10, 2),
            (Emissary, 10, 3),
            (Drone, 10, 4),
            (Drone, 10, 5)
        ]
        
        for row_idx, (enemy_cls, count, row_id) in enumerate(enemy_types):
            spacing = 16
            start_x = (VIRTUAL_WIDTH - (count * spacing)) // 2
            for col_idx in range(count):
                x = start_x + col_idx * spacing
                y = 10 + row_idx * spacing # Start a bit lower
                enemy = enemy_cls(x, y, row_id, col_idx)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy, layer=0) # Ensure they are in a layer below bullets if needed

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.state == "START":
                    self.state = "PLAYING"
                elif self.state == "GAME_OVER":
                    self.score = 0
                    self.level = 1
                    self.player.lives = 3
                    self.create_enemies()
                    self.state = "PLAYING"
                elif self.state == "PLAYING":
                    if event.key == pygame.K_SPACE:
                        if self.player.cooldown == 0 and len(self.player_bullets) < 1:
                            bullet = self.player.shoot()
                            if bullet:
                                self.player_bullets.add(bullet)
                                self.all_sprites.add(bullet, layer=1)

    def update(self):
        if self.state != "PLAYING":
            # Update stars even in menus
            for star in self.stars:
                star.update()
            return

        self.player.handle_input()
        
        # Starfield update
        for star in self.stars:
            star.update()

        # The Sway logic
        self.formation_x += 0.5 * self.formation_dir
        if abs(self.formation_x) > 20:
            self.formation_dir *= -1

        self.enemies.update(self.formation_x + 20, self.formation_y)
        
        # Handle diving
        self.dive_timer += 1
        if self.dive_timer > 120: # Every 2 seconds
            import random
            eligible = [e for e in self.enemies if e.state == Enemy.FORMATION]
            if eligible:
                enemy = random.choice(eligible)
                if isinstance(enemy, Flagship):
                    # Flagships dive with escorts (usually two Hornets if available)
                    hornets = [e for e in self.enemies if isinstance(e, Hornet) and e.state == Enemy.FORMATION]
                    escorts = random.sample(hornets, min(len(hornets), 2))
                    enemy.start_dive(escorts)
                    self.flagship_escort_kills = 0 # Reset count for special bonus
                else:
                    enemy.start_dive()
            self.dive_timer = 0

        # Enemy shooting
        for enemy in self.enemies:
            bullet = enemy.shoot()
            if bullet:
                self.enemy_bullets.add(bullet)
                self.all_sprites.add(bullet, layer=1)

        self.player_bullets.update()
        self.enemy_bullets.update()
        self.player.update()
        self.explosions.update()

        if pygame.sprite.spritecollideany(self.player, self.enemies, pygame.sprite.collide_mask) or \
           pygame.sprite.spritecollideany(self.player, self.enemy_bullets, pygame.sprite.collide_mask):
            # Player hit
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.state = "GAME_OVER"
                if self.score > self.high_score:
                    self.high_score = self.score
            else:
                for b in self.enemy_bullets: b.kill()
                self.player.rect.midbottom = (VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT - 10)
                expl = Explosion(self.player.rect.centerx, self.player.rect.centery, GREEN)
                self.explosions.add(expl)
                self.all_sprites.add(expl)
        
        # Check enemy collisions with player bullets using masks
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, False, True, pygame.sprite.collide_mask)
        for enemy in hits:
            # Special points logic
            points = enemy.points
            if enemy.state == Enemy.DIVING:
                points *= 2
                if isinstance(enemy, Hornet):
                    # Check if it was an escort for current flagship dive
                    self.flagship_escort_kills += 1
                elif isinstance(enemy, Flagship):
                    if self.flagship_escort_kills >= 2:
                        # Bonus for destroying flagship and its 2 escorts
                        points += 800 
            
            self.score += points
            
            # Create explosion
            expl = Explosion(enemy.rect.centerx, enemy.rect.centery, enemy.color if hasattr(enemy, 'color') else PURPLE)
            enemy.kill() # Now manually killing after points logic
            self.explosions.add(expl)
            self.all_sprites.add(expl)

        # Check if all enemies are gone
        if not self.enemies:
            self.level += 1
            self.create_enemies()

    def draw(self):
        self.virtual_surface.fill(BLACK)
        
        # Draw Stars
        for star in self.stars:
            pygame.draw.circle(self.virtual_surface, star.color, (int(star.x), int(star.y)), 1)

        if self.state == "START":
            title = self.font.render("GALAXIAN", True, YELLOW)
            start_msg = self.font.render("PRESS ANY KEY TO START", True, WHITE)
            self.virtual_surface.blit(title, (VIRTUAL_WIDTH // 2 - 30, VIRTUAL_HEIGHT // 2 - 20))
            self.virtual_surface.blit(start_msg, (VIRTUAL_WIDTH // 2 - 65, VIRTUAL_HEIGHT // 2 + 10))
            
            # Show high score on start screen
            hs_msg = self.font.render(f"HIGH SCORE: {self.high_score}", True, RED)
            self.virtual_surface.blit(hs_msg, (VIRTUAL_WIDTH // 2 - 40, VIRTUAL_HEIGHT // 2 + 30))
        elif self.state == "GAME_OVER":
            over_msg = self.font.render("GAME OVER", True, RED)
            score_msg = self.font.render(f"FINAL SCORE: {self.score}", True, WHITE)
            restart_msg = self.font.render("PRESS ANY KEY TO RESTART", True, WHITE)
            self.virtual_surface.blit(over_msg, (VIRTUAL_WIDTH // 2 - 35, VIRTUAL_HEIGHT // 2 - 20))
            self.virtual_surface.blit(score_msg, (VIRTUAL_WIDTH // 2 - 45, VIRTUAL_HEIGHT // 2))
            self.virtual_surface.blit(restart_msg, (VIRTUAL_WIDTH // 2 - 65, VIRTUAL_HEIGHT // 2 + 20))
        else:
            self.all_sprites.draw(self.virtual_surface)
            
            # Draw Score, Level and Lives
            score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
            self.virtual_surface.blit(score_text, (5, 5))
            high_score_text = self.font.render(f"HI: {self.high_score}", True, RED)
            self.virtual_surface.blit(high_score_text, (VIRTUAL_WIDTH // 2 - 15, 18))
            level_text = self.font.render(f"LVL: {self.level}", True, WHITE)
            self.virtual_surface.blit(level_text, (VIRTUAL_WIDTH // 2 - 20, 5))
            lives_text = self.font.render(f"LIVES: {self.player.lives}", True, WHITE)
            self.virtual_surface.blit(lives_text, (VIRTUAL_WIDTH - 60, 5))

        # Scale the virtual surface to the screen size
        scaled_surface = pygame.transform.scale(self.virtual_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
