import arcade
import random
import os
import arcade.resources
from windows.menu.menu_window import WindowMenu


TANK_FILENAMES = [
    "tank_dark.png",
    "tank_darkLarge.png",
    "tank_green.png",
    "tank_huge.png",
    "tank_red.png",
    "tank_sand.png",
    "tank_bigRed.png",
    "tank_blue.png"
]


class FloatingTank:
    def __init__(self, window):
        self.window = window
        self.respawn()

    def respawn(self):
        filename = random.choice(TANK_FILENAMES)
        resource_path = f":tanks:{filename}"

        try:
            self.sprite = arcade.Sprite(resource_path)
        except Exception as e:
            print(f"Ошибка загрузки {resource_path}: {e}")
            self.sprite = arcade.SpriteSolidColor(60, 40, arcade.color.GRAY)

        scale_factor = self.window.width / 1920
        self.sprite.scale = 0.45 * scale_factor * 1.1

        self.sprite.center_x = random.uniform(40, self.window.width - 40)
        self.sprite.center_y = random.uniform(self.window.height + 50, self.window.height + 400)

        self.speed_y = random.uniform(35, 90) * (self.window.height / 1080)
        self.rotation_speed = random.uniform(-50, 50)
        self.direction = random.choice([-1, 1])
        self.sprite_all = arcade.SpriteList()
        self.sprite_all.append(self.sprite)

    def update(self, delta_time):
        self.sprite.center_y -= self.speed_y * delta_time
        self.sprite.angle += self.rotation_speed * self.direction * delta_time

        if self.sprite.center_y < -120:
            self.respawn()

    def draw(self):
        self.sprite_all.draw()


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        base_count = 12
        extra = max(0, int((self.window.width - 1920) / 400))
        self.floating_tanks = [FloatingTank(self.window) for _ in range(base_count + extra)]

        self.time = 0
        self.blink_timer = 0
        self.show_text = True

    def on_show_view(self):
        arcade.set_background_color((10, 18, 35))

    def on_update(self, delta_time):
        self.time += delta_time
        self.blink_timer += delta_time

        if self.blink_timer >= 0.7:
            self.show_text = not self.show_text
            self.blink_timer = 0

        for tank in self.floating_tanks:
            tank.update(delta_time)

    def on_draw(self):
        self.clear()

        w = self.window.width
        h = self.window.height

        scale = min(w / 1920, h / 1080)

        for tank in self.floating_tanks:
            tank.draw()

        arcade.draw_rect_filled(
            arcade.rect.XYWH(w/2, h/2, w, h),
            (0, 0, 0, 140)
        )

        arcade.draw_text(
            "ТАНЧИКИ",
            w / 2,
            h - 150 * scale,
            arcade.color.WHITE,
            font_size=88 * scale,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial Black"
        )

        arcade.draw_text(
            "2D БИТВА",
            w / 2,
            h - 235 * scale,
            arcade.color.LIGHT_BLUE,
            font_size=36 * scale,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial"
        )

        if self.show_text:
            arcade.draw_text(
                "НАЖМИ ПРОБЕЛ ЧТОБЫ НАЧАТЬ",
                w / 2,
                h // 2 - 30 * scale,
                arcade.color.WHITE,
                font_size=26 * scale,
                anchor_x="center",
                anchor_y="center",
                font_name="Arial"
            )

        arcade.draw_text(
            "WASD / стрелки — движение    ЛКМ — выстрел",
            w / 2,
            70 * scale,
            arcade.color.LIGHT_GRAY,
            font_size=17 * scale,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial"
        )

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            menu_view = WindowMenu()
            menu_view.setup()
            self.window.show_view(menu_view)
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()

