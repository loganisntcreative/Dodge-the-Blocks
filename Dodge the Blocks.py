import pygame
import sys
import random
import math

# -------------------------
# Constants
# -------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 7
BLOCK_WIDTH = 50
BLOCK_HEIGHT = 50
BASE_BLOCK_SPEED = 4
SPAWN_DELAY = 120
HIGH_SCORE_FILE = "highscore.txt"
HUD_HEIGHT = 90
current_music = None

#--------------------------
# UI COLORS
#--------------------------
BG_COLOR = (245, 242, 235)
TEXT_PRIMARY = (40, 40, 40)
TEXT_SECONDARY = (120, 120, 120)
ACCENT = (90, 140, 120)

PANEL_COLOR = (255, 255, 255)
PANEL_SHADOW = (220, 220, 220)
PLAYER_COLOR = (70, 120, 200)
BLOCK_COLOR = (220, 80, 80)


# -------------------------
# Helper Functions
# -------------------------
def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read())
    except:
        return 0

def save_high_score(high_score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(high_score))

def reset_game():
    player_x = SCREEN_WIDTH // 2 - 25
    player_y = SCREEN_HEIGHT - 50 - 20
    blocks = []
    score = 0
    spawn_timer = 0
    game_over = False
    return player_x, player_y, score, blocks, spawn_timer, game_over

def draw_grid(surface, spacing = 40):
    for x in range(0, SCREEN_WIDTH, spacing):
        pygame.draw.line(surface, (30, 30, 30), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, spacing):
        pygame.draw.line(surface, (30, 30, 30), (0, y), (SCREEN_WIDTH, y))

def draw_rounded_rect(surface, rect, color, radius = 12):
    pygame.draw.rect(surface, color, rect, border_radius = radius)

def draw_text(surface, text, font, color, center):
    render = font.render(text, True, color)
    surface.blit(render, render.get_rect(center=center))

def play_music(track, loop =-1):
    global current_music
    if current_music != track:
        pygame.mixer.music.load(track)
        pygame.mixer.music.play(loop)
        current_music = track

