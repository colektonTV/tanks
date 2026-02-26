import arcade

# Настройки
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Танчики: Плавное движение"
SPEED = 5

class Tank(arcade.Sprite):
    def __init__(self, color, x, y):
        # Рисуем простой квадрат-танк
        super().__init__()
        self.texture = arcade.make_soft_circle_texture(30, color)
        self.center_x = x
        self.center_y = y

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.AMAZON)
        
        self.tank1 = None
        self.tank2 = None
        self.player_list = None

    def setup(self):
        self.player_list = arcade.SpriteList()
        
        # Создаем двух игроков
        self.tank1 = Tank(arcade.color.RED, 200, 300)
        self.tank2 = Tank(arcade.color.BLUE, 600, 300)
        
        self.player_list.append(self.tank1)
        self.player_list.append(self.tank2)

    def on_draw(self):
        arcade.start_render()
        self.player_list.draw()
        arcade.draw_text("Игрок 1: WASD | Игрок 2: Стрелки", 10, 20, arcade.color.WHITE, 14)

    def on_key_press(self, key, modifiers):
        # --- УПРАВЛЕНИЕ ТАНКОМ 1 (WASD) ---
        if key == arcade.key.W:
            self.tank1.change_y = SPEED
        elif key == arcade.key.S:
            self.tank1.change_y = -SPEED
        elif key == arcade.key.A:
            self.tank1.change_x = -SPEED
        elif key == arcade.key.D:
            self.tank1.change_x = SPEED

        # --- УПРАВЛЕНИЕ ТАНКОМ 2 (СТРЕЛКИ) ---
        if key == arcade.key.UP:
            self.tank2.change_y = SPEED
        elif key == arcade.key.DOWN:
            self.tank2.change_y = -SPEED
        elif key == arcade.key.LEFT:
            self.tank2.change_x = -SPEED
        elif key == arcade.key.RIGHT:
            self.tank2.change_x = SPEED

    def on_key_release(self, key, modifiers):
        # Остановка Танка 1 при отпускании
        if key == arcade.key.W or key == arcade.key.S:
            self.tank1.change_y = 0
        elif key == arcade.key.A or key == arcade.key.D:
            self.tank1.change_x = 0

        # Остановка Танка 2 при отпускании
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.tank2.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.tank2.change_x = 0

    def on_update(self, delta_time):
        # Двигаем танки на основе их текущей скорости
        self.player_list.update()

        # Проверка границ, чтобы не уезжали за экран
        for tank in self.player_list:
            if tank.left < 0: tank.left = 0
            if tank.right > SCREEN_WIDTH: tank.right = SCREEN_WIDTH
            if tank.bottom < 0: tank.bottom = 0
            if tank.top > SCREEN_HEIGHT: tank.top = SCREEN_HEIGHT

if __name__ == "__main__":
    game = MyGame()
    game.setup()
    arcade.run()