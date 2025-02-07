import pygame
import json
import sys


class CraftingBookMenu:
    def __init__(self, inventory, json_path, book_image_path):
        self.inventory = inventory
        self.json_path = json_path
        self.book_image_path = book_image_path

        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.craftable_items = [item for item in data if "ingredients" in item]
        self.item_names = {}
        for item in data:
            if "id" in item and "name" in item:
                self.item_names[item["id"]] = item["name"]

        self.font = pygame.font.Font(None, 24)
        self.craft_sound = pygame.mixer.Sound("Data/eb558a111597a65.mp3")

        self.book_image = pygame.image.load(self.book_image_path).convert_alpha()
        self.book_rect = self.book_image.get_rect()
        self.book_rect.center = (400, 300)

        self.recipes_per_page = 6
        self.current_page = 0
        self.total_pages = (len(self.craftable_items) + self.recipes_per_page - 1) // self.recipes_per_page

        self.left_page_rect = pygame.Rect(self.book_rect.x + 50, self.book_rect.y + 50, 200, 300)
        self.right_page_rect = pygame.Rect(self.book_rect.x + 350, self.book_rect.y + 50, 200, 300)

        self.left_arrow_rect = pygame.Rect(self.book_rect.x - 40,
                                           self.book_rect.centery - 20, 30, 40)
        self.right_arrow_rect = pygame.Rect(self.book_rect.right + 10,
                                            self.book_rect.centery - 20, 30, 40)

        self.arrow_color = (200, 200, 200)
        self.running = False

    def open(self, screen, clock):
        self.running = True
        background_surf = screen.copy()

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
                        if self.left_arrow_rect.collidepoint(mx, my):
                            self.turn_page(-1)
                        elif self.right_arrow_rect.collidepoint(mx, my):
                            self.turn_page(1)
                        else:
                            self.check_recipe_click(mx, my)
                    elif event.button == 4:
                        self.turn_page(-1)
                    elif event.button == 5:
                        self.turn_page(1)

            screen.blit(background_surf, (0, 0))
            screen.blit(self.book_image, self.book_rect)
            pygame.draw.rect(screen, self.arrow_color, self.left_arrow_rect)
            pygame.draw.rect(screen, self.arrow_color, self.right_arrow_rect)
            arrow_font = pygame.font.Font(None, 36)
            left_arrow_text = arrow_font.render("<", True, (0, 0, 0))
            right_arrow_text = arrow_font.render(">", True, (0, 0, 0))
            screen.blit(left_arrow_text, (self.left_arrow_rect.centerx - left_arrow_text.get_width() // 2,
                                          self.left_arrow_rect.centery - left_arrow_text.get_height() // 2))
            screen.blit(right_arrow_text, (self.right_arrow_rect.centerx - right_arrow_text.get_width() // 2,
                                           self.right_arrow_rect.centery - right_arrow_text.get_height() // 2))

            self.draw_recipes(screen)
            pygame.display.flip()
            clock.tick(60)

    def turn_page(self, direction):
        new_page = self.current_page + direction
        if 0 <= new_page < self.total_pages:
            self.current_page = new_page

    def draw_recipes(self, screen):
        self.recipe_hitboxes = []

        start_index = self.current_page * self.recipes_per_page
        end_index = start_index + self.recipes_per_page
        page_items = self.craftable_items[start_index:end_index]

        half = len(page_items) // 2 + len(page_items) % 2
        left_side = page_items[:half]
        right_side = page_items[half:]

        y_left = self.left_page_rect.top + 35
        x_left = self.left_page_rect.left - 20

        for recipe in left_side:
            hitbox = self.draw_single_recipe(screen, recipe, x_left, y_left)
            self.recipe_hitboxes.append((recipe, hitbox))
            y_left += 80

        y_right = self.right_page_rect.top + 35
        x_right = self.right_page_rect.left - 60

        for recipe in right_side:
            hitbox = self.draw_single_recipe(screen, recipe, x_right, y_right)
            self.recipe_hitboxes.append((recipe, hitbox))
            y_right += 80

    def draw_single_recipe(self, screen, recipe, x, y):

        icon = pygame.image.load(recipe["icon_path"]).convert_alpha()
        icon = pygame.transform.scale(icon, (32, 32))
        screen.blit(icon, (x, y))

        text_surf = self.font.render(recipe["name"], True, (255, 255, 255))
        screen.blit(text_surf, (x + 40, y))

        line_height = self.font.get_linesize()
        base_y = y + 20
        for i, ing in enumerate(recipe["ingredients"]):
            ing_text = f"{self.item_names.get(ing['id'], ing['id'])} x {ing['quantity']}"
            ing_surf = self.font.render(ing_text, True, (200, 200, 200))
            screen.blit(ing_surf, (x + 40, base_y + i * line_height))

        hitbox_height = 20 + len(recipe["ingredients"]) * line_height
        recipe_hitbox = pygame.Rect(x, y, 200, hitbox_height)
        return recipe_hitbox

    def check_recipe_click(self, mx, my):

        for recipe, hitbox in self.recipe_hitboxes:
            if hitbox.collidepoint(mx, my):
                self.try_craft(recipe)
                return

    def try_craft(self, recipe):
        if self.has_ingredients(recipe):
            self.remove_ingredients(recipe)
            self.add_result_item(recipe)
            print(f"Скрафтили {recipe['name']}")
            self.craft_sound.play()
        else:
            print("Недостаточно ресурсов!")

    def has_ingredients(self, recipe):
        for ing in recipe["ingredients"]:
            needed = ing["quantity"]
            have = self.inventory.count_item(ing["id"])
            if have < needed:
                return False
        return True

    def remove_ingredients(self, recipe):
        for ing in recipe["ingredients"]:
            self.inventory.remove_item(ing["id"], ing["quantity"])

    def add_result_item(self, recipe):
        self.inventory.add_item(
            item_id=recipe["id"],
            item_name=recipe["name"],
            icon_path=recipe["icon_path"],
            price=recipe.get("price", 0),
            description=recipe.get("description", ""),
            damage=recipe.get("damage", 0),
            max_stack=recipe.get("max_stack", 1),
            quantity=1
        )
