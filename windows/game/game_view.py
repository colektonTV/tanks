import arcade
import os
from windows.game.pouse import Pouse
import json

# --- Константы ---
SCREEN_WIDTH = 1920  # Full HD ширина
SCREEN_HEIGHT = 1080  # Full HD высота
SCREEN_TITLE = "Танки: Битва на двоих"
TANK_SPEED = 8  # Увеличил скорость для большого экрана
BULLET_SPEED = 7

class GameView(arcade.View):
    def __init__(self, menu):
        super().__init__()
        self.menu = menu
        with open("data/level.json", "r", encoding="utf-8") as f:
            fs = f.read()
            data = json.loads(fs)
            map_value = data.get("map")
            self.select_map = map_value 
        # Списки спрайтов
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.collision_list = arcade.SpriteList()
        
        # Камера
        self.camera = None
        
        # Границы карты
        self.map_left = 0
        self.map_right = 0
        self.map_bottom = 0
        self.map_top = 0
        
        # Физические движки для каждого танка
        self.physics_engine_wasd = None
        self.physics_engine_arrows = None

        # Танки
        self.tank_wasd = None
        self.tank_arrows = None
        
        # Путь к корневой папке проекта
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_path = os.path.dirname(os.path.dirname(current_dir))
        print(f"Корневая папка проекта: {self.project_path}")

    def setup(self):
        """Настраиваем игру здесь"""
        # Очищаем списки
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.collision_list = arcade.SpriteList()
        self.backgr_list = arcade.SpriteList()
        
        # Создаем окно
        if not self.window:
            self.window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=True)  # Полноэкранный режим
        
        # Создаём камеру
        self.camera = arcade.Camera2D()
        
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        
        # Пытаемся загрузить карту, если не получается - создаём простые стены
        if not self._load_map():
            print("Не удалось загрузить карту, создаём простые стены...")
        
        # Определяем границы карты
        self._calculate_map_bounds()
        
        # Создаём танки
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

    def _load_map(self):
        
        """Загружает карту из папки textures/map"""
        map_path = os.path.join(self.project_path, "textures", "map", self.select_map)
        
        print(f"Загружаем карту из: {map_path}")
        
        if os.path.exists(map_path):
            try:
                # Получаем размеры карты из TMX файла
                # Размер карты в тайлах: 60x34
                # Размер тайла: 70x70 пикселей
                map_tile_width = 60
                map_tile_height = 34
                tile_size = 70
                
                # Вычисляем масштаб для заполнения экрана
                # Оставляем 10% отступов по краям
                margin_percent = 0.9
                
                # Масштаб по ширине и высоте
                scale_x = (SCREEN_WIDTH * margin_percent) / (map_tile_width * tile_size)
                scale_y = (SCREEN_HEIGHT * margin_percent) / (map_tile_height * tile_size)
                
                # Берём меньший масштаб, чтобы карта полностью поместилась
                scale = min(scale_x, scale_y)
                
                print(f"Масштаб карты для Full HD: {scale:.2f}")
                print(f"Размер карты после масштабирования: {map_tile_width * tile_size * scale:.0f} x {map_tile_height * tile_size * scale:.0f}")
                
                # Грузим тайловую карту с вычисленным масштабом
                tile_map = arcade.load_tilemap(map_path, scaling=scale-0.04)
                
                # Получаем слои из карты
                if "walls" in tile_map.sprite_lists:
                    self.wall_list = tile_map.sprite_lists["walls"]
                    print(f"Загружено стен: {len(self.wall_list)}")
                
                if "colision" in tile_map.sprite_lists:
                    self.collision_list = tile_map.sprite_lists["colision"]
                    print(f"Загружено коллизий: {len(self.collision_list)}")
                if "backgr" in tile_map.sprite_lists:
                    self.backgr_list= tile_map.sprite_lists["backgr"]
                    print(f"Загружено коллизий: {len(self.collision_list)}")
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

    def _calculate_map_bounds(self):
        """Вычисляет границы карты на основе стен"""
        if self.wall_list:
            self.map_left = min(wall.left for wall in self.backgr_list)
            self.map_right = max(wall.right for wall in self.backgr_list)
            self.map_bottom = min(wall.bottom for wall in self.backgr_list)
            self.map_top = max(wall.top for wall in self.backgr_list)
            
            print(f"Границы карты: left={self.map_left:.0f}, right={self.map_right:.0f}, bottom={self.map_bottom:.0f}, top={self.map_top:.0f}")

    def _center_camera(self):
        """Центрирует камеру на карте"""
        if self.wall_list:
            # Находим центр карты
            center_x = (self.map_left + self.map_right) / 2
            center_y = (self.map_bottom + self.map_top) / 2
            
            # Устанавливаем камеру в центр карты
            self.camera.position = (center_x, center_y)
            
            print(f"Карта занимает область: x=[{self.map_left:.0f}, {self.map_right:.0f}], y=[{self.map_bottom:.0f}, {self.map_top:.0f}]")
            print(f"Размер карты: {self.map_right - self.map_left:.0f} x {self.map_top - self.map_bottom:.0f}")
            print(f"Центр карты: ({center_x:.0f}, {center_y:.0f})")


    def _create_tanks(self):
        """Создаём танки с масштабом под Full HD"""
        tank_red_path = os.path.join(self.project_path, "textures", "sprites", "tanks", "tank_red.png")
        tank_blue_path = os.path.join(self.project_path, "textures", "sprites", "tanks", "tank_blue.png")
        
        print(f"Ищем красный танк: {tank_red_path}")
        print(f"Ищем синий танк: {tank_blue_path}")
        
        if self.select_map == "map_1.tmx":
            tank_scale = 0.8
        else:
            tank_scale = 0.6
        
        if os.path.exists(tank_red_path):
            self.tank_wasd = arcade.Sprite(tank_red_path, scale=tank_scale)
            print("Красный танк загружен")
        else:
            self.tank_wasd = arcade.SpriteSolidColor(60, 60, arcade.color.RED)
            print("Красный танк не найден, создан прямоугольник")
        
        if os.path.exists(tank_blue_path):
            self.tank_arrows = arcade.Sprite(tank_blue_path, scale=tank_scale)
            print("Синий танк загружен")
        else:
            self.tank_arrows = arcade.SpriteSolidColor(60, 60, arcade.color.BLUE)
            print("Синий танк не найден, создан прямоугольник")
        
        # Позиционируем танки в пределах карты
        # Используем 1/4 и 3/4 ширины карты, но в пределах границ
        map_center_x = (self.map_left + self.map_right) / 2
        map_width = self.map_right - self.map_left
        
        self.tank_wasd.center_x = self.map_left + map_width * 0.25
        self.tank_wasd.center_y = (self.map_bottom + self.map_top) / 2
        
        self.tank_arrows.center_x = self.map_left + map_width * 0.75
        self.tank_arrows.center_y = (self.map_bottom + self.map_top) / 2
        
        self.player_list.append(self.tank_wasd)
        self.player_list.append(self.tank_arrows)

    def _fire_bullet(self, tank, direction_x):
        """Создаёт пулю"""
        bullet = arcade.SpriteSolidColor(15, 8, arcade.color.YELLOW)  # Увеличил пули для Full HD
        bullet.center_x = tank.center_x
        bullet.center_y = tank.center_y
        bullet.change_x = direction_x
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
            if self.wall_list:
                self.wall_list.draw()
            self.backgr_list.draw()
            self.player_list.draw()
            self.bullet_list.draw()
            self.explosion_list.draw()
        
        # Рисуем UI поверх всего (без камеры)
        if len(self.player_list) < 2:
            arcade.draw_text("ИГРА ОКОНЧЕНА", 
                           SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 
                           arcade.color.WHITE, 50, anchor_x="center")  # Увеличил шрифт

    def on_key_press(self, key, modifiers):
        if self.tank_wasd not in self.player_list or self.tank_arrows not in self.player_list:
            return
            
        # --- Управление WASD ---
        if key == arcade.key.W: 
            self.tank_wasd.change_y = TANK_SPEED
        elif key == arcade.key.S: 
            self.tank_wasd.change_y = -TANK_SPEED
        elif key == arcade.key.A: 
            self.tank_wasd.change_x = -TANK_SPEED
        elif key == arcade.key.D: 
            self.tank_wasd.change_x = TANK_SPEED
        
        # Стрельба WASD (Space)
        if key == arcade.key.SPACE:
            self._fire_bullet(self.tank_wasd, BULLET_SPEED)

        # --- Управление СТРЕЛКИ ---
        if key == arcade.key.UP: 
            self.tank_arrows.change_y = TANK_SPEED
        elif key == arcade.key.DOWN: 
            self.tank_arrows.change_y = -TANK_SPEED
        elif key == arcade.key.LEFT: 
            self.tank_arrows.change_x = -TANK_SPEED
        elif key == arcade.key.RIGHT: 
            self.tank_arrows.change_x = TANK_SPEED

        # Стрельба Arrows (Enter)
        if key == arcade.key.ENTER:
            self._fire_bullet(self.tank_arrows, -BULLET_SPEED)
        
        if key == arcade.key.ESCAPE:
            pause_view = Pouse(game_view=self, menu=self.menu)
            pause_view.setup()  # Передаём текущий вид, чтобы вернуться
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
                hit.remove_from_sprite_lists()
                bullets_to_remove.append(bullet)
                
                explosion = arcade.SpriteSolidColor(40, 40, arcade.color.ORANGE)  # Увеличил взрыв
                explosion.center_x = hit.center_x
                explosion.center_y = hit.center_y
                self.explosion_list.append(explosion)
                break

            # Проверяем столкновение со стенами
            if self.collision_list:
                wall_hits = arcade.check_for_collision_with_list(bullet, self.collision_list)
                if wall_hits:
                    bullets_to_remove.append(bullet)
            
            # Удаление пули за пределами карты
            if self.wall_list:
                if (bullet.left > self.map_right + 100 or 
                    bullet.right < self.map_left - 100 or 
                    bullet.bottom > self.map_top + 100 or 
                    bullet.top < self.map_bottom - 100):
                    bullets_to_remove.append(bullet)
        
        for bullet in bullets_to_remove:
            if bullet in self.bullet_list:
                bullet.remove_from_sprite_lists()