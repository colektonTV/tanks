import arcade
import os
from windows.game.pouse import Pouse
import json
import math

# --- Константы ---
SCREEN_TITLE = "Танки: Битва на двоих"
TANK_SPEED = 5  # Скорость в пикселях в секунду (будет масштабироваться)
BULLET_SPEED = 20  # Скорость пули в пикселях в секунду

class GameView(arcade.View):
    def __init__(self, menu):
        super().__init__()
        self.menu = menu
        self.flag_deacrivate = False
        self.game_ended = False
        # Загрузка карты
        with open("data/level.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.select_map = data.get("map")
        
        with open("data/level.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.health = data.get("health_multiplier")
            self.health_red = self.health
            self.health_blue = self.health
            print("Количество жизней", self.health)
        
        # Загрузка количества раундов
        try:
            with open("data\level.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.max_rounds = data.get("rounds", 1)
                print(f"Загружено раундов: {self.max_rounds}")
        except:
            print("Файл настроек не найден, используется 1 раунд")
            self.max_rounds = 1
        
        # Переменные для раундов и счета
        self.current_round = 1
        self.round_timer = 0
        self.round_delay = 2  # Задержка между раундами в секундах
        self.round_active = True  # Флаг активного раунда
        self.round_winner = None  # Победитель раунда
        
        # Счет игроков
        self.score_wasd = 0  # Счет красного танка (WASD)
        self.score_arrows = 0  # Счет синего танка (стрелки)
        
        # Списки спрайтов
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.collision_list = arcade.SpriteList()
        self.backgr_list = arcade.SpriteList()
        
        # Камера
        self.camera = None
        
        # Границы карты
        self.map_left = 0
        self.map_right = 0
        self.map_bottom = 0
        self.map_top = 0
        
        # Физические движки
        self.physics_engine_wasd = None
        self.physics_engine_arrows = None
        
        # Танки
        self.tank_wasd = None
        self.tank_arrows = None
        
        # Масштабирование
        self.global_scale = 1.0
        self.screen_width = 0
        self.screen_height = 0
        
        # Путь к корневой папке
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_path = os.path.dirname(os.path.dirname(current_dir))

    
    def _calculate_scale(self):
        """Вычисляет масштаб на основе размера экрана и карты"""
        # Размер карты в тайлах для map_1.tmx
        map_tile_width = 60
        map_tile_height = 34
        tile_size = 70  # оригинальный размер тайла в пикселях
        
        # Оригинальный размер карты в пикселях
        original_map_width = map_tile_width * tile_size
        original_map_height = map_tile_height * tile_size
        
        # Получаем размер экрана
        self.screen_width = self.window.width
        self.screen_height = self.window.height
        
        # Вычисляем масштаб для заполнения экрана
        scale_x = self.screen_width / original_map_width
        scale_y = self.screen_height / original_map_height
        
        # Используем минимальный масштаб, чтобы карта полностью поместилась
        self.global_scale = min(scale_x, scale_y)
        
        print(f"Размер экрана: {self.screen_width}x{self.screen_height}")
        print(f"Оригинальный размер карты: {original_map_width}x{original_map_height}")
        print(f"Масштаб: {self.global_scale:.2f}")
        print(f"Новый размер карты: {original_map_width * self.global_scale:.0f}x{original_map_height * self.global_scale:.0f}")
        
        return self.global_scale
    
    def _reset_round(self):
        """Возвращает танки на стартовые позиции для нового раунда"""
        print(f"Сброс раунда {self.current_round}")
        
        # Очищаем пули и взрывы
        self.bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.health_red = self.health
        self.health_blue = self.health
        self.flag_deacrivate = False
        self.game_ended = False  # Сбрасываем флаг
        
        # Удаляем старые танки из списка
        self.player_list = arcade.SpriteList()
        
        # Создаем танки заново с правильным масштабом
        self._create_tanks()
        
        # Обновляем физику
        if len(self.collision_list) > 0:
            self.physics_engine_wasd = arcade.PhysicsEngineSimple(self.tank_wasd, self.collision_list)
            self.physics_engine_arrows = arcade.PhysicsEngineSimple(self.tank_arrows, self.collision_list)
        
        # Активируем раунд
        self.round_active = True
        self.round_winner = None
        
        print(f"Раунд {self.current_round} начался! Счет: {self.score_wasd}:{self.score_arrows}")
        
    def setup(self):
        """Настраиваем игру здесь"""
        # Вычисляем масштаб под текущий экран
        self._calculate_scale()
        
        # Очищаем списки
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.collision_list = arcade.SpriteList()
        self.backgr_list = arcade.SpriteList()


        # Создаём камеру
        self.camera = arcade.Camera2D()
        
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        
        # Пытаемся загрузить карту с вычисленным масштабом
        if not self._load_map():
            print("Не удалось загрузить карту, создаём простые стены...")
            self._create_simple_walls()
        
        # Определяем границы карты
        self._calculate_map_bounds()
        
        # Создаём танки с правильным масштабом
        self._create_tanks()
        
        # Создаём физические движки
        if len(self.collision_list) > 0:
            if self.tank_wasd:
                self.physics_engine_wasd = arcade.PhysicsEngineSimple(
                    self.tank_wasd, self.collision_list
                )
            
            if self.tank_arrows:
                self.physics_engine_arrows = arcade.PhysicsEngineSimple(
                    self.tank_arrows, self.collision_list
                )
        
        # Центрируем камеру на карте
        self._center_camera()
        
        # Сбрасываем счет
        self.score_wasd = 0
        self.score_arrows = 0
        self.current_round = 1
        self.round_active = True

    def _load_map(self):
        """Загружает карту с учетом масштаба экрана"""
        map_path = os.path.join(self.project_path, "textures", "map", self.select_map)
        
        print(f"Загружаем карту из: {map_path}")
        print(f"Масштаб карты: {self.global_scale:.2f}")
        
        if os.path.exists(map_path):
            try:
                # Грузим тайловую карту с вычисленным масштабом
                tile_map = arcade.load_tilemap(map_path, scaling=self.global_scale)
                
                # Получаем слои из карты
                if "walls" in tile_map.sprite_lists:
                    self.wall_list = tile_map.sprite_lists["walls"]
                    print(f"Загружено стен: {len(self.wall_list)}")
                
                if "colision" in tile_map.sprite_lists:
                    self.collision_list = tile_map.sprite_lists["colision"]
                    print(f"Загружено коллизий: {len(self.collision_list)}")
                
                if "backgr" in tile_map.sprite_lists:
                    self.backgr_list = tile_map.sprite_lists["backgr"]
                    print(f"Загружено фона: {len(self.backgr_list)}")
                elif len(self.wall_list) > 0:
                    self.collision_list = self.wall_list
                    print("Слой colision не найден, использую walls для коллизий")
                
                print(f"Карта успешно загружена!")
                return True
                
            except Exception as e:
                print(f"Ошибка при загрузке карты: {e}")
                return False
        else:
            print(f"Файл карты не найден: {map_path}")
            return False
    
    def _create_simple_walls(self):
        """Создает простые стены, если карта не загружена"""
        wall_path = os.path.join(self.project_path, "textures", "sprites", "blocks", "block.png")
        
        if os.path.exists(wall_path):
            wall_texture = arcade.load_texture(wall_path)
        else:
            wall_texture = None
        
        # Создаем граничные стены
        wall_size = 70 * self.global_scale
        wall_count_x = int(self.screen_width / wall_size) + 2
        wall_count_y = int(self.screen_height / wall_size) + 2
        
        for x in range(wall_count_x):
            for y in range(wall_count_y):
                if x == 0 or x == wall_count_x-1 or y == 0 or y == wall_count_y-1:
                    if wall_texture:
                        wall = arcade.Sprite(wall_path, scale=self.global_scale)
                    else:
                        wall = arcade.SpriteSolidColor(int(wall_size), int(wall_size), arcade.color.GRAY)
                    
                    wall.center_x = x * wall_size
                    wall.center_y = y * wall_size
                    self.wall_list.append(wall)
                    self.collision_list.append(wall)

    def _calculate_map_bounds(self):
        """Вычисляет границы карты на основе фона или стен"""
        if self.backgr_list and len(self.backgr_list) > 0:
            self.map_left = min(sprite.left for sprite in self.backgr_list)
            self.map_right = max(sprite.right for sprite in self.backgr_list)
            self.map_bottom = min(sprite.bottom for sprite in self.backgr_list)
            self.map_top = max(sprite.top for sprite in self.backgr_list)
        elif self.wall_list and len(self.wall_list) > 0:
            self.map_left = min(wall.left for wall in self.wall_list)
            self.map_right = max(wall.right for wall in self.wall_list)
            self.map_bottom = min(wall.bottom for wall in self.wall_list)
            self.map_top = max(wall.top for wall in self.wall_list)
        else:
            # Если ничего нет, используем размер экрана
            self.map_left = 0
            self.map_right = self.screen_width
            self.map_bottom = 0
            self.map_top = self.screen_height
            
        print(f"Границы карты: left={self.map_left:.0f}, right={self.map_right:.0f}, bottom={self.map_bottom:.0f}, top={self.map_top:.0f}")

    def _center_camera(self):
        """Центрирует камеру на карте"""
        if self.backgr_list or self.wall_list:
            # Находим центр карты
            center_x = (self.map_left + self.map_right) / 2
            center_y = (self.map_bottom + self.map_top) / 2
            
            # Устанавливаем камеру в центр карты
            self.camera.position = (center_x, center_y)
            
            print(f"Центр карты: ({center_x:.0f}, {center_y:.0f})")
        else:
            self.camera.position = (self.screen_width/2, self.screen_height/2)

    def _create_tanks(self):
        """Создаём танки с масштабом под текущее разрешение"""
        tank_red_path = os.path.join(self.project_path, "textures", "sprites", "tanks", "tank_red.png")
        tank_blue_path = os.path.join(self.project_path, "textures", "sprites", "tanks", "tank_blue.png")
        
        # Масштаб танков относительно карты
        map_width = self.map_right - self.map_left
        tank_scale = max(0.3, min(0.8, map_width / 2000))
        
        # Корректировка для разных карт
        if self.select_map == "map_1.tmx":
            tank_scale *= 1.2  # Для map_1 делаем танки чуть больше
        
        print(f"Масштаб танков: {tank_scale:.2f}")
        
        if os.path.exists(tank_red_path):
            self.tank_wasd = arcade.Sprite(tank_red_path, scale=tank_scale)
            print("Красный танк загружен")
        else:
            # Создаем прямоугольник пропорционального размера
            tank_size = int(60 * tank_scale)
            self.tank_wasd = arcade.SpriteSolidColor(tank_size, tank_size, arcade.color.RED)
            print("Красный танк не найден, создан прямоугольник")
        
        if os.path.exists(tank_blue_path):
            self.tank_arrows = arcade.Sprite(tank_blue_path, scale=tank_scale)
            print("Синий танк загружен")
        else:
            tank_size = int(60 * tank_scale)
            self.tank_arrows = arcade.SpriteSolidColor(tank_size, tank_size, arcade.color.BLUE)
            print("Синий танк не найден, создан прямоугольник")
        
        # Позиционируем танки
        self._position_tanks()
        
        self.player_list.append(self.tank_wasd)
        self.player_list.append(self.tank_arrows)
    
    def _position_tanks(self):
        """Позиционирует танки на карте"""
        if self.backgr_list or self.wall_list:
            # Используем границы карты
            map_center_x = (self.map_left + self.map_right) / 2
            map_width = self.map_right - self.map_left
            
            self.tank_wasd.center_x = self.map_left + map_width * 0.25
            self.tank_wasd.center_y = (self.map_bottom + self.map_top) / 2
            self.tank_wasd.angle = 0
            
            self.tank_arrows.center_x = self.map_left + map_width * 0.75
            self.tank_arrows.center_y = (self.map_bottom + self.map_top) / 2
            self.tank_arrows.angle = 0
        else:
            # Если карты нет, позиционируем по экрану
            self.tank_wasd.center_x = self.screen_width * 0.25
            self.tank_wasd.center_y = self.screen_height / 2
            
            self.tank_arrows.center_x = self.screen_width * 0.75
            self.tank_arrows.center_y = self.screen_height / 2

    def _fire_bullet(self, tank, speed=None):
        """Создает пулю в направлении танка"""
        if speed is None:
            speed = BULLET_SPEED * self.global_scale
        
        bullet_path = os.path.join(self.project_path, "textures", "sprites", "tanks", "bulletDark2_outline.png")
        
        if os.path.exists(bullet_path):
            bullet = arcade.Sprite(bullet_path, scale=2 * self.global_scale)
        else:
            bullet_size = int(20 * self.global_scale)
            bullet = arcade.SpriteSolidColor(bullet_size, bullet_size, arcade.color.YELLOW)
        
        # Смещение пули относительно танка (пропорционально размеру танка)
        offset = tank.height * 0.7
        
        # Определяем направление по углу танка
        if tank.angle == 180:  # вверх
            bullet.center_x = tank.center_x
            bullet.center_y = tank.center_y + offset
            bullet.change_x = 0
            bullet.change_y = speed
            bullet.angle = 180
        elif tank.angle == 360 or tank.angle == 0:  # вниз
            bullet.center_x = tank.center_x
            bullet.center_y = tank.center_y - offset
            bullet.change_x = 0
            bullet.change_y = -speed
            bullet.angle = 0
        elif tank.angle == 90:  # влево
            bullet.center_x = tank.center_x - offset
            bullet.center_y = tank.center_y
            bullet.change_x = -speed
            bullet.change_y = 0
            bullet.angle = 90
        elif tank.angle == 270:  # вправо
            bullet.center_x = tank.center_x + offset
            bullet.center_y = tank.center_y
            bullet.change_x = speed
            bullet.change_y = 0
            bullet.angle = 270
        
        self.bullet_list.append(bullet)

    def _keep_tank_in_bounds(self, tank):
        """Удерживает танк в границах карты"""
        if tank.left < self.map_left:
            tank.left = self.map_left
        if tank.right > self.map_right:
            tank.right = self.map_right
        if tank.bottom < self.map_bottom:
            tank.bottom = self.map_bottom
        if tank.top > self.map_top:
            tank.top = self.map_top

    def on_draw(self):
        self.clear()
        
        # Активируем камеру
        with self.camera.activate():
            # Рисуем все спрайты в координатах мира
            self.backgr_list.draw()
            self.wall_list.draw()
            self.player_list.draw()
            self.bullet_list.draw()
            self.explosion_list.draw()
        
        # Рисуем UI поверх всего (без камеры)
        # Отображаем счет
        arcade.draw_text(f"КРАСНЫЙ: {self.score_wasd}", 
                        20, self.screen_height - 50, 
                        arcade.color.RED, 24, bold=True)
        arcade.draw_text(f"СИНИЙ: {self.score_arrows}", 
                        20, self.screen_height - 80, 
                        arcade.color.BLUE, 24, bold=True)
        arcade.draw_text(f"РАУНД: {self.current_round}/{self.max_rounds}", 
                        self.screen_width - 200, self.screen_height - 50, 
                        arcade.color.WHITE, 24, bold=True)
        arcade.draw_text(f"Здоровье КРАСНЫЙ: {self.health_red}", self.screen_width - 400, 50, arcade.color.RED, 24, bold=True)
        arcade.draw_text(f"Здоровье СИНИЙ: {self.health_blue}", self.screen_width - 400, 20, arcade.color.BLUE, 24, bold=True)

        
        # Отображаем сообщения о конце раунда или игры
        if not self.round_active and self.round_winner:
            if self.current_round <= self.max_rounds and self.current_round < self.max_rounds:
                # Определяем цвет текста в зависимости от победителя
                if self.round_winner == "wasd":
                    winner_color = arcade.color.RED
                    winner_text = "КРАСНЫЙ"
                else:
                    winner_color = arcade.color.BLUE
                    winner_text = "СИНИЙ"
                

                arcade.draw_text(f"{winner_text} ВЫИГРАЛ РАУНД!", 
                                self.screen_width/2, self.screen_height/2 + 50, 
                                winner_color, 40, anchor_x="center", bold=True)
                arcade.draw_text(f"Следующий раунд через {max(0, int(self.round_delay - self.round_timer + 1))}...", 
                                self.screen_width/2, self.screen_height/2 - 20, 
                                arcade.color.WHITE, 30, anchor_x="center")
        
        # Отображаем финальный победитель
        if self.current_round > self.max_rounds:
            if self.score_wasd > self.score_arrows:
                winner_text = "КРАСНЫЙ ПОБЕДИЛ В ИГРЕ!"
                winner_color = arcade.color.RED
            elif self.score_arrows > self.score_wasd:
                winner_text = "СИНИЙ ПОБЕДИЛ В ИГРЕ!"
                winner_color = arcade.color.BLUE
            else:
                winner_text = "НИЧЬЯ!"
                winner_color = arcade.color.WHITE
            
            arcade.draw_text(winner_text, 
                            self.screen_width/2, self.screen_height/2, 
                            winner_color, 50, anchor_x="center", bold=True)
            arcade.draw_text("Нажмите ESC для выхода в меню", 
                            self.screen_width/2, self.screen_height/2 - 60, 
                            arcade.color.WHITE, 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        # Если игра закончена, только ESC работает
        if self.current_round > self.max_rounds:
            if key == arcade.key.ESCAPE:
                arcade.set_background_color((10, 18, 35))
                self.window.show_view(self.menu)

        # Если раунд не активен, не обрабатываем управление
        if not self.round_active:
            return
        
        if self.tank_wasd not in self.player_list or self.tank_arrows not in self.player_list:
            return
        
        # Масштабируем скорость под размер экрана
        scaled_speed = TANK_SPEED * self.global_scale

        # --- Управление танком WASD ---
        if key == arcade.key.W:
            self.tank_wasd.change_y = scaled_speed
            self.tank_wasd.change_x = 0
            self.tank_wasd.angle = 180
        elif key == arcade.key.S:
            self.tank_wasd.change_y = -scaled_speed
            self.tank_wasd.change_x = 0
            self.tank_wasd.angle = 360
        elif key == arcade.key.A:
            self.tank_wasd.change_x = -scaled_speed
            self.tank_wasd.change_y = 0
            self.tank_wasd.angle = 90
        elif key == arcade.key.D:
            self.tank_wasd.change_x = scaled_speed
            self.tank_wasd.change_y = 0
            self.tank_wasd.angle = 270

        # Стрельба для танка WASD
        if key == arcade.key.SPACE:
            self._fire_bullet(self.tank_wasd)

        # --- Управление танком стрелками ---
        if key == arcade.key.UP:
            self.tank_arrows.change_y = scaled_speed
            self.tank_arrows.change_x = 0
            self.tank_arrows.angle = 180
        elif key == arcade.key.DOWN:
            self.tank_arrows.change_y = -scaled_speed
            self.tank_arrows.change_x = 0
            self.tank_arrows.angle = 360
        elif key == arcade.key.LEFT:
            self.tank_arrows.change_x = -scaled_speed
            self.tank_arrows.change_y = 0
            self.tank_arrows.angle = 90
        elif key == arcade.key.RIGHT:
            self.tank_arrows.change_x = scaled_speed
            self.tank_arrows.change_y = 0
            self.tank_arrows.angle = 270

        # Стрельба для танка стрелками
        if key == arcade.key.ENTER:
            self._fire_bullet(self.tank_arrows)

        # Пауза
        if key == arcade.key.ESCAPE:
            pause_view = Pouse(game_view=self, menu=self.menu)
            pause_view.setup()
            self.window.show_view(pause_view)

    def on_key_release(self, key, modifiers):
        if self.tank_wasd in self.player_list:
            if key in (arcade.key.W, arcade.key.S): 
                self.tank_wasd.change_y = 0
            if key in (arcade.key.A, arcade.key.D): 
                self.tank_wasd.change_x = 0
        
        if self.tank_arrows in self.player_list:
            if key in (arcade.key.UP, arcade.key.DOWN): 
                self.tank_arrows.change_y = 0
            if key in (arcade.key.LEFT, arcade.key.RIGHT): 
                self.tank_arrows.change_x = 0

    def on_update(self, delta_time):
        # Если игра закончена, ничего не обновляем
        if self.current_round > self.max_rounds:
            return
        # Если раунд активен, обновляем игру
        if self.round_active:
            # Обновляем физику
            if self.physics_engine_wasd and self.tank_wasd in self.player_list:
                self.physics_engine_wasd.update()
            
            if self.physics_engine_arrows and self.tank_arrows in self.player_list:
                self.physics_engine_arrows.update()
            
            # Удерживаем танки в границах карты
            if self.tank_wasd in self.player_list:
                self._keep_tank_in_bounds(self.tank_wasd)
            
            if self.tank_arrows in self.player_list:
                self._keep_tank_in_bounds(self.tank_arrows)
            
            self.bullet_list.update()
            self.explosion_list.update()

            # --- Логика попаданий ---
            bullets_to_remove = []

            for bullet in self.bullet_list:
                # Проверяем столкновение с игроками
                hit_list = arcade.check_for_collision_with_list(bullet, self.player_list)
                
                for hit in hit_list:
                    # Определяем, какой танк уничтожен
                    if hit == self.tank_wasd and int(self.health_red) == 1:
                        self.round_winner = "arrows"  # Победил синий
                        self.health_red = 0
                        self.score_arrows += 1
                        self.flag_deacrivate = True
                        print(f"Красный танк уничтожен! Синий получает очко. Счет: {self.score_wasd}:{self.score_arrows}")
                    elif hit == self.tank_arrows and int(self.health_blue) == 1:
                        self.round_winner = "wasd"  # Победил красный
                        self.health_blue = 0
                        self.score_wasd += 1
                        self.flag_deacrivate = True
                        print(f"Синий танк уничтожен! Красный получает очко. Счет: {self.score_wasd}:{self.score_arrows}")
                    
                    if hit == self.tank_wasd and int(self.health_red) > 1:
                        self.health_red -= 1
                        bullets_to_remove.append(bullet)

                    elif hit == self.tank_arrows and int(self.health_blue) > 1:
                        self.health_blue -= 1
                        bullets_to_remove.append(bullet)
                    
                    if self.flag_deacrivate == True:
                        # Удаляем танк
                        hit.remove_from_sprite_lists()
                        bullets_to_remove.append(bullet)
                        
                        # Деактивируем раунд
                        self.round_active = False
                        self.round_timer = 0
                        break

                # Проверяем столкновение со стенами
                if self.collision_list:
                    wall_hits = arcade.check_for_collision_with_list(bullet, self.collision_list)
                    if wall_hits:
                        bullets_to_remove.append(bullet)
                
                # Удаление пули за пределами карты
                if self.backgr_list or self.wall_list:
                    if (bullet.left > self.map_right + 100 or 
                        bullet.right < self.map_left - 100 or 
                        bullet.bottom > self.map_top + 100 or 
                        bullet.top < self.map_bottom - 100):
                        bullets_to_remove.append(bullet)

            for bullet in bullets_to_remove:
                if bullet in self.bullet_list:
                    bullet.remove_from_sprite_lists()
        
        # Если раунд не активен (кто-то умер), обрабатываем переход к следующему раунду
        else:            
            self.round_timer += delta_time
            
            # Проверяем, закончились ли все раунды
            if self.current_round >= self.max_rounds:
                # Это был последний раунд - показываем финал сразу
                if not hasattr(self, 'game_ended') or not self.game_ended:
                    print(f"Игра окончена! Финальный счет: {self.score_wasd}:{self.score_arrows}")
                    self.game_ended = True
                    self.current_round = self.max_rounds + 1  # Переходим в состояние финала
            else:
                # Если это не последний раунд, ждем задержку перед следующим
                if self.round_timer >= self.round_delay:
                    self.current_round += 1
                    self._reset_round()