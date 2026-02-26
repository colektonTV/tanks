import arcade
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