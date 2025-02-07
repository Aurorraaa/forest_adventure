import pygame
import sys


class Trade_menu():
    def __init__(self, player, merchant):
        self.player = player
        self.merchant = merchant

        self.font = pygame.font.Font(None, 24)
        self.running = False

        self.player_list_x = 50
        self.player_list_y = 100
        self.merchant_list_x = 400
        self.merchant_list_y = 100

        self.item_height = 30

    def open(self, screen, clock):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mx, my = event.pos
                        # Проверяем клик по предмету игрока
                        clicked_item = self.get_clicked_item(self.player.inventory, mx, my,
                                                             self.player_list_x, self.player_list_y)
                        if clicked_item is not None:
                            self.player.sell_item_to_merchant(clicked_item, self.merchant)
                            continue
                        clicked_item = self.get_clicked_item(self.merchant.inventory, mx, my,
                                                             self.merchant_list_x, self.merchant_list_y)
                        if clicked_item is not None:
                            self.player.buy_item_from_merchant(clicked_item, self.merchant)
                            continue

            screen.fill((30, 30, 30))
            self.draw_header(screen)
            self.draw_inventory_list(screen, self.player.inventory,
                                     x=self.player_list_x, y=self.player_list_y,
                                     title=f"Игрок ({self.player.coins})")
            self.draw_inventory_list(screen, self.merchant.inventory,
                                     x=self.merchant_list_x, y=self.merchant_list_y,
                                     title=f"{self.merchant.name}")

            pygame.display.flip()
            clock.tick(60)
        return

    def draw_header(self, screen):
        title_surf = self.font.render("Кузнец Владимир", True, (255, 255, 255))
        screen.blit(title_surf, (10, 10))

    def draw_inventory_list(self, screen, inventory, x, y, title=""):
        title_surf = self.font.render(title, True, (255, 255, 255))
        screen.blit(title_surf, (x, y - 30))

        items = inventory.get_all_items()
        y_offset = y
        for i, item in enumerate(items):
            text = f"{item['name']} ({item['price']})"
            surf = self.font.render(text, True, (200, 200, 200))
            screen.blit(surf, (x, y_offset))
            y_offset += self.item_height

    def get_clicked_item(self, inventory, mx, my, list_x, list_y):
        items = inventory.get_all_items()
        for i, item in enumerate(items):
            # Каждая строка занимает self.item_height по вертикали
            item_rect = pygame.Rect(list_x, list_y + i * self.item_height,
                                    200, self.item_height)
            if item_rect.collidepoint(mx, my):
                return item
        return None
