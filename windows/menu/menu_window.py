import arcade
from arcade.gui import UIManager, UIFlatButton
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
import random
from windows.buttons.button import Button
from windows.menu.settings import Settings

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
        self.buttons = []

    def setup(self):
        base_count = 12
        extra = max(0, int((self.window.width - 1920) / 400))
        self.floating_tanks = [
            FloatingTank(self.window) for _ in range(base_count + extra)
        ]

        arcade.set_background_color((10, 18, 35))
        self.manager = UIManager()
        self.manager.enable()

        center_x = self.window.width // 2
        center_y = self.window.height // 2
        
        self.button_play = Button(
            "Играть", 
            center_x, 
            center_y + 70, 
            300, 
            60, 
            color=(186, 183, 182), 
            color2=(0, 0, 0), 
            hover_color=(144, 144, 144), 
            click_color=(255,255,255),
            callback=self.on_play_click
        )
        
        self.button_settings = Button(
            "Настройки", 
            center_x, 
            center_y, 
            300, 
            60, 
            color=(186, 183, 182), 
            color2=(0, 0, 0), 
            hover_color=(144, 144, 144), 
            click_color=(255,255,255),
            callback=self.on_settings_click
        )
        
        self.button_exit = Button(
            "Выйти", 
            center_x, 
            center_y - 70, 
            300, 
            60, 
            color=(186, 183, 182), 
            color2=(0, 0, 0), 
            hover_color=(144, 144, 144), 
            click_color=(255,255,255),
            callback=self.on_exit_click
        )
        
        self.buttons = [self.button_play, self.button_settings, self.button_exit]

    def on_play_click(self):
        pass
        # game_view = GameView()
        # game_view.setup()
        # self.window.show_view(game_view)
    
    def on_settings_click(self):
        print("Настройки нажато!")
        settings_view = Settings()
        settings_view.setup()
        self.window.show_view(settings_view)
    
    def on_exit_click(self):
        print("Выход из игры")
        arcade.exit()

    def on_update(self, delta_time):
        for tank in self.floating_tanks:
            tank.update(delta_time)

    def on_draw(self):
        self.clear()

        for tank in self.floating_tanks:
            tank.draw()

        if self.manager:
            self.manager.draw()
        
        for button in self.buttons:
            button.draw()
    
    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.check_hover(x, y)
    
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn in self.buttons:
                btn.on_mouse_press(x, y)
    
    def on_mouse_release(self, x, y, button, modifiers):
            for btn in self.buttons:
                btn.on_mouse_release()