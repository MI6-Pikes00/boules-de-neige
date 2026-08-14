"""Menu et boucle de jeu d'Avalanche."""

import os
import random
from tkinter import CENTER, LEFT, Button, Canvas, Label, PhotoImage, Tk, Toplevel

from . import highscore
from .constants import (
    ASSETS_DIR,
    BACKGROUND_COLOR,
    DIFFICULTIES,
    FPS,
    GAME_DURATION,
    INVINCIBILITY_DURATION,
    MENU_BACKGROUND,
    SCORE_PER_SECOND,
    SNOWBALL_SIZES,
)
from .santa import Santa
from .snowball import Snowball

RULES_TEXT = (
    "Guide le Père Noël (flèches ◀ ▶) pour éviter les boules de neige.\n"
    "Elles rétrécissent à chaque rebond au sol, puis disparaissent.\n"
    "Survis 60 secondes pour gagner.\n\n"
    "⭐ Pouvoir : la barre d'espace rend invincible 2 secondes.\n"
    "Les records indiquent s'ils ont été obtenus avec ou sans ce pouvoir."
)


def asset(name):
    return os.path.join(ASSETS_DIR, name)


class Menu:
    """Fenêtre d'accueil : règles du jeu, choix de la difficulté ou sortie."""

    def __init__(self):
        self.menu = Tk()
        self.menu.title("Avalanche")
        self.menu.geometry("460x520")
        self.menu.resizable(width=False, height=False)

        self.canvas = Canvas(
            self.menu, width=460, height=520, bg=MENU_BACKGROUND, highlightthickness=0
        )
        self.canvas.pack()

        self.quit_image = PhotoImage(file=asset("quit.png"))

        self.menu.bind("<Escape>", self.quit)

        self.canvas.create_text(
            230, 45, text="AVALANCHE", fill="black", font=("Impact", 44), anchor=CENTER
        )

        Label(
            self.canvas,
            text=RULES_TEXT,
            justify=LEFT,
            anchor="w",
            bg="white",
            fg="black",
            font=("Helvetica", 11),
            padx=14,
            pady=10,
            wraplength=380,
        ).place(x=40, y=85, width=380)

        self.difficulty_buttons = {}
        y = 265
        for difficulty in DIFFICULTIES:
            btn = Button(
                self.canvas,
                text=self._label(difficulty),
                width=32,
                command=lambda d=difficulty: self.jouer(d),
            )
            btn.place(x=230, y=y, anchor=CENTER)
            self.difficulty_buttons[difficulty] = btn
            y += 42

        Button(
            self.canvas,
            image=self.quit_image,
            width=95,
            height=44,
            border=0,
            command=self.menu.destroy,
        ).place(x=230, y=y + 15, anchor=CENTER)

        self.menu.configure(background="white")
        self.menu.eval("tk::PlaceWindow . center")

    def _label(self, difficulty):
        return f"{difficulty.capitalize()}  —  {highscore.format_record(difficulty)}"

    def refresh_records(self):
        for difficulty, btn in self.difficulty_buttons.items():
            btn.configure(text=self._label(difficulty))

    def run(self):
        self.menu.mainloop()

    def jouer(self, difficulty, event=None):
        Game(difficulty, on_close=self.refresh_records)

    def quit(self, event=None):
        self.menu.destroy()


