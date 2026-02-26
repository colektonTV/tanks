import arcade
from windows.menu.menu_window import WindowMenu
from textures.animation.anim_tank import FloatingTank



class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        base_count = 12
        extra = max(0, int((self.window.width - 1920) / 400))
        self.floating_tanks = [FloatingTank(self.window) for _ in range(base_count + extra)]

        self.time = 0
        self.blink_timer = 0
        self.show_text = True

    def on_show_view(self):
        arcade.set_background_color((10, 18, 35))

    def on_update(self, delta_time):
        self.time += delta_time
        self.blink_timer += delta_time

        if self.blink_timer >= 0.7:
            self.show_text = not self.show_text
            self.blink_timer = 0

        for tank in self.floating_tanks:
            tank.update(delta_time)

    def on_draw(self):
        self.clear()

        w = self.window.width
        h = self.window.height

        scale = min(w / 1920, h / 1080)

        for tank in self.floating_tanks:
            tank.draw()

        arcade.draw_rect_filled(
            arcade.rect.XYWH(w/2, h/2, w, h),
            (0, 0, 0, 140)
        )

        arcade.draw_text(
            "ТАНЧИКИ",
            w / 2,
            h - 150 * scale,
            arcade.color.WHITE,
            font_size=88 * scale,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial Black"
        )

        arcade.draw_text(
            "2D БИТВА",
            w / 2,
            h - 235 * scale,
            arcade.color.LIGHT_BLUE,
            font_size=36 * scale,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial"
        )

        if self.show_text:
            arcade.draw_text(
                "НАЖМИ ПРОБЕЛ ЧТОБЫ НАЧАТЬ",
                w / 2,
                h // 2 - 30 * scale,
                arcade.color.WHITE,
                font_size=26 * scale,
                anchor_x="center",
                anchor_y="center",
                font_name="Arial"
            )

        arcade.draw_text(
            "WASD / стрелки — движение    ЛКМ — выстрел",
            w / 2,
            70 * scale,
            arcade.color.LIGHT_GRAY,
            font_size=17 * scale,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial"
        )

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            menu_view = WindowMenu()
            menu_view.setup()
            self.window.show_view(menu_view)
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()

