import sys
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from time import sleep
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:

    def __init__(self):
        pygame.init()  # Инициализирует игру и создает игровые ресурсы
        self.settings = Settings()
        self.fullscreen = False

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))

        pygame.display.set_caption('Alien Invasion')
        self.stats = GameStats(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.shoots = False
        self._create_fleet()
        self.play_button = Button(self, "Play")
        self.sb = Scoreboard(self)

    def run_game(self):
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:  # відключаємо поле на реакцію миші під час гри
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.aliens.empty()
            self.bullets.empty()
            self._create_fleet()
            self.ship.center_ship()
            pygame.mouse.set_visible(False)
            self.settings.initialize_dynamic_settings()

    def _check_keydown_events(self, event):  # Отслеживание событий клавиатуры и мыши
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.shoots = True
        elif event.key == pygame.K_f:
            if not self.fullscreen:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                self.settings.screen_width = self.screen.get_rect().width
                self.settings.screen_height = self.screen.get_rect().height
                self.ship.screen = self.screen
                self.ship.screen_rect = self.screen.get_rect()
                # self._create_fleet()
                self.fullscreen = True
            else:
                self.settings = Settings()
                self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
                self.ship.screen_rect = self.screen.get_rect()
                self.ship.screen = self.screen
                self.fullscreen = False

    def _check_keyup_events(self, event):  # Отслеживание событий клавиатуры и мыши.
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False
        elif event.key == pygame.K_SPACE:
            self.shoots = False

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        self._check_aliens_bottom()

    def _ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)  # включаємо мишку при неактивній грі
        self.aliens.empty()
        self.bullets.empty()
        self._create_fleet()
        self.ship.center_ship()
        sleep(0.5)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width
        numbers_aliens_x = int(available_space_x // (1.4 * alien_width))

        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = int(available_space_y // (1.2 * alien_height))

        for row_number in range(number_rows):
            for alien_number in range(numbers_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = (0.2 * alien_width) + 1.2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = (0.2 * alien.rect.height) + 1.2 * alien.rect.height * row_number  # розміщення аліен по вертикалі
        self.aliens.add(alien)

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():  # не можна видаляти та змінювати основну групу спрайтів в циклі, тому копія
            if bullet.rect.bottom <= 0:  # при виході нижньої частини буллет за межі зеро-лінії координат - видалення
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

    def _update_screen(self):
        """Обновляет изображения на экране и отображает новый экран."""
        self.screen.fill(self.settings.bg_color)  # При каждом проходе цикла перерисовывается экран
        self.ship.blitme()
        if self.shoots:
            self._fire_bullet()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)  # метод класа пайгейм,виводить все на даний екран
        self.sb.show_score()
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()  # Отображение последнего прорисованного экрана


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
