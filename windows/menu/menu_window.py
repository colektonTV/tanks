import arcade
from arcade.gui import UIManager
from windows.buttons.button import Button
from windows.menu.settings import Settings
from textures.animation.anim_tank import FloatingTank
from windows.game.game_view import GameView


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
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)
    
    def on_settings_click(self):
        settings_view = Settings(menu_view=self)
        settings_view.setup()
        self.window.show_view(settings_view)
    
    def on_exit_click(self):
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