import pygame
import sys
import random
from array import array

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong with Deltarune-style Menu")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Paddle dimensions and speed
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 90
PADDLE_SPEED = 5

# Ball dimensions and speed
BALL_SIZE = 15
BALL_SPEED = 5

# Sound generation function
def generate_beep_sound(frequency=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    wave = [int(max_amplitude * ((i // (sample_rate // frequency)) % 2)) for i in range(samples)]
    sound = pygame.mixer.Sound(buffer=array('h', wave))
    sound.set_volume(0.1)
    return sound

# Create sound effects
paddle_hit_sound = generate_beep_sound(440, 0.1)  # A4
wall_hit_sound = generate_beep_sound(523.25, 0.1)  # C5
score_sound = generate_beep_sound(659.25, 0.5)  # E5
menu_move_sound = generate_beep_sound(330, 0.05)  # E4
menu_select_sound = generate_beep_sound(440, 0.1)  # A4

# Paddle Class
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED

    def move(self, up=True):
        if up:
            self.rect.y -= self.speed
        else:
            self.rect.y += self.speed
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - PADDLE_HEIGHT))

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

    def ai_move(self, ball):
        if self.rect.centery < ball.rect.centery:
            self.move(up=False)
        elif self.rect.centery > ball.rect.centery:
            self.move(up=True)

# Ball Class
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.dx = BALL_SPEED * random.choice((1, -1))
        self.dy = BALL_SPEED * random.choice((1, -1))

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.dy *= -1
            wall_hit_sound.play()

    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.dx = BALL_SPEED * random.choice((1, -1))
        self.dy = BALL_SPEED * random.choice((1, -1))

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

# Function to display text on screen
def display_text(text, x, y, size=36, color=WHITE):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Menu class
class Menu:
    def __init__(self):
        self.state = "main"
        self.options = {
            "main": ["Start Game", "Settings", "Controls", "Exit"],
            "settings": ["Ball Speed", "Paddle Speed", "Back"],
            "controls": ["Back"]
        }
        self.selected = 0
        self.ball_speed = BALL_SPEED
        self.paddle_speed = PADDLE_SPEED

    def draw(self):
        screen.fill(BLACK)
        display_text("PONG", SCREEN_WIDTH // 2, 100, size=72, color=YELLOW)
        
        start_y = 250
        for i, option in enumerate(self.options[self.state]):
            color = YELLOW if i == self.selected else WHITE
            display_text(option, SCREEN_WIDTH // 2, start_y + i * 50, color=color)

        if self.state == "settings":
            display_text(f"Ball Speed: {self.ball_speed}", SCREEN_WIDTH // 2, 450)
            display_text(f"Paddle Speed: {self.paddle_speed}", SCREEN_WIDTH // 2, 500)
        elif self.state == "controls":
            display_text("W / S : Move Left Paddle Up / Down", SCREEN_WIDTH // 2, 450)
            display_text("Right Paddle is AI Controlled", SCREEN_WIDTH // 2, 500)

    def move_selection(self, direction):
        menu_move_sound.play()
        self.selected = (self.selected + direction) % len(self.options[self.state])

    def select(self):
        menu_select_sound.play()
        if self.state == "main":
            if self.selected == 0:  # Start Game
                return "playing"
            elif self.selected == 1:  # Settings
                self.state = "settings"
                self.selected = 0
            elif self.selected == 2:  # Controls
                self.state = "controls"
                self.selected = 0
            elif self.selected == 3:  # Exit
                return "exit"
        elif self.state in ["settings", "controls"]:
            if self.options[self.state][self.selected] == "Back":
                self.state = "main"
                self.selected = 0
        return None

    def handle_settings(self, direction):
        if self.selected == 0:  # Ball Speed
            self.ball_speed = max(1, min(10, self.ball_speed + direction))
        elif self.selected == 1:  # Paddle Speed
            self.paddle_speed = max(1, min(10, self.paddle_speed + direction))

# Create game objects
menu = Menu()
player1 = Paddle(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
player2 = Paddle(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
ball = Ball()

# Initialize scores
score1 = 0
score2 = 0

# Game States
game_state = "menu"

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_UP:
                    menu.move_selection(-1)
                elif event.key == pygame.K_DOWN:
                    menu.move_selection(1)
                elif event.key == pygame.K_RETURN:
                    result = menu.select()
                    if result == "playing":
                        game_state = "playing"
                        score1 = 0
                        score2 = 0
                        ball.reset()
                    elif result == "exit":
                        running = False
                elif event.key == pygame.K_LEFT and menu.state == "settings":
                    menu.handle_settings(-1)
                elif event.key == pygame.K_RIGHT and menu.state == "settings":
                    menu.handle_settings(1)
            elif game_state in ["win", "lose"] and event.key == pygame.K_SPACE:
                game_state = "menu"

    if game_state == "menu":
        menu.draw()
    elif game_state == "playing":
        # Update game objects
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player1.move(up=True)
        if keys[pygame.K_s]:
            player1.move(up=False)

        player2.ai_move(ball)
        ball.move()

        # Check for collisions
        if ball.rect.colliderect(player1.rect) or ball.rect.colliderect(player2.rect):
            ball.dx *= -1
            paddle_hit_sound.play()

        # Check for scoring
        if ball.rect.left <= 0:
            score2 += 1
            score_sound.play()
            ball.reset()
        elif ball.rect.right >= SCREEN_WIDTH:
            score1 += 1
            score_sound.play()
            ball.reset()

        # Check for win condition
        if score1 >= 5:
            game_state = "win"
        elif score2 >= 5:
            game_state = "lose"

        # Draw everything
        screen.fill(BLACK)
        player1.draw()
        player2.draw()
        ball.draw()
        pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        display_text(str(score1), SCREEN_WIDTH // 4, 50)
        display_text(str(score2), SCREEN_WIDTH * 3 // 4, 50)

    elif game_state == "win":
        screen.fill(BLACK)
        display_text("You Win!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, size=72)
        display_text("Press SPACE to return to menu", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

    elif game_state == "lose":
        screen.fill(BLACK)
        display_text("You Lose!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, size=72)
        display_text("Press SPACE to return to menu", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

    # Update the display
    pygame.display.flip()

    # Control game speed (60 FPS)
    clock.tick(60)

pygame.quit()
sys.exit()
