import arcade
import os
import json
import random
import math
from windows.game.pause import Pause
from arcade.particles import FadeParticle, Emitter, EmitBurst
from arcade import SpriteList, Sprite, Camera2D, PhysicsEngineSimple
from arcade import draw_text, set_background_color, color
from arcade import check_for_collision_with_list
from arcade import load_tilemap

TANK_SPEED = 5
BULLET_SPEED = 20

SPARK_TEX = [
    arcade.make_soft_circle_texture(8, arcade.color.PASTEL_YELLOW),
    arcade.make_soft_circle_texture(8, arcade.color.PEACH),
    arcade.make_soft_circle_texture(8, arcade.color.BABY_BLUE),
    arcade.make_soft_circle_texture(8, arcade.color.ELECTRIC_CRIMSON),
]

SMOKE_TEX = arcade.make_soft_circle_texture(20, arcade.color.LIGHT_GRAY, 255, 80)


def gravity_drag(p):
    p.change_y += -0.03
    p.change_x *= 0.92
    p.change_y *= 0.92


def smoke_mutator(p):
    p.scale_x *= 1.02
    p.scale_y *= 1.02
    p.alpha = max(0, p.alpha - 2)


def make_explosion(x, y, count=80):
    return Emitter(
        center_xy=(x, y),
        emit_controller=EmitBurst(count),
        particle_factory=lambda e: FadeParticle(
            filename_or_texture=random.choice(SPARK_TEX),
            change_xy=arcade.math.rand_in_circle((0.0, 0.0), 9.0),
            lifetime=random.uniform(0.5, 1.1),
            start_alpha=255,
            end_alpha=0,
            scale=random.uniform(0.35, 0.6),
            mutation_callback=gravity_drag,
        ),
    )


def make_smoke_puff(x, y):
    return Emitter(
        center_xy=(x, y),
        emit_controller=EmitBurst(12),
        particle_factory=lambda e: FadeParticle(
            filename_or_texture=SMOKE_TEX,
            change_xy=arcade.math.rand_in_circle((0.0, 0.0), 0.6),
            lifetime=random.uniform(1.5, 2.5),
            start_alpha=200,
            end_alpha=0,
            scale=random.uniform(0.6, 0.9),
            mutation_callback=smoke_mutator,
        ),
    )


