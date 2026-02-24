import arcade

class Button:
    def __init__(self, text, x, y, width=100, height=150, 
                 color=(0, 0, 0), hover_color=(100, 100, 100),
                 click_color=(150, 150, 150), color2=(255, 255, 255),
                 callback=None):  # Добавляем функцию обратного вызова
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color
        self.click_color = click_color
        self.color2 = color2
        self.is_hovered = False
        self.is_pressed = False
        self.callback = callback  # Функция, которая выполнится при клике
    
    def check_hover(self, mouse_x, mouse_y):
        left = self.x - self.width // 2
        right = self.x + self.width // 2
        bottom = self.y - self.height // 2
        top = self.y + self.height // 2
        self.is_hovered = left <= mouse_x <= right and bottom <= mouse_y <= top
    
    def on_mouse_press(self, mouse_x, mouse_y):
        if self.is_hovered:  # Используем is_hovered вместо повторной проверки
            self.is_pressed = True
            return True
        return False
    
    def on_mouse_release(self):
        if self.is_pressed and self.is_hovered and self.callback:
            self.callback()  # Вызываем функцию при успешном клике
        was_pressed = self.is_pressed
        self.is_pressed = False
        return was_pressed
    
    def draw(self):
        # Выбираем цвет: нажата > наведена > обычная
        if self.is_pressed:
            current_color = self.click_color
        elif self.is_hovered:
            current_color = self.hover_color
        else:
            current_color = self.color
        
        # Рисуем прямоугольник
        arcade.draw_rect_filled(
            arcade.rect.XYWH(self.x, self.y, self.width, self.height), 
            current_color
        )
        
        # Рисуем текст (с адаптивным размером шрифта)
        font_size = min(17, self.width // 6)  # Адаптивный размер шрифта
        text_obj = arcade.Text(
            self.text,
            self.x,
            self.y,
            self.color2,
            font_size,
            anchor_x="center",
            anchor_y="center",
            width=self.width - 10,
            align="center",
            multiline=True
        )
        text_obj.draw()