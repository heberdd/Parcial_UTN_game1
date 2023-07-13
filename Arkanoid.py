import pygame
import sqlite3
from random import randrange as rnd
import time
import tkinter as tk
from tkinter import messagebox


class Block:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def update(self, keys, width):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < width:
            self.rect.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, pygame.Color('black'), self.rect)


class Ball:
    def __init__(self, x, y, radius, speed):
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.radius = radius
        self.speed = speed
        self.direction = [1, -1]

    def update(self):
        self.rect.x += self.speed * self.direction[0]
        self.rect.y += self.speed * self.direction[1]

    def draw(self, screen):
        pygame.draw.circle(screen, pygame.Color('white'), self.rect.center, self.radius)


class Level:
    def __init__(self, blocks, background):
        self.blocks = blocks
        self.background = background

    def draw_blocks(self, screen):
        for block in self.blocks:
            block.draw(screen)

    def remove_block(self, block):
        self.blocks.remove(block)

    def block_count(self):
        return len(self.blocks)


class ArkanoidGame:
    def __init__(self):
        self.WIDTH = 800
        self.HEIGHT = 600
        self.fps = 60
        self.score = 0
        self.lives = 3
        self.level = 0
        self.levels = [
            Level([
                Block((self.WIDTH // 2 - 500) + 100 * i, (self.HEIGHT // 2 - 200) + 70 * j, 100, 50,
                      (rnd(30, 256), rnd(30, 256), rnd(30, 256))) for i in range(10) for j in range(4)
            ],
                "C:\\Users\\Win7-64\\Desktop\\Juego Arkanoid\\arkanoid-main\\Level 1 - Ocean.jpg"),
            Level([
                Block((self.WIDTH // 2 - 600) + 100 * i, (self.HEIGHT // 2 - 200) + 50 * j, 80, 40,
                      (rnd(30, 256), rnd(30, 256), rnd(30, 256))) for i in range(12) for j in range(3)
            ],
                "C:\\Users\\Win7-64\\Desktop\\Juego Arkanoid\\arkanoid-main\\Level 2 - Noche Estrellada.jpg"),
            Level([
                Block((self.WIDTH // 2 - 700) + 80 * i, (self.HEIGHT // 2 - 200) + 40 * j, 60, 30,
                      (rnd(30, 256), rnd(30, 256), rnd(30, 256))) for i in range(16) for j in range(2)
            ],
                "C:\\Users\\Win7-64\\Desktop\\Juego Arkanoid\\arkanoid-main\\Level 3 - Magritte.jpg")
        ]
        self.current_level = self.levels[self.level]

        self.paddle_width = 200
        self.paddle_height = 30
        self.paddle_speed = 15
        self.paddle = Paddle(self.WIDTH // 2 - self.paddle_width // 2, self.HEIGHT - self.paddle_height - 10,
                             self.paddle_width, self.paddle_height, self.paddle_speed)

        self.ball_radius = 20
        self.ball_speed = 6
        self.ball = Ball(rnd(self.ball_radius, self.WIDTH - self.ball_radius), self.HEIGHT // 2, self.ball_radius,
                         self.ball_speed)

        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.game_state = "play"
        self.block_count = self.current_level.block_count()
        self.points_counter = 0
        self.timer_counter = 0

    def run(self):
        self.load_level_background()
        start_time = time.time()
        level_completed = False

        # Musica de fondo
        pygame.mixer.music.load("C:\\Users\\Win7-64\\Desktop\\Juego Arkanoid\\arkanoid-main\\relaxed-vlog-night-street-131746.mp3")
        pygame.mixer.music.play(-1)  # -1 significa reproducir en bucle

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()

            keys = pygame.key.get_pressed()
            self.paddle.update(keys, self.WIDTH)

            self.screen.blit(self.background, (0, 0))

            if not level_completed:
                self.current_level.draw_blocks(self.screen)
                self.paddle.draw(self.screen)
                self.ball.draw(self.screen)

                self.ball.update()
                self.handle_collisions()

            if self.block_count == 0:
                level_completed = True
                if self.level >= len(self.levels) - 1:
                    self.game_state = "completed"
                    self.game_over()
                else:
                    self.update_screen()
                    time.sleep(2)
                    self.level += 1
                    self.current_level = self.levels[self.level]
                    self.load_level_background()
                    self.reset_ball_and_paddle()
                    self.block_count = self.current_level.block_count()
                    level_completed = False

            if self.game_state == "completed":
                self.game_over()

            self.update_screen()
            self.clock.tick(self.fps)

            elapsed_time = time.time() - start_time
            self.timer_counter = int(elapsed_time)

    def load_level_background(self):
        self.background = pygame.image.load(self.current_level.background).convert()
        self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))

    def handle_collisions(self):
        if self.ball.rect.colliderect(self.paddle.rect) and self.ball.direction[1] > 0:
            self.ball.direction[1] = -self.ball.direction[1]

        for block in self.current_level.blocks:
            if self.ball.rect.colliderect(block.rect):
                self.ball.direction[1] = -self.ball.direction[1]
                self.current_level.remove_block(block)
                self.block_count -= 1
                self.score += 1
                self.points_counter += 1
                self.fps += 2
                break

        if self.ball.rect.left < 0 or self.ball.rect.right > self.WIDTH:
            self.ball.direction[0] = -self.ball.direction[0]

        if self.ball.rect.top < 0:
            self.ball.direction[1] = -self.ball.direction[1]

        if self.ball.rect.bottom > self.HEIGHT:
            self.lives -= 1
            if self.lives == 0:
                self.game_over()
            else:
                self.reset_ball_and_paddle()

    def reset_ball_and_paddle(self):
        self.ball = Ball(rnd(self.ball_radius, self.WIDTH - self.ball_radius), self.HEIGHT // 2, self.ball_radius,
                         self.ball_speed)
        self.paddle = Paddle(self.WIDTH // 2 - self.paddle_width // 2, self.HEIGHT - self.paddle_height - 10,
                             self.paddle_width, self.paddle_height, self.paddle_speed)

    def update_screen(self):
        pygame.draw.rect(self.screen, pygame.Color('black'), (10, 10, 150, 70))
        score_text = self.font.render(f"Score: {self.score}", True, pygame.Color('white'))
        self.screen.blit(score_text, (20, 20))

        pygame.draw.rect(self.screen, pygame.Color('black'), (self.WIDTH - 160, 10, 150, 70))
        timer_text = self.font.render(f"Time: {self.timer_counter} s", True, pygame.Color('white'))
        self.screen.blit(timer_text, (self.WIDTH - 150, 20))

        pygame.display.flip()

    def exit_game(self):
        pygame.quit()
        exit()

    def game_over(self):
        self.save_score()
        print('GAME OVER!')
        pygame.mixer.music.stop()  # Detener la musica de fondo
        self.exit_game()

    def save_score(self):
        try:
            root = tk.Tk()
            root.withdraw()

            dialog = AliasDialog(root)
            root.wait_window(dialog)

            alias = dialog.result

            if alias:
                conn = sqlite3.connect('scores.db')
                cursor = conn.cursor()
                cursor.execute('CREATE TABLE IF NOT EXISTS scores (alias TEXT, score INTEGER)')
                cursor.execute('INSERT INTO scores VALUES (?, ?)', (alias, self.score))
                conn.commit()
                conn.close()
            else:
                messagebox.showinfo("Error", "El alias no puede estar vacío.")
                self.save_score()
        except sqlite3.Error as error:
            print("Error al guardar el puntaje:", error)

    def show_scores(self):
        try:
            conn = sqlite3.connect('scores.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM scores ORDER BY score DESC')
            scores = cursor.fetchall()
            conn.close()

            root = tk.Tk()
            root.title("Ranking de Puntajes")
            frame = tk.Frame(root)
            frame.pack(padx=20, pady=20)

            label = tk.Label(frame, text="Ranking de Puntajes", font=("Arial", 18, "bold"))
            label.pack()

            for score in scores:
                label = tk.Label(frame, text=f"Alias: {score[0]}, Score: {score[1]}", font=("Arial", 12))
                label.pack()

            root.mainloop()
        except sqlite3.Error as error:
            print("Error al mostrar los puntajes:", error)


class AliasDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Alias")
        self.parent = parent
        self.result = None

        self.label = tk.Label(self, text="Ingrese su alias:")
        self.label.pack()

        self.entry = tk.Entry(self)
        self.entry.pack()

        self.button = tk.Button(self, text="Aceptar", command=self.accept)
        self.button.pack()

    def accept(self):
        alias = self.entry.get()
        if alias:
            self.result = alias
            self.destroy()
        else:
            messagebox.showinfo("Error", "El alias no puede estar vacío.")


class Menu:
    def __init__(self):
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = None
        self.menu_items = ['1. Jugar', '2. Ver puntajes', '3. Salir']
        self.selected_item = 0

    def run(self):
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

        # Cargar imagen de fondo para el menu
        background_image = pygame.image.load("C:\\Users\\Win7-64\\Desktop\\Juego Arkanoid\\arkanoid-main\\UTN_logo.jpg").convert()
        background_image = pygame.transform.scale(background_image, (self.WIDTH, self.HEIGHT))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                    elif event.key == pygame.K_DOWN:
                        self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                    elif event.key == pygame.K_RETURN:
                        self.handle_selection()

            self.screen.blit(background_image, (0, 0))

            for i, item in enumerate(self.menu_items):
                color = pygame.Color('white') if i == self.selected_item else pygame.Color('gray')
                text = self.font.render(item, True, color)
                self.screen.blit(text, (self.WIDTH // 2 - text.get_width() // 2, 200 + i * 50))

            self.update_screen()
            self.clock.tick(30)

    def handle_selection(self):
        if self.selected_item == 0:
            self.start_game()
        elif self.selected_item == 1:
            self.show_scores()
        elif self.selected_item == 2:
            self.exit_game()

    def start_game(self):
        game = ArkanoidGame()
        game.run()

    def show_scores(self):
        game = ArkanoidGame()
        game.show_scores()

    def update_screen(self):
        pygame.display.flip()

    def exit_game(self):
        pygame.quit()
        exit()


menu = Menu()
menu.run()
