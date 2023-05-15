import pygame

class Ship():
    """Инициализирует корабль и задает его начальную позицию."""
    def __init__(self, ai_game):
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        self.image = pygame.image.load('images/ship.bmp') # Загружает изображение корабля и ...
        self.rect = self.image.get_rect()                 # ... получает прямоугольник
        self.rect.midbottom = self.screen_rect.midbottom  # Каждый новый корабль появляется у нижнего края экрана.

        self.x = float(self.rect.x) # Сохранение вещественной координаты центра корабля.
        self.y = float(self.rect.y)

        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
    def update(self):
        ''' обмеження виходу прямокутника корабля за визначені розміри екрану'''
        if self.moving_right:
            if self.moving_right and self.rect.right < self.screen_rect.right:
                self.x += self.settings.ship_speed
        elif self.moving_left:
            if self.moving_left and self.rect.left > 0:
                self.x -= self.settings.ship_speed
        elif self.moving_up:
            if self.moving_up and self.rect.top > 0:
                self.y -= self.settings.ship_speed
        elif self.moving_down:
            if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
                self.y += self.settings.ship_speed

        self.rect.x = self.x # Повернення цілочисельної координати корабля
        self.rect.y = self.y

    def blitme(self):
        """Рисует корабль в текущей позиции."""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)