# -------------------------
# Main Function
# -------------------------
def main():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.35)

    menu_pulse = 0

    high_score = load_high_score()

    start_sound= pygame.mixer.Sound("start.wav")
    game_over_sound = pygame.mixer.Sound("game_over.wav")

    # Volume Control
    start_sound.set_volume(0.5)
    game_over_sound.set_volume(0.6)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dodge the Blocks")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # Game variables
    player_x, player_y, score, blocks, spawn_timer, game_over = reset_game()
    block_speed = BASE_BLOCK_SPEED
    fade_alpha = 0
    fade_speed = 5
    game_state = "menu"

    # --- Fonts ---
    title_font = pygame.font.SysFont("arial", 72, bold = True)
    menu_font= pygame.font.SysFont("arial", 32)
    small_font = pygame.font.SysFont("arial", 22)

    running = True
    while running:
        clock.tick(FPS)

        # -------------------------
        # Event Handling
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == "menu" and event.key == pygame.K_SPACE:
                    start_sound.play()
                    game_state = "playing"
                elif event.key == pygame.K_r and game_over:
                    player_x, player_y, score, blocks, spawn_timer, game_over = reset_game()
                    fade_alpha = 0
                    game_state = "playing"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    player_x, player_y, score, blocks, spawn_timer, game_over = reset_game()
                    fade_alpha = 0
                    game_state = "menu"

        # -------------------------
        # Input Handling
        # -------------------------
        keys = pygame.key.get_pressed()
        if game_state == "playing":
            if keys[pygame.K_a]:
                player_x -= PLAYER_SPEED
            if keys[pygame.K_d]:
                player_x += PLAYER_SPEED
            # Keep player inside screen
            player_x = max(0, min(SCREEN_WIDTH - 50, player_x))

        # -------------------------
        # Game Logic
        # -------------------------
        if game_state == "playing":
            play_music("gameplay_music.ogg", loop = -1)
            score += 1
            spawn_timer += 1
            max_blocks = min(1 + score // 500, 10)

            if spawn_timer >= SPAWN_DELAY and len(blocks) < max_blocks:
                # Try to spawn a new block without over lapping
                new_x = random.randint(0, SCREEN_WIDTH - BLOCK_WIDTH)
                new_y = -BLOCK_HEIGHT - HUD_HEIGHT

                # Check for vertical collision with existing blocks
                can_spawn = True
                for block in blocks:
                    if abs(block[1] - new_y) < BLOCK_HEIGHT + 10: # 10 px cushion
                        can_spawn = False
                        break

                if can_spawn:
                    blocks.append([new_x, new_y])
                    spawn_timer = 0 # reset only if we actually spawned

            block_speed = BASE_BLOCK_SPEED + score // 500

            # Move blocks and check collisions
            for block in blocks:
                block[1] += block_speed
                if block[1] > SCREEN_HEIGHT:
                    block[1] = -BLOCK_HEIGHT - HUD_HEIGHT
                    block[0] = random.randint(0, SCREEN_WIDTH - BLOCK_WIDTH)

                player_rect = pygame.Rect(player_x, player_y, 50, 50)
                block_rect = pygame.Rect(block[0], block[1], BLOCK_WIDTH, BLOCK_HEIGHT)
                if player_rect.colliderect(block_rect) and not game_over:
                    game_over_sound.play()
                    pygame.mixer.music.stop()
                    play_music("game_over_music.wav", loop=0)
                    game_state = "game_over"
                    game_over = True

            if game_state == "game_over":
                if score > high_score:
                    high_score = score # update the variable
                    save_high_score(high_score) # write it to the file

        # -------------------------
        # Drawing
        # -------------------------
        screen.fill((20, 20, 20))
        draw_grid(screen)

        if game_state == "menu":
            play_music("menu_music.wav", loop =-1)
            screen.fill(BG_COLOR)

            menu_card = pygame.Rect(
                SCREEN_WIDTH // 2 - 260,
                SCREEN_HEIGHT // 2 - 180,
                520,
                360
            )

            menu_shadow = menu_card.move(0, 6)

            draw_rounded_rect(screen, menu_shadow, PANEL_SHADOW, 24)
            draw_rounded_rect(screen, menu_card, PANEL_COLOR, 24)

            # --- Title ---
            draw_text(
                screen,
                "DODGE THE BLOCKS",
                title_font,
                TEXT_PRIMARY,
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
            )

            # --- Subtitle ---
            draw_text(
                screen,
                "Minimal reflex game",
                small_font,
                TEXT_SECONDARY,
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            )

            # --- Start Prompt ---
            button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 140,
                SCREEN_HEIGHT // 2 + 20,
                280,
                50
            )

            draw_rounded_rect(screen, button_rect, ACCENT, 16)

            # --- Footer Hint ---
            esc_text = small_font.render("ESC anytime to return to menu", True, TEXT_SECONDARY)
            screen.blit(
                esc_text,
                (SCREEN_WIDTH // 2 - esc_text.get_width() // 2,
                 SCREEN_HEIGHT - 60)
            )

            menu_pulse += 1
            pulse_alpha = 128 + int(127 * math.sin(menu_pulse / 20))  # smooth glow from 1 to 255

            pulse_surface = pygame.Surface(button_rect.size, pygame.SRCALPHA)
            pulse_surface.fill((0, 0, 0, 0))  # fully transparent
            pygame.draw.rect(pulse_surface, (*ACCENT, pulse_alpha), pulse_surface.get_rect(), border_radius=16)
            screen.blit(pulse_surface, button_rect.topleft)

            start_surface = pygame.Surface(menu_font.size("Press SPACE to Start"), pygame.SRCALPHA)
            text_render = menu_font.render("Press SPACE to Start", True, (255, 255, 255))
            start_surface.blit(text_render, (0, 0))
            start_surface.set_alpha(pulse_alpha)
            screen.blit(
                start_surface,
                start_surface.get_rect(center=button_rect.center)
            )

            pygame.display.flip()
            continue

        elif game_state == "playing" or game_state == "game_over":

            # Draw player
            pygame.draw.rect(
                screen,
                ACCENT,
                (player_x, player_y, 50, 50),
                border_radius=10
            )

            # Draw blocks
            for block in blocks:
                pygame.draw.rect(
                    screen,
                    (200, 80, 80),
                    (block[0], block[1], BLOCK_WIDTH, BLOCK_HEIGHT),
                    border_radius=8
                )

            # --- Top HUD Panel ---
            panel_rect = pygame.Rect(20, 20, SCREEN_WIDTH - 40, 60)
            shadow_rect = pygame.Rect(20, 24, SCREEN_WIDTH - 40, 60)

            draw_rounded_rect(screen, shadow_rect, PANEL_SHADOW, 16)
            draw_rounded_rect(screen, panel_rect, PANEL_COLOR, 16)

            # Draw score
            draw_text(
                screen,
                f"Score: {score}",
                font,
                TEXT_PRIMARY,
                (120, 50)
            )

            draw_text(
                screen,
                f"High: {high_score}",
                font,
                TEXT_SECONDARY,
                (SCREEN_WIDTH - 120, 50)
            )

            # Draw game over
            if game_state == "game_over":
                fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fade_surface.fill((0, 0, 0))
                if fade_alpha < 180:
                    fade_alpha += fade_speed
                fade_surface.set_alpha(fade_alpha)
                screen.blit(fade_surface, (0, 0))

                card = pygame.Rect(
                    SCREEN_WIDTH // 2 - 220,
                    SCREEN_HEIGHT // 2 - 120,
                    440,
                    240
                )

                draw_rounded_rect(screen, card, (255, 255, 255), 18)

                draw_text(
                    screen,
                    "GAME OVER",
                    pygame.font.SysFont("arial", 56, bold=True),
                    TEXT_PRIMARY,
                    (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
                )

                draw_text(
                    screen,
                    "Press R to Restart",
                    font,
                    TEXT_SECONDARY,
                    (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
                )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


# -------------------------
# Run the game
# -------------------------
if __name__ == "__main__":
    main()
