import arcade

# --- Константы ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Танки: Битва на двоих"
TANK_SPEED = 4
BULLET_SPEED = 7

class GameView(arcade.View):
    def __init__(self):
        super().__init__()  # Убрали лишние аргументы!
        
        # Списки спрайтов
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList() # Для твоей анимации

        # Танки
        self.tank_wasd = None
        self.tank_arrows = None

    def setup(self):
        # Создаем окно, если его еще нет
        if not self.window:
            self.window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        
        # 1. ЗАМЕНИ НА СВОИ ФАЙЛЫ ТАНКОВ
        self.tank_wasd = arcade.Sprite(":tanks:tank_red.png", scale=1.0)
        self.tank_wasd.center_x = 150
        self.tank_wasd.center_y = 300

        self.tank_arrows = arcade.Sprite(":tank:tank_blue.png", scale=1.0)
        self.tank_arrows.center_x = 650
        self.tank_arrows.center_y = 300

        self.player_list.append(self.tank_wasd)
        self.player_list.append(self.tank_arrows)

    def on_draw(self):
        arcade.start_render()
        self.player_list.draw()
        self.bullet_list.draw()
        self.explosion_list.draw()
        
        if len(self.player_list) < 2:
            # Используем Text объект вместо draw_text для лучшей производительности
            text = arcade.Text("ИГРА ОКОНЧЕНА", 
                              SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 
                              arcade.color.WHITE, 30, anchor_x="center")
            text.draw()

    def on_key_press(self, key, modifiers):
        # --- Управление WASD ---
        if key == arcade.key.W: self.tank_wasd.change_y = TANK_SPEED
        elif key == arcade.key.S: self.tank_wasd.change_y = -TANK_SPEED
        elif key == arcade.key.A: self.tank_wasd.change_x = -TANK_SPEED
        elif key == arcade.key.D: self.tank_wasd.change_x = TANK_SPEED
        
        # Стрельба WASD (Space)
        if key == arcade.key.SPACE and self.tank_wasd in self.player_list:
            # 2. ЗАМЕНИ НА СВОЙ ФАЙЛ ПУЛИ
            bullet = arcade.Sprite(":tank:bulletDark2_outline.png", scale=0.5)
            bullet.center_x = self.tank_wasd.center_x
            bullet.center_y = self.tank_wasd.center_y
            bullet.change_x = 8 # Летит вправо (можешь менять логику)
            self.bullet_list.append(bullet)

        # --- Управление СТРЕЛКИ ---
        if key == arcade.key.UP: self.tank_arrows.change_y = TANK_SPEED
        elif key == arcade.key.DOWN: self.tank_arrows.change_y = -TANK_SPEED
        elif key == arcade.key.LEFT: self.tank_arrows.change_x = -TANK_SPEED
        elif key == arcade.key.RIGHT: self.tank_arrows.change_x = TANK_SPEED

        # Стрельба Arrows (Enter)
        if key == arcade.key.ENTER and self.tank_arrows in self.player_list:
            bullet = arcade.Sprite(":tank:bulletDark2_outline.png", scale=0.5)
            bullet.center_x = self.tank_arrows.center_x
            bullet.center_y = self.tank_arrows.center_y
            bullet.change_x = -8 # Летит влево
            self.bullet_list.append(bullet)

    def on_key_release(self, key, modifiers):
        # Остановка WASD
        if key in (arcade.key.W, arcade.key.S): self.tank_wasd.change_y = 0
        if key in (arcade.key.A, arcade.key.D): self.tank_wasd.change_x = 0
        # Остановка Arrows
        if key in (arcade.key.UP, arcade.key.DOWN): self.tank_arrows.change_y = 0
        if key in (arcade.key.LEFT, arcade.key.RIGHT): self.tank_arrows.change_x = 0

    def on_update(self, delta_time):
        self.player_list.update()
        self.bullet_list.update()
        self.explosion_list.update() # Обновление анимаций

        # --- Логика попаданий ---
        for bullet in self.bullet_list:
            # Попали во второго игрока?
            hit_list = arcade.check_for_collision_with_list(bullet, self.player_list)
            
            for hit in hit_list:
                # 3. СЮДА ВСТАВЬ СВОЮ АНИМАЦИЮ ВЗРЫВА
                # Пример: создание спрайта взрыва на месте попадания
                # explosion = MyExplosionSprite(self.explosion_textures)
                # explosion.center_x = hit.center_x
                # self.explosion_list.append(explosion)
                
                hit.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
                break  # Пуля уничтожена, выходим из цикла

            # Удаление пули за экраном
            if bullet.left > SCREEN_WIDTH or bullet.right < 0:
                bullet.remove_from_sprite_lists()

        # Границы экрана
        for tank in self.player_list:
            if tank.left < 0: tank.left = 0
            if tank.right > SCREEN_WIDTH: tank.right = SCREEN_WIDTH
            if tank.bottom < 0: tank.bottom = 0
            if tank.top > SCREEN_HEIGHT: tank.top = SCREEN_HEIGHT