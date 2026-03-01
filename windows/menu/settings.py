import arcade
import json
from arcade.gui import (
    UIManager,
    UIDropdown,
    UISlider,
    UIFlatButton,
    UILabel,
    UIBoxLayout,
    UIAnchorLayout,
)
from textures.animation.anim_tank import FloatingTank


class Settings(arcade.View):
    def __init__(self, menu_view=None):
        super().__init__()
        base_count = 12
        self.menu_view = menu_view
        extra = max(0, int((self.window.width - 1920) / 400))
        self.floating_tanks = [FloatingTank(self.window) for _ in range(base_count + extra)]
        self.selected_map = "map_1.tmx"
        self.rounds = 3
        self.health_multiplier = 1

        self.time = 0.0

    def setup(self):
        arcade.set_background_color((10, 18, 35))

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()

        self.box_layout = UIBoxLayout(
            vertical=True,
            space_between=28
        )

        self.setup_widgets()

        self.anchor_layout.add(
            child=self.box_layout,
            anchor_x="center_x",
            anchor_y="center_y",
        )
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        title_label = UILabel(
            text="Настройки игры",
            font_size=24,
            text_color=arcade.color.LIGHT_GRAY,
        )
        self.box_layout.add(title_label.with_padding(bottom=20))

        map_label = UILabel(
            text="Карта:",
            font_size=18,
            text_color=arcade.color.WHITE,
        )
        self.box_layout.add(map_label)

        dropdown = UIDropdown(
            options=["Первая карта", "Вторая карта"],
            width=280,
            height=44
        )
        dropdown.text = self.selected_map

        @dropdown.event("on_change")
        def on_map_change(event):
            self.selected_map = event.new_value

        self.box_layout.add(dropdown.with_padding(bottom=20))

        self.rounds_label = UILabel(
            text=f"Раундов: {self.rounds}",
            font_size=18,
            text_color=arcade.color.WHITE,
        )
        self.box_layout.add(self.rounds_label)

        rounds_slider = UISlider(
            value=self.rounds,
            min_value=1,
            max_value=15,
            width=300,
            height=48
        )

        @rounds_slider.event("on_change")
        def on_rounds_change(event):
            self.rounds = int(round(event.new_value))
            self.rounds_label.text = f"Раундов: {self.rounds}"

        self.box_layout.add(rounds_slider.with_padding(bottom=25))

        self.health_label = UILabel(
            text=f"Здоровье танка: ×{self.health_multiplier:.1f}",
            font_size=18,
            text_color=arcade.color.WHITE,
        )
        self.box_layout.add(self.health_label)

        health_slider = UISlider(
            value=self.health_multiplier,
            min_value=1,
            max_value=5,
            width=300,
            height=48
        )

        @health_slider.event("on_change")
        def on_health_change(event):
            self.health_multiplier = int(round(event.new_value))
            self.health_label.text = f"Здоровье танка: ×{self.health_multiplier:.1f}"

        self.box_layout.add(health_slider.with_padding(bottom=35))

        buttons_layout = UIBoxLayout(
            vertical=False,
            space_between=40,
        )

        save_button = UIFlatButton(
            text="Сохранить",
            width=220,
            height=55,
        )

        @save_button.event("on_click")
        def on_save(_):
            self.save_settings()

        back_button = UIFlatButton(
            text="Назад",
            width=220,
            height=55,
        )

        @back_button.event("on_click")
        def on_back(_):
            self.go_back_to_menu()
        
        buttons_layout.add(save_button)
        buttons_layout.add(back_button)

        self.box_layout.add(buttons_layout)
    def go_back_to_menu(self):
        if self.menu_view:
            self.window.show_view(self.menu_view)
        else:
            possible_keys = ["WindowMenu", "windowMenu", "menu"]
            if hasattr(self.window, 'views'):
                for key in possible_keys:
                    if key in self.window.views:
                        self.window.show_view(self.window.views[key])
                        return

    def save_settings(self):
        self.map_selec = ''
        if self.selected_map == "Первая карта":
            self.map_selec = "map_1.tmx"
        else:
            self.map_selec = "map_2.tmx"
        data = {
            "map": self.map_selec,
            "rounds": self.rounds,
            "health_multiplier": self.health_multiplier,
        }

        with open("data/level.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def on_update(self, delta_time: float):
        self.time += delta_time
        for tank in self.floating_tanks:
            tank.update(delta_time)

    def on_draw(self):
        self.clear()
        for tank in self.floating_tanks:
            tank.draw()

        arcade.draw_text(
            "Настройки",
            self.window.width // 2,
            self.window.height - 70,
            arcade.color.WHITE,
            font_size=48,
            anchor_x="center",
            font_name="Kenney Future"
        )

        self.manager.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.go_back_to_menu()