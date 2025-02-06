import pygame
import math

# 1100 363
class Xonas(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.hp = 2500
        self.max_hp = 2500
        self.damage = 15
        self.is_alive = True

        # Позиция
        self.x = x
        self.y = y

        # Начальное изображение + прямоугольник
        self.image = pygame.image.load("Data/Xonas/0.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))

        # Параметры движения (если нужно)
        self.speed = 2

        # Загружаем кадры анимации ожидания (idle)
        self.frames = []
        for i in range(15):
            frame = pygame.image.load(f"Data/Xonas/{i}.png").convert_alpha()
            self.frames.append(frame)

        self.frame_index = 0
        self.animation_speed = 0.4  # чем выше, тем быстрее "листает" кадры

        # Счётчик перезарядки атаки
        self.attack_cooldown = 60  # Пример: 1 сек при 60 FPS
        self.attack_timer = 0

        self.vortex_cooldown = 300
        self.vortex_timer = 0
        self.vortex_damage = 30

    def update(self, player, vortex_group):
        """
        Логика босса:
        1) Идём к игроку
        2) Пытаемся выполнить ближнюю атаку
        3) Пытаемся применить "особую атаку" (создать вихрь)
        4) Крутим общую анимацию
        """
        if not self.is_alive:
            return

        # 1) Движение к игроку (если нужно, чтобы босс ходил)
        self.move_towards_player(player)

        # 2) Ближняя атака, если игрок близко
        self.melee_attack(player)

        # 3) Особая атака – вызов вихря
        self.special_attack(player, vortex_group)

        # 4) Анимация босса
        self.animate()

    def move_towards_player(self, player):
        """Простая логика преследования игрока."""
        px, py = player.rect.center
        bx, by = self.rect.center
        dx = px - bx
        dy = py - by

        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

    def melee_attack(self, player):
        """Проверяем кулдаун. Если игрок рядом, наносим урон сразу (через хитбокс сбоку)."""
        # Отсчитываем кулдаун
        if self.attack_timer > 0:
            self.attack_timer -= 1
            return

        # Проверим расстояние
        distance_x = abs(self.rect.centerx - player.rect.centerx)
        distance_y = abs(self.rect.centery - player.rect.centery)

        # Если достаточно близко (по сути, в квадрате 100x100)
        if distance_x < 100 and distance_y < 100:
            # Создаём простой хитбокс
            boss_attack_rect = pygame.Rect(self.rect.right, self.rect.y, 50, self.rect.height)
            if boss_attack_rect.colliderect(player.rect):
                old_hp = player.hp
                player.hp -= self.damage
                print(f"Xonas ударил игрока на {self.damage}. Было {old_hp}, осталось {player.hp}")

            # Ставим кулдаун
            self.attack_timer = self.attack_cooldown

    def special_attack(self, player, vortex_group):
        """Особый спелл: раз в vortex_cooldown кадров Xonas призывает вихрь на месте игрока."""
        if self.vortex_timer > 0:
            self.vortex_timer -= 1
            return

        # Если таймер 0, создаём вихрь
        # Вихрь появится ровно там, где сейчас игрок
        vx, vy = player.rect.center
        vortex = Vortex(vx, vy, self.vortex_damage)
        vortex_group.add(vortex)

        print("Xonas вызвал вихрь!")

        # Ставим кулдаун на особую атаку
        self.vortex_timer = self.vortex_cooldown

    def animate(self):
        """Проигрываем одну и ту же анимацию."""
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

        # Чтобы не скакал по карте, восстанавливаем центр
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def take_damage(self, damage):
        """Получение урона от игрока."""
        if not self.is_alive:
            return
        self.hp -= damage
        if self.hp <= 0:
            self.is_alive = False
            print("Xonas повержен!")

    def draw(self, screen, camera):
        """Отрисовка босса."""
        if self.is_alive:
            screen.blit(self.image, camera.apply(self.rect))

    def draw_hp_bar(self, screen, camera):
        """Рисует полоску здоровья босса с его именем над ней,
        а внутри полоски отображает текущее и максимальное HP."""
        # Получаем экранный прямоугольник босса с учётом смещения камеры
        boss_screen_rect = camera.apply(self.rect)

        # Параметры полоски здоровья
        bar_width = 300
        bar_height = 20

        screen_width, screen_height = screen.get_size()

        x = (screen_width - bar_width) // 2
        y = screen_height - bar_height - 50

        # Рисуем рамку полоски здоровья (белой линией)
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)

        # Вычисляем, какая часть полоски будет заполнена
        hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 0
        fill_width = int(bar_width * hp_ratio)

        pygame.draw.rect(screen, (255, 0, 0), (x, y, fill_width, bar_height))

        font = pygame.font.Font(None, 28)
        name_surf = font.render("Xonas", True, (255, 255, 255))
        name_rect = name_surf.get_rect(center=(x + bar_width // 2, y - 10))
        screen.blit(name_surf, name_rect)

        # Отрисовываем текст с числовыми значениями внутри полоски
        hp_text = font.render(f"{self.hp}/{self.max_hp}", True, (255, 255, 255))
        hp_text_rect = hp_text.get_rect(center=(x + bar_width // 2, y + bar_height // 2))
        screen.blit(hp_text, hp_text_rect)


class Vortex(pygame.sprite.Sprite):
    def __init__(self, x, y, damage):
        super().__init__()
        # Загружаем кадры анимации вихря (пр.: 5 кадров)
        self.frames = []
        for i in ["tile000.png", "tile001.png", "tile002.png", "tile003.png", "tile004.png", "tile005.png",
                  "tile006.png", "tile007.png", "tile008.png", "tile009.png", "tile010.png", "tile011.png",
                  "tile012.png", "tile013.png", "tile014.png", "tile015.png", "tile016.png", "tile017.png",
                  "tile018.png", "tile019.png"]:
            frame = pygame.image.load(f"Data/vortex/{i}").convert_alpha()
            self.frames.append(frame)

        self.frame_index = 0
        self.animation_speed = 0.2

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))

        self.damage = damage
        self.done = False  # когда анимация закончится, пометим на удаление

    def update(self, player):
        """Проигрываем анимацию. Когда заканчиваем, проверяем, не стоит ли игрок в зоне."""
        if self.done:
            return  # уже «отстрелялся»

        # Анимация
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            # Анимация закончилась – проверяем позицию игрока
            if self.rect.colliderect(player.rect):
                old_hp = player.hp
                player.hp -= self.damage
                print(f"Вихрь нанёс {self.damage} урона! Было {old_hp}, осталось {player.hp}")
            # Помечаем вихрь как «отработавший»
            self.done = True
            return

        # Обновим текущий кадр
        self.image = self.frames[int(self.frame_index)]
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center
