import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Танки: Свои текстуры"
SPEED = 5

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.GRAY)
        
        self.player_list = None
        self.tank_wasd = None
        self.tank_arrows = None

    def setup(self):
        self.player_list = arcade.SpriteList()

        #ЗАМЕНИ НАЗВАНИЯ ФАЙЛОВ ЗДЕСЬ
        #scale=1.0 — это оригинальный размер картинки
        self.tank_wasd = arcade.Sprite("tank_1.png", scale=1.0) 
        self.tank_wasd.center_x = 200
        self.tank_wasd.center_y = 300
        
        self.tank_arrows = arcade.Sprite("tank_2.png", scale=1.0)
        self.tank_arrows.center_x = 600
        self.tank_arrows.center_y = 300
        
        self.player_list.append(self.tank_wasd)
        self.player_list.append(self.tank_arrows)

    def on_draw(self):
        arcade.start_render()
        self.player_list.draw()
        arcade.draw_text("Игрок 1: WASD | Игрок 2: СТРЕЛКИ", 10, 20, arcade.color.BLACK, 12)

    def on_key_press(self, key, modifiers):
        #УПРАВЛЕНИЕ WASD (Первый танк)
        if key == arcade.key.W: self.tank_wasd.change_y = SPEED
        elif key == arcade.key.S: self.tank_wasd.change_y = -SPEED
        elif key == arcade.key.A: self.tank_wasd.change_x = -SPEED
        elif key == arcade.key.D: self.tank_wasd.change_x = SPEED

        #УПРАВЛЕНИЕ СТРЕЛКАМИ (Второй танк)
        if key == arcade.key.UP: self.tank_arrows.change_y = SPEED
        elif key == arcade.key.DOWN: self.tank_arrows.change_y = -SPEED
        elif key == arcade.key.LEFT: self.tank_arrows.change_x = -SPEED
        elif key == arcade.key.RIGHT: self.tank_arrows.change_x = SPEED

    def on_key_release(self, key, modifiers):
        #Плавная остановка WASD
        if key in (arcade.key.W, arcade.key.S): self.tank_wasd.change_y = 0
        if key in (arcade.key.A, arcade.key.D): self.tank_wasd.change_x = 0

        # Плавная остановка СТРЕЛОК
        if key in (arcade.key.UP, arcade.key.DOWN): self.tank_arrows.change_y = 0
        if key in (arcade.key.LEFT, arcade.key.RIGHT): self.tank_arrows.change_x = 0

    def on_update(self, delta_time):
        self.player_list.update()
        
        #Чтобы не уезжали за границы
        for tank in self.player_list:
            if tank.left < 0: tank.left = 0
            elif tank.right > SCREEN_WIDTH: tank.right = SCREEN_WIDTH
            if tank.bottom < 0: tank.bottom = 0
            elif tank.top > SCREEN_HEIGHT: tank.top = SCREEN_HEIGHT

if __name__ == "__main__":
    game = MyGame()
    game.setup()
    arcade.run()
