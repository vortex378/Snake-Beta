import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Screen Setup
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiplayer Snake Battle")
clock = pygame.time.Clock()
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
PURPLE = (150, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (50, 50, 50)
RED = (255, 0, 0)
BLUE = (0, 150, 255)
NEON_GREEN = (0, 255, 150)
NEON_PURPLE = (200, 0, 255)

# Game Settings
MOVE_DELAY = 5  # Frames between moves
WINNING_SCORE = 10

# Snake Class
class Snake:
    def __init__(self, color, controls, start_pos):
        self.body = [start_pos]
        self.direction = (1, 0)
        self.color = color
        self.grow = False
        self.score = 0
        self.move_counter = 0
        self.alive = True
        self.controls = controls  # Dict of keys for movement

    def change_direction(self, new_dir):
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def move(self, foods):
        if not self.alive:
            return

        self.move_counter += 1
        if self.move_counter < MOVE_DELAY:
            return

        self.move_counter = 0
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % COLS, (head_y + dy) % ROWS)

        # Collision with self or obstacles
        if new_head in self.body or new_head in obstacles:
            self.alive = False
            return

        # Collision with other snake
        for other_snake in [player1, player2]:
            if other_snake != self and new_head in other_snake.body:
                self.alive = False
                other_snake.alive = False
                return

        # Food Collision
        for food in foods[:]:
            if new_head == food.position:
                if food.type == "grow":
                    self.score += 1
                    self.grow = True
                    create_particle(food.position, self.color)
                elif food.type == "shrink":
                    if len(self.body) > 1:
                        self.body.pop()
                    create_particle(food.position, RED)
                elif food.type == "speed":
                    self.score += 1
                    self.move_counter -= 2
                    create_particle(food.position, BLUE)
                foods.remove(food)
                foods.append(Food())
                break

        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def draw(self):
        for i, segment in enumerate(self.body):
            x, y = segment
            color = tuple(max(0, c - i * 10) for c in self.color)
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Food Class
class Food:
    def __init__(self):
        self.position = self.random_position()
        self.color = random.choice([GREEN, PURPLE, YELLOW])
        self.type = {GREEN: "grow", PURPLE: "shrink", YELLOW: "speed"}.get(self.color, "speed")

    def random_position(self):
        while True:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in player1.body and pos not in player2.body and pos not in obstacles:
                return pos

    def draw(self):
        x, y = self.position
        pygame.draw.rect(screen, self.color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Particle System
particles = []

def create_particle(pos, color):
    for _ in range(10):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 3)
        vel_x = math.cos(angle) * speed
        vel_y = math.sin(angle) * speed
        particles.append([list(pos), [vel_x, vel_y], color])

def update_particles():
    for p in particles[:]:
        p[0][0] += p[1][0]
        p[0][1] += p[1][1]
        p[1][0] *= 0.9
        p[1][1] *= 0.9
        if abs(p[1][0]) < 0.1 and abs(p[1][1]) < 0.1:
            particles.remove(p)

# Initialize Snakes
player1 = Snake(GREEN, {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0)
}, (COLS // 4, ROWS // 2))

player2 = Snake(PURPLE, {
    pygame.K_w: (0, -1),
    pygame.K_s: (0, 1),
    pygame.K_a: (-1, 0),
    pygame.K_d: (1, 0)
}, (COLS * 3 // 4, ROWS // 2))

# Obstacles (after snakes are initialized)
obstacles = []
while len(obstacles) < 10:
    obs = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
    if obs not in player1.body and obs not in player2.body:
        obstacles.append(obs)

# Food and Power-Ups
foods = [Food() for _ in range(5)]

# Score Display
font = pygame.font.SysFont("Arial", 24)
large_font = pygame.font.SysFont("Arial", 40)

# Game Loop
def main():
    global foods
    game_over = False
    winner = None

    while True:
        if not game_over:
            screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Player Input
            keys = pygame.key.get_pressed()
            for key, direction in player1.controls.items():
                if keys[key]:
                    player1.change_direction(direction)
            for key, direction in player2.controls.items():
                if keys[key]:
                    player2.change_direction(direction)

            # Move Snakes
            player1.move(foods)
            player2.move(foods)

            # Check Victory
            if player1.score >= WINNING_SCORE:
                winner = "Player 1"
                game_over = True
            if player2.score >= WINNING_SCORE:
                winner = "Player 2"
                game_over = True

            # Draw Everything
            for obs in obstacles:
                pygame.draw.rect(screen, GRAY, (obs[0] * CELL_SIZE, obs[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if player1.alive:
                player1.draw()
            if player2.alive:
                player2.draw()
            for food in foods:
                food.draw()
            update_particles()
            for p in particles:
                x, y = p[0]
                color = p[2]
                pygame.draw.circle(screen, color, (int(x * CELL_SIZE + CELL_SIZE // 2), int(y * CELL_SIZE + CELL_SIZE // 2)), 3)

            # Draw Scores
            score1 = font.render(f"Player 1: {player1.score}", True, NEON_GREEN)
            score2 = font.render(f"Player 2: {player2.score}", True, NEON_PURPLE)
            screen.blit(score1, (10, 10))
            screen.blit(score2, (10, 40))

            pygame.display.flip()
            clock.tick(FPS)

        else:
            screen.fill(BLACK)
            win_text = large_font.render(f"{winner} Wins!", True, WHITE)
            restart_text = font.render("Press R to Restart | Q to Quit", True, WHITE)
            screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Reset Game
                        player1.__init__(GREEN, player1.controls, (COLS // 4, ROWS // 2))
                        player2.__init__(PURPLE, player2.controls, (COLS * 3 // 4, ROWS // 2))
                        foods = [Food() for _ in range(5)]
                        game_over = False
                        winner = None
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

if __name__ == "__main__":
    main()