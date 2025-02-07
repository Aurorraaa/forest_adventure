import sys
import pygame

from crafting import CraftingBookMenu


class Inventory:
    dragging_item = None
    dragging_from = None
    drag_offset = (0, 0)
    drag_pos = (0, 0)

    def __init__(self):
        self.items = []
        self.inventory_bg = pygame.image.load("Data/invent.png").convert_alpha()
        self.bg_rect = self.inventory_bg.get_rect()
        self.slots = []
        self.slot_positions = [(16, 18), (68, 18), (118, 18), (168, 18), (220, 18), (270, 18), (320, 18), (370, 18),
                               (16, 68), (68, 68), (118, 68), (168, 68), (220, 68), (270, 68), (320, 68), (370, 68),
                               (16, 118), (68, 118), (118, 118), (168, 118), (220, 118), (270, 118), (320, 118),
                               (370, 118),
                               (16, 168), (68, 168), (118, 168), (168, 168), (220, 168), (270, 168), (320, 168),
                               (370, 168),
                               (16, 218), (68, 218), (118, 218), (168, 218), (220, 218), (270, 218), (320, 218),
                               (370, 218)
                               ]
        self.slot_width, self.slot_height = 48, 48
        for pos in self.slot_positions:
            self.x, self.y = pos
            r = pygame.Rect(self.x, self.y, self.slot_width, self.slot_height)
            self.slots.append({"rect": r, "item": None})

    def add_item(self, item_id, item_name, icon_path, price=0, description="", damage=0, max_stack=1, quantity=1):
        try:
            self.icon_surf = pygame.image.load(icon_path).convert_alpha()
        except pygame.error as e:
            print(f"Ошибка загрузки иконки: {icon_path}. {e}")
            return

        for slot in self.slots:
            if slot["item"] is not None and slot["item"]["id"] == item_id:
                current_stack = slot["item"]["current_stack"]
                free_space = slot["item"]["max_stack"] - current_stack
                if free_space > 0:
                    to_add = min(quantity, free_space)
                    slot["item"]["current_stack"] += to_add
                    quantity -= to_add
                    if quantity <= 0:
                        return

        while quantity > 0:
            to_add = min(quantity, max_stack)
            new_item = {
                "id" : item_id,
                "name": item_name,
                "icon": self.icon_surf,
                "price": price,
                "description": description,
                "damage": damage,
                "max_stack": max_stack,
                "current_stack": to_add
            }
            for slot in self.slots:
                if slot["item"] is None:
                    slot["item"] = new_item
                    quantity -= to_add
                    break
            else:
                print("Нет свободных слотов!")
                return

    def remove_item(self, item_id, quantity=1):
        for slot in self.slots:
            if slot["item"] is not None and slot["item"]["id"] == item_id:
                if slot["item"]["current_stack"] > quantity:
                    slot["item"]["current_stack"] -= quantity
                    return
                else:
                    quantity -= slot["item"]["current_stack"]
                    slot["item"] = None
                    if quantity <= 0:
                        return

    def show_inventory(self, screen, clock):
        font = pygame.font.Font(None, 36)
        background_surf = screen.copy()
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((50, 50, 50))

        self.bg_rect.center = (screen.get_width() // 2, screen.get_height() // 2)

        runin = True
        craft_button_rect = pygame.Rect(self.bg_rect.right + 20, self.bg_rect.top + 20, 100, 40)

        while runin:
            screen.blit(background_surf, (0, 0))
            screen.blit(overlay, (0, 0))
            screen.blit(self.inventory_bg, self.bg_rect)
            pygame.draw.rect(screen, (100, 100, 200), craft_button_rect)
            craft_text = font.render("Крафт", True, (255, 255, 255))
            screen.blit(craft_text, (craft_button_rect.centerx - craft_text.get_width() // 2,
                                     craft_button_rect.centery - craft_text.get_height() // 2))
            self.draw_slots(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_e, pygame.K_ESCAPE]:
                        runin = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if craft_button_rect.collidepoint(event.pos):
                            runin = False
                            craft_menu = CraftingBookMenu(inventory=self, json_path="objects (2).json",
                                                          book_image_path="Data/book.png")
                            craft_menu.open(screen, clock)
                        self.handle_mouse_down(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # ЛКМ
                        self.handle_mouse_up(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)
                self.process_event(event, screen)

            mouse_pos = pygame.mouse.get_pos()
            self.show_tooltip(screen, mouse_pos)

            if Inventory.dragging_item is not None:
                self.icon = Inventory.dragging_item["icon"]
                self.draw_x = Inventory.drag_pos[0] - Inventory.drag_offset[0]
                self.draw_y = Inventory.drag_pos[1] - Inventory.drag_offset[1]
                screen.blit(self.icon, (self.draw_x, self.draw_y))

            pygame.display.flip()
            clock.tick(60)
        return

    def draw_slots(self, screen):
        for slot in self.slots:
            abs_x = self.bg_rect.x + slot["rect"].x
            abs_y = self.bg_rect.y + slot["rect"].y
            rect_abs = pygame.Rect(abs_x, abs_y, slot["rect"].width, slot["rect"].height)
            pygame.draw.rect(screen, (200, 200, 200), rect_abs, 2)

            if slot["item"] is not None:
                if slot["item"] != Inventory.dragging_item:
                    icon = slot["item"]["icon"]
                    icon_rect = icon.get_rect(center=rect_abs.center)
                    screen.blit(icon, icon_rect)

                if slot["item"]["current_stack"] > 1:
                    font = pygame.font.Font(None, 18)
                    text_surface = font.render(str(slot["item"]["current_stack"]), True, (255, 255, 255))
                    text_rect = text_surface.get_rect(bottomright=(rect_abs.right - 2, rect_abs.bottom - 2))
                    screen.blit(text_surface, text_rect)

    def show_tooltip(self, screen, mouse_pos):
        for slot in self.slots:
            abs_x = self.bg_rect.x + slot["rect"].x
            abs_y = self.bg_rect.y + slot["rect"].y
            rect_abs = pygame.Rect(abs_x, abs_y, slot["rect"].width, slot["rect"].height)

            if rect_abs.collidepoint(mouse_pos) and slot["item"] is not None:
                item = slot["item"]
                tooltip_text = f"{item['name']}\nЦена: {item['price']} золота за шт."

                if "description" in item and item["description"]:
                    tooltip_text += f"\n{item['description']}"

                if "damage" in item and isinstance(item["damage"], (int, float)) and item["damage"] > 0:
                    tooltip_text += f"\nУрон: {item['damage']}"

                font = pygame.font.Font(None, 24)
                tooltip_lines = tooltip_text.split("\n")
                max_width = max(font.size(line)[0] for line in tooltip_lines) + 10
                tooltip_height = len(tooltip_lines) * 20 + 10
                tooltip_surface = pygame.Surface((max_width, tooltip_height), pygame.SRCALPHA)
                tooltip_surface.fill((0, 0, 0, 180))

                for i, line in enumerate(tooltip_lines):
                    text_surface = font.render(line, True, (255, 255, 255))
                    tooltip_surface.blit(text_surface, (5, 5 + i * 20))

                screen_width, screen_height = screen.get_size()
                tooltip_x = min(mouse_pos[0] + 10, screen_width - max_width - 10)
                tooltip_y = min(mouse_pos[1] + 10, screen_height - tooltip_height - 10)
                screen.blit(tooltip_surface, (tooltip_x, tooltip_y))

    def handle_mouse_down(self, mouse_pos):
        if Inventory.dragging_item is not None:
            return

        for i, slot in enumerate(self.slots):
            abs_x = self.bg_rect.x + slot["rect"].x
            abs_y = self.bg_rect.y + slot["rect"].y
            rect_abs = pygame.Rect(abs_x, abs_y, slot["rect"].width, slot["rect"].height)

            if rect_abs.collidepoint(mouse_pos):
                if slot["item"] is not None:
                    Inventory.dragging_item = slot["item"]
                    Inventory.dragging_from = i
                    slot["item"] = None  

                    icon_rect = Inventory.dragging_item["icon"].get_rect(center=rect_abs.center)
                    dx = mouse_pos[0] - icon_rect.x
                    dy = mouse_pos[1] - icon_rect.y
                    Inventory.drag_offset = (dx, dy)
                    Inventory.drag_pos = mouse_pos
                break

    def handle_mouse_motion(self, mouse_pos):
        if Inventory.dragging_item is not None:
            Inventory.drag_pos = mouse_pos

    def handle_mouse_up(self, mouse_pos):
        if Inventory.dragging_item is None:
            return

        dropped_in_slot = False
        for i, slot in enumerate(self.slots):
            abs_x = self.bg_rect.x + slot["rect"].x
            abs_y = self.bg_rect.y + slot["rect"].y
            rect_abs = pygame.Rect(abs_x, abs_y, slot["rect"].width, slot["rect"].height)
            if rect_abs.collidepoint(mouse_pos):
                if slot["item"] is not None and slot["item"]["name"] == Inventory.dragging_item["name"]:
                    free_space = slot["item"]["max_stack"] - slot["item"]["current_stack"]
                    if free_space > 0:
                        to_add = min(Inventory.dragging_item["current_stack"], free_space)
                        slot["item"]["current_stack"] += to_add
                        Inventory.dragging_item["current_stack"] -= to_add
                        if Inventory.dragging_item["current_stack"] == 0:
                            Inventory.dragging_item = None
                        dropped_in_slot = True
                        break
                if slot["item"] is None and Inventory.dragging_item is not None:
                    slot["item"] = Inventory.dragging_item
                    dropped_in_slot = True
                    break
                if not dropped_in_slot:
                    old_item = slot["item"]
                    slot["item"] = Inventory.dragging_item
                    self.slots[Inventory.dragging_from]["item"] = old_item
                    dropped_in_slot = True
                    break
        if not dropped_in_slot:
            self.slots[Inventory.dragging_from]["item"] = Inventory.dragging_item
        Inventory.dragging_item = None
        Inventory.dragging_from = None
        Inventory.drag_offset = (0, 0)
        Inventory.drag_pos = (0, 0)

    def add_existing_item(self, item):
        for slot in self.slots:
            if slot["item"] is None:
                slot["item"] = item
                return
        print("Нет свободных слотов!")

    def remove_existing_item(self, item):
        for slot in self.slots:
            if slot["item"] == item:
                slot["item"] = None
                return
        print("Не нашли предмет в инвентаре.")

    def get_all_items(self):
        all_items = []
        for slot in self.slots:
            if slot["item"] is not None:
                all_items.append(slot["item"])
        return all_items

    def process_event(self, event, screen):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_mouse_down(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            Inventory.drag_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.handle_mouse_up(event.pos)

    def count_item(self, item_id):
        count = 0
        for slot in self.slots:
            if slot["item"] is not None and slot["item"]["id"] == item_id:
                count += slot["item"]["current_stack"]
        return count


class ChestInventory(Inventory):
    def __init__(self):
        super().__init__()
        self.inventory_bg = pygame.image.load("Data/chest_invent.png").convert_alpha()
        self.bg_rect = self.inventory_bg.get_rect()
        self.slot_positions = [(25, 25), (85, 25), (145, 25), (205, 25),
                               (25, 85), (85, 85), (145, 85), (205, 85),
                               (25, 145), (85, 145), (145, 145), (205, 145)]
        self.slot_width, self.slot_height = 55, 55
        self.slots = []
        for pos in self.slot_positions:
            x, y = pos
            r = pygame.Rect(x, y, self.slot_width, self.slot_height)
            self.slots.append({"rect": r, "item": None})
