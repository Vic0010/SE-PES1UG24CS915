import random
import pygame
from game.text_box import TextBox


class GameEngine:
    MAX_ATTEMPTS = 7
    HISTORY_LIMIT = 5

    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Game state
        self.secret_number = random.randint(1, 100)
        self.attempts = 0
        self.game_won = False
        self.game_over = False

        # Task 2: Dynamic search range
        self.min_range = 1
        self.max_range = 100

        # Task 3: Guess history
        self.guess_history = []

        # Feedback
        self.feedback_msg = "Enter a number between 1 and 100"
        self.feedback_color = (220, 220, 220)

        # Input and button
        self.input_box = TextBox(
            width // 2 - 110,
            150,
            120,
            48
        )

        self.submit_btn = pygame.Rect(
            width // 2 + 25,
            150,
            100,
            48
        )

        # Fonts
        self.font_title = pygame.font.SysFont(None, 42)
        self.font_medium = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 22)
        self.font_btn = pygame.font.SysFont(None, 26)

    # ---------------------------------------------------------
    # TASK 1, 2, 3 and 4: Submit a guess
    # ---------------------------------------------------------
    def submit_guess(self):

        # Don't allow guesses after winning or losing
        if self.game_won or self.game_over:
            return

        # -----------------------------------------------------
        # TASK 1: Handle empty input safely
        # -----------------------------------------------------
        if not self.input_box.text.strip():
            self.feedback_msg = "WARNING: Enter a number first!"
            self.feedback_color = (255, 220, 80)
            return

        # Convert input to integer
        guess = int(self.input_box.text)

        # Clear the input box
        self.input_box.clear()

        # -----------------------------------------------------
        # Validate range
        # -----------------------------------------------------
        if guess < 1 or guess > 100:
            self.feedback_msg = "WARNING: Enter a number from 1 to 100!"
            self.feedback_color = (255, 220, 80)
            return

        # -----------------------------------------------------
        # Check whether the guess is already outside the
        # currently valid search range
        # -----------------------------------------------------
        if guess < self.min_range or guess > self.max_range:
            self.feedback_msg = (
                f"Use a number between {self.min_range} "
                f"and {self.max_range}!"
            )
            self.feedback_color = (255, 220, 80)
            return

        # -----------------------------------------------------
        # Count the valid guess as an attempt
        # -----------------------------------------------------
        self.attempts += 1

        # -----------------------------------------------------
        # TASK 3: Add guess to history
        # -----------------------------------------------------
        if guess < self.secret_number:

            # Task 2: Narrow lower boundary
            self.min_range = max(
                self.min_range,
                guess + 1
            )

            self.feedback_msg = f"TOO LOW! (Guess was {guess})"
            self.feedback_color = (80, 160, 240)

            self.guess_history.append(
                (guess, "TOO LOW", (80, 160, 240))
            )

        elif guess > self.secret_number:

            # Task 2: Narrow upper boundary
            self.max_range = min(
                self.max_range,
                guess - 1
            )

            self.feedback_msg = f"TOO HIGH! (Guess was {guess})"
            self.feedback_color = (240, 100, 80)

            self.guess_history.append(
                (guess, "TOO HIGH", (240, 100, 80))
            )

        else:
            # Correct guess
            self.feedback_msg = (
                f"CORRECT! Found in {self.attempts} attempts."
            )

            self.feedback_color = (80, 220, 90)

            self.guess_history.append(
                (guess, "CORRECT", (80, 220, 90))
            )

            self.game_won = True

        # Keep only the most recent guesses
        if len(self.guess_history) > self.HISTORY_LIMIT:
            self.guess_history = self.guess_history[
                -self.HISTORY_LIMIT:
            ]

        # -----------------------------------------------------
        # TASK 4: Maximum attempts
        # -----------------------------------------------------
        if (
            self.attempts >= self.MAX_ATTEMPTS
            and not self.game_won
        ):
            self.game_over = True

            self.feedback_msg = (
                f"GAME OVER! The number was {self.secret_number}."
            )

            self.feedback_color = (255, 90, 90)

    # ---------------------------------------------------------
    # Reset game
    # ---------------------------------------------------------
    def reset(self):
        self.secret_number = random.randint(1, 100)

        self.attempts = 0

        self.game_won = False
        self.game_over = False

        # Reset dynamic range
        self.min_range = 1
        self.max_range = 100

        # Clear history
        self.guess_history.clear()

        # Reset feedback
        self.feedback_msg = (
            "Enter a number between 1 and 100"
        )

        self.feedback_color = (220, 220, 220)

        # Clear input
        self.input_box.clear()

    # ---------------------------------------------------------
    # Handle keyboard and mouse events
    # ---------------------------------------------------------
    def handle_event(self, event):

        # Allow textbox to handle typing
        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN:

            # Submit using Enter / Return
            if event.key == pygame.K_RETURN:
                self.submit_guess()

            # Restart after win or game over
            elif (
                event.key == pygame.K_r
                and (self.game_won or self.game_over)
            ):
                self.reset()

        # Submit button
        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            if self.submit_btn.collidepoint(event.pos):
                self.submit_guess()

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------
    def update(self):
        pass

    # ---------------------------------------------------------
    # Render everything
    # ---------------------------------------------------------
    def render(self, screen):

        screen.fill((30, 34, 42))

        # -----------------------------------------------------
        # Title
        # -----------------------------------------------------
        title_surf = self.font_title.render(
            "Number Guessing Arena",
            True,
            (245, 245, 245)
        )

        screen.blit(
            title_surf,
            (
                self.width // 2
                - title_surf.get_width() // 2,
                25
            )
        )

        # -----------------------------------------------------
        # Attempts
        # -----------------------------------------------------
        attempts_surf = self.font_medium.render(
            f"Attempts: {self.attempts}/{self.MAX_ATTEMPTS}",
            True,
            (180, 185, 195)
        )

        screen.blit(
            attempts_surf,
            (
                self.width // 2
                - attempts_surf.get_width() // 2,
                75
            )
        )

        # -----------------------------------------------------
        # Input box
        # -----------------------------------------------------
        self.input_box.render(screen)

        # -----------------------------------------------------
        # Submit button
        # -----------------------------------------------------
        pygame.draw.rect(
            screen,
            (50, 150, 80),
            self.submit_btn,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (220, 220, 220),
            self.submit_btn,
            width=2,
            border_radius=6
        )

        btn_text = self.font_btn.render(
            "SUBMIT",
            True,
            (255, 255, 255)
        )

        screen.blit(
            btn_text,
            (
                self.submit_btn.centerx
                - btn_text.get_width() // 2,
                self.submit_btn.centery
                - btn_text.get_height() // 2
            )
        )

        # -----------------------------------------------------
        # TASK 2: Dynamic search range
        # -----------------------------------------------------
        range_text = (
            f"Possible Range: "
            f"{self.min_range} - {self.max_range}"
        )

        range_surf = self.font_small.render(
            range_text,
            True,
            (200, 210, 220)
        )

        screen.blit(
            range_surf,
            (
                self.width // 2
                - range_surf.get_width() // 2,
                205
            )
        )

        # -----------------------------------------------------
        # Feedback
        # -----------------------------------------------------
        feedback_surf = self.font_medium.render(
            self.feedback_msg,
            True,
            self.feedback_color
        )

        # Prevent very long messages from going off-screen
        feedback_x = (
            self.width // 2
            - feedback_surf.get_width() // 2
        )

        screen.blit(
            feedback_surf,
            (feedback_x, 235)
        )

        # -----------------------------------------------------
        # TASK 3: Guess history
        # -----------------------------------------------------
        history_title = self.font_small.render(
            "Recent Guesses:",
            True,
            (220, 220, 220)
        )

        screen.blit(
            history_title,
            (25, 285)
        )

        if not self.guess_history:

            no_history = self.font_small.render(
                "No guesses yet",
                True,
                (130, 135, 145)
            )

            screen.blit(
                no_history,
                (25, 310)
            )

        else:

            history_y = 310

            for guess, result, color in reversed(
                self.guess_history
            ):

                history_text = (
                    f"{guess}  -  {result}"
                )

                history_surf = self.font_small.render(
                    history_text,
                    True,
                    color
                )

                screen.blit(
                    history_surf,
                    (25, history_y)
                )

                history_y += 22

        # -----------------------------------------------------
        # TASK 4: Win state
        # -----------------------------------------------------
        if self.game_won:

            restart_surf = self.font_medium.render(
                "YOU WIN! Press [R] to Start a New Game",
                True,
                (255, 220, 80)
            )

            screen.blit(
                restart_surf,
                (
                    self.width // 2
                    - restart_surf.get_width() // 2,
                    285
                )
            )

        # -----------------------------------------------------
        # TASK 4: Game Over state
        # -----------------------------------------------------
        elif self.game_over:

            game_over_surf = self.font_medium.render(
                "GAME OVER! Press [R] to Try Again",
                True,
                (255, 100, 100)
            )

            screen.blit(
                game_over_surf,
                (
                    self.width // 2
                    - game_over_surf.get_width() // 2,
                    285
                )
            )
