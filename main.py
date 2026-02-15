import arcade
import os
from windows.menu.start import MenuView



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TANKS_DIR = os.path.join(BASE_DIR, "textures", "sprites", "tanks")
arcade.resources.add_resource_handle("tanks", TANKS_DIR)

from windows.menu.start import MenuView

def main():
    window = arcade.Window(
        title="Танчики 2D",
        fullscreen=True,
        resizable=False,
        antialiasing=True,
        center_window=True
    )
    window.show_view(MenuView())
    arcade.run()

if __name__ == "__main__":
    main()