class GameView(arcade.View):
    def __init__(self, menu):
        super().__init__()
        self.menu = menu
        self.flag_deacrivate = False
        self.game_ended = False

        with open("data/level.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.select_map = data.get("map")

        with open("data/level.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.health = data.get("health_multiplier")
            self.health_red = self.health
            self.health_blue = self.health

        try:
            with open("data/level.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.max_rounds = data.get("rounds", 1)
        except Exception:
            self.max_rounds = 1

        self.current_round = 1
        self.round_timer = 0
        self.round_delay = 2
        self.round_active = True
        self.round_winner = None

        self.score_wasd = 0
        self.score_arrows = 0

        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.emitters = []
        self.wall_list = arcade.SpriteList()
        self.collision_list = arcade.SpriteList()
        self.backgr_list = arcade.SpriteList()

        self.camera = None

        self.map_left = 0
        self.map_right = 0
        self.map_bottom = 0
        self.map_top = 0

        self.physics_engine_wasd = None
        self.physics_engine_arrows = None

        self.tank_wasd = None
        self.tank_arrows = None

        self.global_scale = 1.0
        self.screen_width = 0
        self.screen_height = 0

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_path = os.path.dirname(os.path.dirname(current_dir))

        self.shoot_sound = arcade.load_sound(":resources:/sounds/laser1.wav")
        self.explosion_sound = arcade.load_sound(":resources:/sounds/explosion1.wav")
        self.background_music = arcade.load_sound(":resources:/music/funkyrobot.mp3")
        self.background_player = None

    def on_show_view(self):
        if self.background_music:
            self.background_player = self.background_music.play(looping=True, volume=0.3)

    def on_hide_view(self):
        if self.background_player:
            arcade.stop_sound(self.background_player)
            self.background_player = None

    def _calculate_scale(self):
        map_tile_width = 60
        map_tile_height = 34
        tile_size = 70

        original_map_width = map_tile_width * tile_size
        original_map_height = map_tile_height * tile_size

        self.screen_width = self.window.width
        self.screen_height = self.window.height

        scale_x = self.screen_width / original_map_width
        scale_y = self.screen_height / original_map_height

        self.global_scale = min(scale_x, scale_y)

        return self.global_scale

    def _reset_round(self):
        self.bullet_list = arcade.SpriteList()
        self.emitters = []
        self.health_red = self.health
        self.health_blue = self.health
        self.flag_deacrivate = False
        self.game_ended = False

        self.player_list = arcade.SpriteList()

        self._create_tanks()

        if len(self.collision_list) > 0:
            self.physics_engine_wasd = arcade.PhysicsEngineSimple(
                self.tank_wasd, self.collision_list
            )
            self.physics_engine_arrows = arcade.PhysicsEngineSimple(
                self.tank_arrows, self.collision_list
            )

        self.round_active = True
        self.round_winner = None

    def setup(self):
        self._calculate_scale()

        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.emitters = []
        self.wall_list = arcade.SpriteList()
        self.collision_list = arcade.SpriteList()
        self.backgr_list = arcade.SpriteList()

        self.camera = arcade.Camera2D()

        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        if not self._load_map():
            self._create_simple_walls()

        self._calculate_map_bounds()

        self._create_tanks()

        if len(self.collision_list) > 0:
            if self.tank_wasd:
                self.physics_engine_wasd = arcade.PhysicsEngineSimple(
                    self.tank_wasd, self.collision_list
                )

            if self.tank_arrows:
                self.physics_engine_arrows = arcade.PhysicsEngineSimple(
                    self.tank_arrows, self.collision_list
                )

        self._center_camera()

        self.score_wasd = 0
        self.score_arrows = 0
        self.current_round = 1
        self.round_active = True

    def _load_map(self):
        map_path = os.path.join(self.project_path, "textures", "map", self.select_map)

        if os.path.exists(map_path):
            try:
                tile_map = arcade.load_tilemap(map_path, scaling=self.global_scale)

                if "walls" in tile_map.sprite_lists:
                    self.wall_list = tile_map.sprite_lists["walls"]

                if "colision" in tile_map.sprite_lists:
                    self.collision_list = tile_map.sprite_lists["colision"]

                if "backgr" in tile_map.sprite_lists:
                    self.backgr_list = tile_map.sprite_lists["backgr"]
                elif len(self.wall_list) > 0:
                    self.collision_list = self.wall_list

                return True

            except Exception:
                return False
        else:
            return False

    def _create_simple_walls(self):
        wall_path = os.path.join(
            self.project_path, "textures", "sprites", "blocks", "block.png"
        )

        if os.path.exists(wall_path):
            wall_texture = arcade.load_texture(wall_path)
        else:
            wall_texture = None

        wall_size = 70 * self.global_scale
        wall_count_x = int(self.screen_width / wall_size) + 2
        wall_count_y = int(self.screen_height / wall_size) + 2

        for x in range(wall_count_x):
            for y in range(wall_count_y):
                if x == 0 or x == wall_count_x - 1 or y == 0 or y == wall_count_y - 1:
                    if wall_texture:
                        wall = arcade.Sprite(wall_path, scale=self.global_scale)
                    else:
                        wall = arcade.SpriteSolidColor(
                            int(wall_size), int(wall_size), arcade.color.GRAY
                        )

                    wall.center_x = x * wall_size
                    wall.center_y = y * wall_size
                    self.wall_list.append(wall)
                    self.collision_list.append(wall)

    def _calculate_map_bounds(self):
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
            self.map_left = 0
            self.map_right = self.screen_width
            self.map_bottom = 0
            self.map_top = self.screen_height

    def _center_camera(self):
        if self.backgr_list or self.wall_list:
            center_x = (self.map_left + self.map_right) / 2
            center_y = (self.map_bottom + self.map_top) / 2

            self.camera.position = (center_x, center_y)
        else:
            self.camera.position = (self.screen_width / 2, self.screen_height / 2)

    def _create_tanks(self):
        tank_red_path = os.path.join(
            self.project_path, "textures", "sprites", "tanks", "tank_red.png"
        )
        tank_blue_path = os.path.join(
            self.project_path, "textures", "sprites", "tanks", "tank_blue.png"
        )

        map_width = self.map_right - self.map_left
        tank_scale = max(0.3, min(0.8, map_width / 2000))

        if self.select_map == "map_1.tmx":
            tank_scale *= 1.2

        if os.path.exists(tank_red_path):
            self.tank_wasd = arcade.Sprite(tank_red_path, scale=tank_scale)
        else:
            tank_size = int(60 * tank_scale)
            self.tank_wasd = arcade.SpriteSolidColor(
                tank_size, tank_size, arcade.color.RED
            )

        if os.path.exists(tank_blue_path):
            self.tank_arrows = arcade.Sprite(tank_blue_path, scale=tank_scale)
        else:
            tank_size = int(60 * tank_scale)
            self.tank_arrows = arcade.SpriteSolidColor(
                tank_size, tank_size, arcade.color.BLUE
            )

        self._position_tanks()

        self.player_list.append(self.tank_wasd)
        self.player_list.append(self.tank_arrows)

    def _position_tanks(self):
        if self.backgr_list or self.wall_list:
            map_center_x = (self.map_left + self.map_right) / 2
            map_width = self.map_right - self.map_left

            self.tank_wasd.center_x = self.map_left + map_width * 0.25
            self.tank_wasd.center_y = (self.map_bottom + self.map_top) / 2
            self.tank_wasd.angle = 0

            self.tank_arrows.center_x = self.map_left + map_width * 0.75
            self.tank_arrows.center_y = (self.map_bottom + self.map_top) / 2
            self.tank_arrows.angle = 0
        else:
            self.tank_wasd.center_x = self.screen_width * 0.25
            self.tank_wasd.center_y = self.screen_height / 2

            self.tank_arrows.center_x = self.screen_width * 0.75
            self.tank_arrows.center_y = self.screen_height / 2

    def _fire_bullet(self, tank, speed=None):
        if speed is None:
            speed = BULLET_SPEED * self.global_scale

        bullet_path = os.path.join(
            self.project_path,
            "textures",
            "sprites",
            "tanks",
            "bulletDark2_outline.png",
        )

        if os.path.exists(bullet_path):
            bullet = arcade.Sprite(bullet_path, scale=2 * self.global_scale)
        else:
            bullet_size = int(20 * self.global_scale)
            bullet = arcade.SpriteSolidColor(
                bullet_size, bullet_size, arcade.color.YELLOW
            )

        offset = tank.height * 0.7

        if tank.angle == 180:
            bullet.center_x = tank.center_x
            bullet.center_y = tank.center_y + offset
            bullet.change_x = 0
            bullet.change_y = speed
            bullet.angle = 180
        elif tank.angle == 360 or tank.angle == 0:
            bullet.center_x = tank.center_x
            bullet.center_y = tank.center_y - offset
            bullet.change_x = 0
            bullet.change_y = -speed
            bullet.angle = 0
        elif tank.angle == 90:
            bullet.center_x = tank.center_x - offset
            bullet.center_y = tank.center_y
            bullet.change_x = -speed
            bullet.change_y = 0
            bullet.angle = 90
        elif tank.angle == 270:
            bullet.center_x = tank.center_x + offset
            bullet.center_y = tank.center_y
            bullet.change_x = speed
            bullet.change_y = 0
            bullet.angle = 270

        self.bullet_list.append(bullet)

        if self.shoot_sound:
            self.shoot_sound.play(volume=0.5)

    def _keep_tank_in_bounds(self, tank):
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

        with self.camera.activate():
            self.backgr_list.draw()
            self.wall_list.draw()
            self.player_list.draw()
            self.bullet_list.draw()

            for emitter in self.emitters:
                emitter.draw()

        draw_text(
            f"КРАСНЫЙ: {self.score_wasd}",
            20,
            self.screen_height - 50,
            color.RED,
            24,
            bold=True,
        )
        draw_text(
            f"СИНИЙ: {self.score_arrows}",
            20,
            self.screen_height - 80,
            color.BLUE,
            24,
            bold=True,
        )
        draw_text(
            f"РАУНД: {self.current_round}/{self.max_rounds}",
            self.screen_width - 200,
            self.screen_height - 50,
            color.WHITE,
            24,
            bold=True,
        )
        draw_text(
            f"Здоровье КРАСНЫЙ: {self.health_red}",
            self.screen_width - 400,
            50,
            color.RED,
            24,
            bold=True,
        )
        draw_text(
            f"Здоровье СИНИЙ: {self.health_blue}",
            self.screen_width - 400,
            20,
            color.BLUE,
            24,
            bold=True,
        )

        if not self.round_active and self.round_winner:
            if (
                self.current_round <= self.max_rounds
                and self.current_round < self.max_rounds
            ):
                if self.round_winner == "wasd":
                    winner_color = color.RED
                    winner_text = "КРАСНЫЙ"
                else:
                    winner_color = color.BLUE
                    winner_text = "СИНИЙ"

                draw_text(
                    f"{winner_text} ВЫИГРАЛ РАУНД!",
                    self.screen_width / 2,
                    self.screen_height / 2 + 50,
                    winner_color,
                    40,
                    anchor_x="center",
                    bold=True,
                )
                draw_text(
                    f"Следующий раунд через {max(0, int(self.round_delay - self.round_timer + 1))}...",
                    self.screen_width / 2,
                    self.screen_height / 2 - 20,
                    color.WHITE,
                    30,
                    anchor_x="center",
                )

        if self.current_round > self.max_rounds:
            if self.score_wasd > self.score_arrows:
                winner_text = "КРАСНЫЙ ПОБЕДИЛ В ИГРЕ!"
                winner_color = color.RED
            elif self.score_arrows > self.score_wasd:
                winner_text = "СИНИЙ ПОБЕДИЛ В ИГРЕ!"
                winner_color = color.BLUE
            else:
                winner_text = "НИЧЬЯ!"
                winner_color = color.WHITE

            draw_text(
                winner_text,
                self.screen_width / 2,
                self.screen_height / 2,
                winner_color,
                50,
                anchor_x="center",
                bold=True,
            )
            draw_text(
                "Нажмите ESC для выхода в меню",
                self.screen_width / 2,
                self.screen_height / 2 - 60,
                color.WHITE,
                20,
                anchor_x="center",
            )

    def on_key_press(self, key, modifiers):
        if self.current_round > self.max_rounds:
            if key == arcade.key.ESCAPE:
                set_background_color((10, 18, 35))
                self.window.show_view(self.menu)

        if not self.round_active:
            return

        if (
            self.tank_wasd not in self.player_list
            or self.tank_arrows not in self.player_list
        ):
            return

        scaled_speed = TANK_SPEED * self.global_scale

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

        if key == arcade.key.SPACE:
            self._fire_bullet(self.tank_wasd)

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

        if key == arcade.key.ENTER:
            self._fire_bullet(self.tank_arrows)

        if key == arcade.key.ESCAPE:
            pause_view = Pause(game_view=self, menu=self.menu)
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
        if self.current_round > self.max_rounds:
            return

        if self.round_active:
            if self.physics_engine_wasd and self.tank_wasd in self.player_list:
                self.physics_engine_wasd.update()

            if self.physics_engine_arrows and self.tank_arrows in self.player_list:
                self.physics_engine_arrows.update()

            if self.tank_wasd in self.player_list:
                self._keep_tank_in_bounds(self.tank_wasd)

            if self.tank_arrows in self.player_list:
                self._keep_tank_in_bounds(self.tank_arrows)

            self.bullet_list.update()

            for emitter in self.emitters:
                emitter.update()

            self.emitters = [e for e in self.emitters if not e.can_reap()]

            bullets_to_remove = []

            for bullet in self.bullet_list:
                hit_list = arcade.check_for_collision_with_list(
                    bullet, self.player_list
                )

                for hit in hit_list:
                    if self.explosion_sound:
                        self.explosion_sound.play(volume=0.7)

                    self.emitters.append(make_explosion(bullet.center_x, bullet.center_y, 80))
                    self.emitters.append(make_smoke_puff(bullet.center_x, bullet.center_y))

                    if hit == self.tank_wasd and int(self.health_red) == 1:
                        self.round_winner = "arrows"
                        self.health_red = 0
                        self.score_arrows += 1
                        self.flag_deacrivate = True
                    elif hit == self.tank_arrows and int(self.health_blue) == 1:
                        self.round_winner = "wasd"
                        self.health_blue = 0
                        self.score_wasd += 1
                        self.flag_deacrivate = True

                    if hit == self.tank_wasd and int(self.health_red) > 1:
                        self.health_red -= 1
                        bullets_to_remove.append(bullet)

                    elif hit == self.tank_arrows and int(self.health_blue) > 1:
                        self.health_blue -= 1
                        bullets_to_remove.append(bullet)

                    if self.flag_deacrivate:
                        hit.remove_from_sprite_lists()
                        bullets_to_remove.append(bullet)

                        self.round_active = False
                        self.round_timer = 0
                        break

                if self.collision_list:
                    wall_hits = arcade.check_for_collision_with_list(
                        bullet, self.collision_list
                    )
                    if wall_hits:
                        if self.explosion_sound:
                            self.explosion_sound.play(volume=0.5)

                        self.emitters.append(make_explosion(bullet.center_x, bullet.center_y, 60))
                        self.emitters.append(make_smoke_puff(bullet.center_x, bullet.center_y))
                        bullets_to_remove.append(bullet)

                if self.backgr_list or self.wall_list:
                    if (
                        bullet.left > self.map_right + 100
                        or bullet.right < self.map_left - 100
                        or bullet.bottom > self.map_top + 100
                        or bullet.top < self.map_bottom - 100
                    ):
                        bullets_to_remove.append(bullet)

            for bullet in bullets_to_remove:
                if bullet in self.bullet_list:
                    bullet.remove_from_sprite_lists()

        else:
            self.round_timer += delta_time

            if self.current_round >= self.max_rounds:
                if not hasattr(self, "game_ended") or not self.game_ended:
                    self.game_ended = True
                    self.current_round = self.max_rounds + 1
            else:
                if self.round_timer >= self.round_delay:
                    self.current_round += 1
                    self._reset_round()