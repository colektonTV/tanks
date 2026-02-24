import arcade


class Settings(arcade.View):
    def __init__(self):
        super().__init__()
    
    def setup(self):
        pass
        # Если хочешь создать кнопку, для этого есть отдельный класс который находиться по пути window/buttons/button.py
        # Почитай посмотри что он делает. Пример как его использовать можно найти в файле menu_window.py.
        # Не забудь добавлять настройки в json файл, который находится по пути data/level.json
        # Что бы запустить игру, тебе надо находиться в корневой папке и написать команду в терминал python main.py