class Game:
    """Une partie d'Avalanche, pour une difficulté donnée."""

    def __init__(self, difficulty, on_close=None):
        self.difficulty = difficulty
        self.settings = DIFFICULTIES[difficulty]
        self.on_close = on_close

        self.window = Toplevel()
        self.window.title("Bataille de boules de neige")

        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()

        self.canvas = Canvas(
            self.window,
            width=self.screen_width,
            height=self.screen_height,
            bg=BACKGROUND_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        # Sprites des boules de neige, chargés une seule fois.
        self.snowball_sprites = {
            size: PhotoImage(file=asset(f"boule{size}.gif")) for size in SNOWBALL_SIZES
        }

        self.snowballs = {}  # id de l'item canvas -> Snowball

        self.fps = FPS
        self.chrono = GAME_DURATION
        self.frame_counter = 0
        self.spawn_timer = 0
        self.paused = False
        self.score = 0
        self.used_power = False
        self.running = True

        self.chrono_text_id = self.canvas.create_text(
            self.screen_width * 0.8,
            self.screen_height * 0.2,
            text=str(self.chrono),
            fill="white",
            font=("Helvetica", 100),
        )
        self.score_text_id = self.canvas.create_text(
            self.screen_width * 0.2,
            self.screen_height * 0.1,
            text="Score : 0",
            fill="white",
            font=("Helvetica", 30),
        )

        sprite_left = PhotoImage(file=asset("NoelG.gif"))
        sprite_right = PhotoImage(file=asset("NoelD.gif"))
        self.santa = Santa(
            self.canvas,
            self.screen_width * 0.5,
            self.screen_height * 0.75,
            sprite_left,
            sprite_right,
        )

        self.window.bind("<Right>", self.move_right)
        self.window.bind("<Left>", self.move_left)
        self.window.bind("<space>", self.power)
        self.window.bind("<p>", self.toggle_pause)
        self.window.bind("<Escape>", self.quit)
        self.window.protocol("WM_DELETE_WINDOW", self.quit)

        self.loop()

    # -- Déplacement du Père Noël ------------------------------------

    def move_left(self, event=None):
        self._update_edge_bindings()
        self.santa.move_left()

    def move_right(self, event=None):
        self._update_edge_bindings()
        self.santa.move_right()

    def _update_edge_bindings(self):
        """Désactive la touche qui ferait sortir le Père Noël de l'écran."""
        x, _y, _x2, _y2 = self.santa.bbox

        if x < 30:
            self.window.unbind("<Left>")
        else:
            self.window.bind("<Left>", self.move_left)

        if x < self.screen_width - 110:
            self.window.bind("<Right>", self.move_right)
        else:
            self.window.unbind("<Right>")

    def _has_collided(self):
        x, y, x2, y2 = self.santa.hitbox
        overlapping = self.canvas.find_overlapping(x, y, x2, y2)
        return len(overlapping) > 1 and not self.santa.invincible

    # -- Pouvoir d'invincibilité ---------------------------------------

    def power(self, event=None):
        if self.santa.invincible or not self.running:
            return
        self.santa.start_invincibility(INVINCIBILITY_DURATION)
        self.used_power = True
        self.canvas.create_text(
            self.screen_width * 0.5,
            self.screen_height * 0.2,
            text="INVINCIBLE",
            fill="black",
            font=("Impact", 50),
            tag="invincible",
        )

    # -- Pause -----------------------------------------------------------

    def toggle_pause(self, event=None):
        if not self.running:
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_text_id = self.canvas.create_text(
                self.screen_width * 0.5,
                self.screen_height * 0.5,
                text="PAUSE",
                fill="black",
                font=("Impact", 150),
                tag="pause",
            )
        else:
            self.canvas.delete("pause")

    # -- Boucle principale ------------------------------------------------

    def loop(self):
        if self.paused:
            self.window.after(1000 // self.fps, self.loop)
            return

        if self._has_collided():
            self._end_game(won=False)
            return

        if self.frame_counter >= self.fps:
            self.frame_counter = 0

            if self.santa.tick_invincibility():
                self.canvas.delete("invincible")

            self.chrono -= 1
            self.canvas.itemconfigure(self.chrono_text_id, text=str(self.chrono))

            self.score += SCORE_PER_SECOND[self.difficulty]
            self.canvas.itemconfigure(self.score_text_id, text=f"Score : {self.score}")

            if self.chrono <= 0:
                self._end_game(won=True)
                return

        if (
            len(self.snowballs) < self.settings["max_snowballs"]
            and self.spawn_timer <= 0
        ):
            self.spawn_timer = self.settings["spawn_interval"]
            self._spawn_snowball()

        self._update_snowballs()

        self.spawn_timer -= 1
        self.frame_counter += 1

        self.window.after(1000 // self.fps, self.loop)

    def _update_snowballs(self):
        expired = []
        for item_id, snowball in self.snowballs.items():
            snowball.move()
            x, y = snowball.position
            self.canvas.moveto(item_id, x=x, y=y)

            if snowball.is_spent:
                expired.append(item_id)
            elif snowball.just_split:
                self.canvas.itemconfigure(
                    item_id, image=self.snowball_sprites[snowball.size]
                )

        for item_id in expired:
            self.canvas.itemconfigure(item_id, state="hidden")
            del self.snowballs[item_id]

    def _spawn_snowball(self):
        size = random.choice(SNOWBALL_SIZES)
        item_id = self.canvas.create_image(0, 0)
        snowball = Snowball(
            size,
            self.screen_width,
            self.screen_height,
            speed_multiplier=self.settings["speed_multiplier"],
        )
        self.snowballs[item_id] = snowball
        self.canvas.itemconfigure(item_id, image=self.snowball_sprites[size])
        x, y = snowball.position
        self.canvas.moveto(item_id, x=x, y=y)

    # -- Fin de partie -----------------------------------------------------

    def _end_game(self, won):
        self.running = False
        self.window.unbind("<space>")
        self.window.unbind("<Left>")
        self.window.unbind("<Right>")
        self.window.unbind("<p>")

        is_record = highscore.save_highscore(self.difficulty, self.score, self.used_power)
        message = "GAGNÉ" if won else "PERDU"
        self.canvas.create_text(
            self.screen_width * 0.5,
            self.screen_height * 0.35,
            text=message,
            fill="black",
            font=("Impact", 220),
        )
        record_suffix = "  (nouveau record !)" if is_record else ""
        self.canvas.create_text(
            self.screen_width * 0.5,
            self.screen_height * 0.55,
            text=f"Score : {self.score}{record_suffix}",
            fill="black",
            font=("Impact", 55),
        )

        Button(
            self.canvas, text="Rejouer", width=16, command=self._retry
        ).place(x=self.screen_width * 0.5 - 90, y=self.screen_height * 0.65, anchor=CENTER)
        Button(
            self.canvas, text="Menu", width=16, command=self.quit
        ).place(x=self.screen_width * 0.5 + 90, y=self.screen_height * 0.65, anchor=CENTER)

    def _retry(self):
        on_close = self.on_close
        difficulty = self.difficulty
        self.window.destroy()
        Game(difficulty, on_close=on_close)

    def quit(self, event=None):
        self.window.destroy()
        if self.on_close:
            self.on_close()
