import arcade
from arcade.gui import UIManager, UIFlatButton
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
import random


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
        self.sprite.center_y = random.uniform(
            self.window.height + 50,
            self.window.height + 400
        )

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


class WindowMenu(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = None
        self.floating_tanks = []

    def setup(self):
        base_count = 12
        extra = max(0, int((self.window.width - 1920) / 400))
        self.floating_tanks = [
            FloatingTank(self.window) for _ in range(base_count + extra)
        ]

        arcade.set_background_color((10, 18, 35))
        self.manager = UIManager()
        self.manager.enable()

        button_box = UIBoxLayout(vertical=True, space_between=20)

        self._add_buttons(button_box)

        anchor = UIAnchorLayout()
        anchor.add(button_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

    def _add_buttons(self, button_box):
        play_btn = UIFlatButton(
            text="ИГРАТЬ",
            width=300,
            height=70,
            color=arcade.color.WHITE,
            hover_color=arcade.color.LIGHT_GRAY,
            press_color=arcade.color.GRAY,
            text_color=arcade.color.BLACK,
            text_color_hover=arcade.color.BLACK,
            text_color_press=arcade.color.BLACK
        )
        play_btn.on_click = lambda e: print("-----")
        button_box.add(play_btn)

        settings_btn = UIFlatButton(
            text="НАСТРОЙКИ",
            width=300,
            height=60,
            color=arcade.color.WHITE,
            hover_color=arcade.color.LIGHT_GRAY,
            press_color=arcade.color.GRAY,
            text_color=arcade.color.BLACK,
            text_color_hover=arcade.color.BLACK,
            text_color_press=arcade.color.BLACK
        )
        settings_btn.on_click = lambda e: print("------")
        button_box.add(settings_btn)

        exit_btn = UIFlatButton(
            text="ВЫХОД",
            width=300,
            height=60,
            color=arcade.color.WHITE,
            hover_color=arcade.color.LIGHT_GRAY,
            press_color=arcade.color.GRAY,
            text_color=arcade.color.BLACK,
            text_color_hover=arcade.color.BLACK,
            text_color_press=arcade.color.BLACK
        )
        exit_btn.on_click = lambda e: arcade.exit()
        button_box.add(exit_btn)

    def on_update(self, delta_time):
        for tank in self.floating_tanks:
            tank.update(delta_time)

    def on_draw(self):
        self.clear()

        for tank in self.floating_tanks:
            tank.draw()

        if self.manager:
            self.manager.draw()