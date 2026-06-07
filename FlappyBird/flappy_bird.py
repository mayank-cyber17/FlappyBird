import pygame
import random
import sys
import os

# =========================
# INITIALIZATION
# =========================

pygame.init()
pygame.mixer.init()

WIDTH = 500
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

clock = pygame.time.Clock()

# =========================
# PATHS
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

def image_path(filename):
    return os.path.join(ASSETS_DIR, filename)

def sound_path(filename):
    return os.path.join(SOUNDS_DIR, filename)

# =========================
# LOAD IMAGES
# =========================

BACKGROUND = pygame.image.load(
    image_path("background.png")
).convert()

GROUND = pygame.image.load(
    image_path("ground.png")
).convert_alpha()

PIPE = pygame.image.load(
    image_path("pipe.png")
).convert_alpha()

BIRD_FRAMES = [
    pygame.image.load(image_path("bird1.png")).convert_alpha(),
    pygame.image.load(image_path("bird2.png")).convert_alpha(),
    pygame.image.load(image_path("bird3.png")).convert_alpha()
]

# =========================
# LOAD SOUNDS
# =========================

wing_sound = pygame.mixer.Sound(
    sound_path("wing.ogg")
)

point_sound = pygame.mixer.Sound(
    sound_path("point.ogg")
)

hit_sound = pygame.mixer.Sound(
    sound_path("hit.ogg")
)

die_sound = pygame.mixer.Sound(
    sound_path("die.wav")
)

# =========================
# HIGH SCORE
# =========================

HIGHSCORE_FILE = os.path.join(
    BASE_DIR,
    "highscore.txt"
)

if not os.path.exists(HIGHSCORE_FILE):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write("0")

with open(HIGHSCORE_FILE, "r") as f:
    try:
        HIGH_SCORE = int(f.read())
    except:
        HIGH_SCORE = 0

# =========================
# FONTS
# =========================

font = pygame.font.SysFont("Arial", 40)
big_font = pygame.font.SysFont("Arial", 70)

# =========================
# GAME VARIABLES
# =========================

GROUND_HEIGHT = 100

bird_x = 120
bird_y = HEIGHT // 2
bird_velocity = 0

GRAVITY = 0.5
JUMP_FORCE = -9

animation_index = 0
animation_timer = 0

ground_x = 0

PIPE_GAP = 180
PIPE_SPEED = 4

pipes = []

score = 0

game_started = False
game_over = False

# =========================
# FUNCTIONS
# =========================

def create_pipe():
    gap_y = random.randint(180, 450)

    top_pipe = PIPE.get_rect(
        midbottom=(WIDTH + 100, gap_y)
    )

    bottom_pipe = PIPE.get_rect(
        midtop=(WIDTH + 100, gap_y + PIPE_GAP)
    )

    return [top_pipe, bottom_pipe]

def reset_game():
    global bird_y
    global bird_velocity
    global pipes
    global score
    global game_started
    global game_over

    bird_y = HEIGHT // 2
    bird_velocity = 0

    pipes = [create_pipe()]

    score = 0

    game_started = False
    game_over = False

def save_high_score():
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(HIGH_SCORE))

pipes.append(create_pipe())

# =========================
# MAIN LOOP
# =========================

running = True

while running:

    clock.tick(FPS)

    # ---------------------
    # EVENTS
    # ---------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            save_high_score()
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                if not game_started:
                    game_started = True

                if not game_over:
                    bird_velocity = JUMP_FORCE
                    wing_sound.play()

            if event.key == pygame.K_r and game_over:
                reset_game()

    # ---------------------
    # DRAW BACKGROUND
    # ---------------------

    screen.blit(BACKGROUND, (0, 0))

    # ---------------------
    # GAME LOGIC
    # ---------------------

    if game_started and not game_over:

        bird_velocity += GRAVITY
        bird_y += bird_velocity

        if pipes[-1][0].centerx < WIDTH - 250:
            pipes.append(create_pipe())

        for pipe_pair in pipes:
            pipe_pair[0].centerx -= PIPE_SPEED
            pipe_pair[1].centerx -= PIPE_SPEED

        if pipes and pipes[0][0].right < 0:
            pipes.pop(0)

            score += 1
            point_sound.play()

            if score > HIGH_SCORE:
                HIGH_SCORE = score

    # ---------------------
    # BIRD ANIMATION
    # ---------------------

    animation_timer += 1

    if animation_timer >= 8:
        animation_index = (
            animation_index + 1
        ) % len(BIRD_FRAMES)

        animation_timer = 0

    bird_image = BIRD_FRAMES[animation_index]

    bird_rotation = max(
        -30,
        min(25, -bird_velocity * 3)
    )

    rotated_bird = pygame.transform.rotate(
        bird_image,
        bird_rotation
    )

    bird_rect = rotated_bird.get_rect(
        center=(bird_x, bird_y)
    )

    # ---------------------
    # DRAW PIPES
    # ---------------------

    for pipe_pair in pipes:

        top_pipe_img = pygame.transform.flip(
            PIPE,
            False,
            True
        )

        screen.blit(
            top_pipe_img,
            pipe_pair[0]
        )

        screen.blit(
            PIPE,
            pipe_pair[1]
        )

        if (
            bird_rect.colliderect(pipe_pair[0])
            or
            bird_rect.colliderect(pipe_pair[1])
        ):

            if not game_over:
                hit_sound.play()
                die_sound.play()

            game_over = True

    # ---------------------
    # GROUND COLLISION
    # ---------------------

    if bird_y < -50:
        game_over = True

    if bird_y > HEIGHT - GROUND_HEIGHT - 20:
        if not game_over:
            hit_sound.play()
            die_sound.play()

        game_over = True

    # ---------------------
    # DRAW BIRD
    # ---------------------

    screen.blit(
        rotated_bird,
        bird_rect
    )

    # ---------------------
    # SCROLLING GROUND
    # ---------------------

    ground_x -= PIPE_SPEED

    if ground_x <= -GROUND.get_width():
        ground_x = 0

    screen.blit(
        GROUND,
        (ground_x, HEIGHT - GROUND_HEIGHT)
    )

    screen.blit(
        GROUND,
        (
            ground_x + GROUND.get_width(),
            HEIGHT - GROUND_HEIGHT
        )
    )

    # ---------------------
    # SCORE
    # ---------------------

    score_text = font.render(
        f"Score: {score}",
        True,
        (255, 255, 255)
    )

    best_text = font.render(
        f"Best: {HIGH_SCORE}",
        True,
        (255, 255, 255)
    )

    screen.blit(score_text, (20, 20))
    screen.blit(best_text, (20, 70))

    # ---------------------
    # START SCREEN
    # ---------------------

    if not game_started:

        title = big_font.render(
            "FLAPPY BIRD",
            True,
            (255, 255, 255)
        )

        message = font.render(
            "Press SPACE",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (40, 250)
        )

        screen.blit(
            message,
            (120, 350)
        )

    # ---------------------
    # GAME OVER
    # ---------------------

    if game_over:

        over_text = big_font.render(
            "GAME OVER",
            True,
            (255, 50, 50)
        )

        restart_text = font.render(
            "Press R To Restart",
            True,
            (255, 255, 255)
        )

        screen.blit(
            over_text,
            (35, 250)
        )

        screen.blit(
            restart_text,
            (70, 350)
        )

    pygame.display.update()
