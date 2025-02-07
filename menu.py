import pygame
import sys


def show_main_menu(screen, clock, volume):
    """Отображает главное меню и возвращает 'play' или 'quit'."""
    pygame.mixer.music.set_volume(volume)
    background_image = pygame.image.load("Data/menu_back.png").convert()
    background_image = pygame.transform.scale(background_image, screen.get_size())
    play_button_images = {"normal": pygame.image.load("Data/buttons/play/play01.png").convert_alpha(),
                          "hover": pygame.image.load("Data/buttons/play/play02.png").convert_alpha(),
                          "pressed": pygame.image.load("Data/buttons/play/play03.png").convert_alpha()}

    quit_button_images = {"normal": pygame.image.load("Data/buttons/back/back01.png").convert_alpha(),
                          "hover": pygame.image.load("Data/buttons/back/back02.png").convert_alpha(),
                          "pressed": pygame.image.load("Data/buttons/back/back03.png").convert_alpha()}

    settings_button_images = {"normal": pygame.image.load("Data/buttons/info/information01.png").convert_alpha(),
                              "hover": pygame.image.load("Data/buttons/info/information02.png").convert_alpha(),
                              "pressed": pygame.image.load("Data/buttons/info/information03.png").convert_alpha()}

    game_name = pygame.image.load("Data/yaname (1).png")
    menu_bg = pygame.Surface(screen.get_size())
    menu_bg.fill((50, 100, 50))

    play_button_rect = play_button_images["normal"].get_rect(topleft=(370, 450))
    settings_button_rect = settings_button_images["normal"].get_rect(topleft=(450, 525))
    quit_button_rect = quit_button_images["normal"].get_rect(topleft=(550, 450))
    name_rect = game_name.get_rect(topleft=(220, 0))

    play_button_state = "normal"
    settings_button_state = "normal"
    quit_button_state = "normal"

    def update_button_state_on_hover(mouse_pos):
        nonlocal play_button_state, quit_button_state, settings_button_state

        if play_button_rect.collidepoint(mouse_pos):
            if play_button_state != "pressed":
                play_button_state = "hover"
        else:
            if play_button_state != "pressed":
                play_button_state = "normal"

        if settings_button_rect.collidepoint(mouse_pos):
            if settings_button_state != "pressed":
                settings_button_state = "hover"
        else:
            if settings_button_state != "pressed":
                settings_button_state = "normal"

        if quit_button_rect.collidepoint(mouse_pos):
            if quit_button_state != "pressed":
                quit_button_state = "hover"
        else:
            if quit_button_state != "pressed":
                quit_button_state = "normal"

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEMOTION:
                update_button_state_on_hover(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_button_rect.collidepoint(event.pos):
                        play_button_state = "pressed"
                    if settings_button_rect.collidepoint(event.pos):
                        settings_button_state = "pressed"
                    if quit_button_rect.collidepoint(event.pos):
                        quit_button_state = "pressed"

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:

                    if play_button_state == "pressed":
                        if play_button_rect.collidepoint(event.pos):
                            return "play"
                        else:
                            play_button_state = "normal"

                    if settings_button_state == "pressed":
                        if settings_button_rect.collidepoint(event.pos):
                            return ("settings", volume)
                        else:
                            settings_button_state = "normal"

                    if quit_button_state == "pressed":
                        if quit_button_rect.collidepoint(event.pos):
                            return "quit"
                        else:
                            quit_button_state = "normal"

                    update_button_state_on_hover(mouse_pos)
        screen.blit(background_image, (0, 0))
        screen.blit(game_name, name_rect)

        current_play_image = play_button_images[play_button_state]
        current_settings_image = settings_button_images[settings_button_state]
        current_quit_image = quit_button_images[quit_button_state]

        screen.blit(current_play_image, play_button_rect)
        screen.blit(current_settings_image, settings_button_rect)
        screen.blit(current_quit_image, quit_button_rect)

        pygame.display.flip()
        clock.tick(60)


def show_settings_menu(screen, clock, volume):
    pygame.font.init()

    background_image = pygame.Surface(screen.get_size())
    background_image.fill((60, 60, 60))

    font = pygame.font.Font(None, 40)

    back_button_surf = pygame.Surface((150, 50))
    back_button_surf.fill((180, 180, 180))
    back_button_rect = back_button_surf.get_rect(topleft=(50, 500))

    back_text = font.render("Back", True, (0, 0, 0))
    current_volume = volume

    plus_surf = pygame.Surface((40, 40))
    plus_surf.fill((100, 200, 100))
    minus_surf = pygame.Surface((40, 40))
    minus_surf.fill((200, 100, 100))

    volume_minus_rect = minus_surf.get_rect(topleft=(225, 150))
    volume_plus_rect = plus_surf.get_rect(topleft=(300, 150))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return current_volume, "back"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if back_button_rect.collidepoint(event.pos):
                        return current_volume, "back"

                    if volume_minus_rect.collidepoint(event.pos):
                        current_volume = max(0.0, current_volume - 0.1)
                        pygame.mixer.music.set_volume(current_volume)

                    if volume_plus_rect.collidepoint(event.pos):
                        current_volume = min(1.0, current_volume + 0.1)
                        pygame.mixer.music.set_volume(current_volume)

        screen.blit(background_image, (0, 0))

        screen.blit(back_button_surf, back_button_rect)
        screen.blit(back_text, (back_button_rect.centerx - back_text.get_width() // 2,
                                back_button_rect.centery - back_text.get_height() // 2))

        vol_text = font.render(f"Volume: {current_volume:.1f}", True, (255, 255, 255))
        screen.blit(vol_text, (50, 150))
        screen.blit(minus_surf, volume_minus_rect)
        screen.blit(plus_surf, volume_plus_rect)

        pygame.display.flip()
        clock.tick(60)
