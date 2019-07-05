# Dino Run
# 2D game inspired by Google Chrome's dinosaur game

# Original Author: Robin Rezwan
# GitHub: http://github.com/robinrezwan

import pygame
from pygame.locals import *
import os
import sys
import random

# set the game window at the center of the display
os.environ['SDL_VIDEO_CENTERED'] = '1'

# defining some global variables
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

FPS = 30

GROUND_HEIGHT = SCREEN_HEIGHT - 70

PLAY_GAME = True

# initialize pygame and create window
pygame.init()
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Run")

clock = pygame.time.Clock()

# load audio files
jump_sound = pygame.mixer.Sound("sound/jump.ogg")
score_sound = pygame.mixer.Sound("sound/score.ogg")
game_over_sound = pygame.mixer.Sound("sound/game_over.ogg")


# function for drawing text on the screen
def draw_text(text, font_name, size, text_color, position_x, position_y, position):

    font = pygame.font.Font(font_name, size)  # loads font

    text_plane = font.render(text, True, text_color)  # renders given text in the selected font
    text_rect = text_plane.get_rect()

    # setting text position
    if position == "midtop":
        text_rect.midtop = (position_x, position_y)
    elif position == "topright":
        text_rect.topright = (position_x, position_y)

    window.blit(text_plane, text_rect)  # draws the rendered text on the screen


# function for loading single image file
def load_image(path, size_x=0, size_y=0):

    image = pygame.image.load(path).convert_alpha()  # loads image file and converts it into pixels

    if size_x > 0 and size_y > 0:
        image = pygame.transform.scale(image, (size_x, size_y))  # resizing the image to the given size

    return image, image.get_rect()


# function for loading multiple image files in a list
def load_sprites(image_path, image_name_prefix, number_of_image, size_x=0, size_y=0):

    images = []  # declaring list to store the images

    for i in range(0, number_of_image):

        path = image_path + image_name_prefix + str(i) + ".png"  # creating the path string
        image = pygame.image.load(path).convert_alpha()  # loads image file and converts it into pixels

        if size_x > 0 and size_y > 0:
            image = pygame.transform.scale(image, (size_x, size_y))  # resizing the image to the given size

        images.append(image)

    return images


# class for creating and moving single background
class Background:

    def __init__(self, image_path, speed=10):

        self.image0, self.rect0 = load_image(image_path, 1280, 720)
        self.image1, self.rect1 = load_image(image_path, 1280, 720)

        self.rect0.bottom = SCREEN_HEIGHT
        self.rect1.bottom = SCREEN_HEIGHT

        self.rect1.left = self.rect0.right

        self.speed = speed

    def draw(self):
        window.blit(self.image0, self.rect0)
        window.blit(self.image1, self.rect1)

    def update(self):

        self.rect0.left -= self.speed
        self.rect1.left -= self.speed

        if self.rect0.right < 0:
            self.rect0.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect0.right


# class for creating and moving single multiple backgrounds using the Background class
class AllBackgrounds:

    def __init__(self, game_speed):

        self.background_0 = Background("image/background/bg_0.png", game_speed)
        self.background_1 = Background("image/background/bg_1.png", game_speed - 12)
        self.background_2 = Background("image/background/bg_2.png", game_speed - 13)
        self.background_3 = Background("image/background/bg_3.png", game_speed - 14)

    def update_speed(self, speed):

        self.background_0.speed = speed
        self.background_1.speed = speed - 12
        self.background_2.speed = speed - 13
        self.background_3.speed = speed - 14

    def draw(self):

        self.background_3.draw()
        self.background_2.draw()
        self.background_1.draw()
        self.background_0.draw()

    def update(self):

        self.background_3.update()
        self.background_2.update()
        self.background_1.update()
        self.background_0.update()


# class for creating and moving obstacle cactus
class Cactus:

    def __init__(self, speed=10):

        self.cactus_images = load_sprites("image/cactus/", "cactus_", 5, 160, 160)

        self.cactus_image_0, self.rect_0 = self.cactus_images[0], self.cactus_images[0].get_rect()
        self.cactus_image_1, self.rect_1 = self.cactus_images[1], self.cactus_images[1].get_rect()

        self.rect_0.bottom = GROUND_HEIGHT - 11
        self.rect_0.left = SCREEN_WIDTH

        self.rect_1.bottom = GROUND_HEIGHT - 11
        self.rect_1.left = self.rect_0.right + SCREEN_WIDTH/2

        self.speed = speed

        self.range_0 = 240
        self.range_1 = 720

    def get_cactus(self):

        current_cactus = [self.cactus_image_0, self.cactus_image_1]
        cactus_rect = [self.rect_0, self.rect_1]

        return current_cactus, cactus_rect

    def update_speed(self, speed):
        self.speed = speed
        self.range_0 += 1
        self.range_1 += 1

    def draw(self):

        window.blit(self.cactus_image_0, self.rect_0)
        window.blit(self.cactus_image_1, self.rect_1)

    def update(self):

        self.rect_0.left -= self.speed
        self.rect_1.left -= self.speed

        if self.rect_0.right < 0:

            temp_position = self.rect_1.right + random.randrange(self.range_0, self.range_1)

            if temp_position > SCREEN_WIDTH:
                self.rect_0.left = temp_position
            else:
                self.rect_0.left = SCREEN_WIDTH

            temp_index = random.randrange(0, 5)
            self.cactus_image_0 = self.cactus_images[temp_index]

        if self.rect_1.right < 0:

            temp_position = self.rect_0.right + random.randrange(self.range_0, self.range_1)

            if temp_position > SCREEN_WIDTH:
                self.rect_1.left = temp_position
            else:
                self.rect_1.left = SCREEN_WIDTH

            temp_index = random.randrange(0, 5)
            self.cactus_image_1 = self.cactus_images[temp_index]


# class for creating and moving our dino buddy
class Dino:

    def __init__(self):

        self.idle_images = load_sprites("image/dino/", "idle_", 10, 220, 153)
        self.running_images = load_sprites("image/dino/", "run_", 8, 220, 153)
        self.jumping_images = load_sprites("image/dino/", "jump_", 16, 220, 153)

        self.rect = self.idle_images[0].get_rect()

        self.rect.bottom = GROUND_HEIGHT
        self.rect.left = 70

        self.jump_limit = GROUND_HEIGHT - 290
        self.jump_speed = 50  # starting speed of the jump
        self.gravity_up = 4  # change rate when jumping up
        self.gravity_down = 2  # change rate when falling down

        # these indexes cycle through the images of the sprites, make the dino look moving
        self.idle_index = 0
        self.running_index = 0
        self.jumping_index = 0

        # these booleans determine which images should be shown
        self.idle = True
        self.running = False
        self.jumping = False
        self.falling = False

        self.call_count = 0  # this variable is used to determine how often a task in a function should be done

    def check_collision(self, all_cactus):

        if self.running:
            dino_mask = pygame.mask.from_surface(self.running_images[self.running_index])
        elif self.jumping:
            dino_mask = pygame.mask.from_surface(self.jumping_images[self.jumping_index])
        else:
            dino_mask = pygame.mask.from_surface(self.idle_images[self.idle_index])

        current_cactus, cactus_rect = all_cactus

        offset_0 = (cactus_rect[0].left - self.rect.left, cactus_rect[0].top - self.rect.top)
        offset_1 = (cactus_rect[1].left - self.rect.left, cactus_rect[1].top - self.rect.top)

        collide = dino_mask.overlap(pygame.mask.from_surface(current_cactus[0]), offset_0) or \
            dino_mask.overlap(pygame.mask.from_surface(current_cactus[1]), offset_1)

        return collide

    def draw(self):

        if self.running:
            window.blit(self.running_images[self.running_index], self.rect)
        elif self.jumping:
            window.blit(self.jumping_images[self.jumping_index], self.rect)
        elif self.idle:
            window.blit(self.idle_images[self.idle_index], self.rect)

    def update(self):

        if self.running and self.call_count % 3 == 0:
            self.running_index = (self.running_index + 1) % 8

        elif self.jumping:

            if not self.falling:
                self.rect.bottom -= self.jump_speed

                if self.jump_speed >= self.gravity_up:
                    self.jump_speed -= self.gravity_up

                if self.rect.bottom < self.jump_limit:

                    self.jump_speed = 0

                    self.falling = True

            else:
                self.rect.bottom += self.jump_speed
                self.jump_speed += self.gravity_down

                if self.rect.bottom > GROUND_HEIGHT:

                    self.rect.bottom = GROUND_HEIGHT

                    self.jump_speed = 50

                    self.jumping_index = 0
                    self.running_index = 0

                    self.jumping = False
                    self.falling = False
                    self.running = True

            if self.call_count % 2 == 0 or self.call_count % 3 == 0:
                self.jumping_index = (self.jumping_index + 1) % 16

        elif self.idle and self.call_count % 3 == 0:
            self.idle_index = (self.idle_index + 1) % 10

        self.call_count = self.call_count + 1


# class for counting and drawing score on the screen and saving high score on a file
class Score:

    def __init__(self):

        self.high_score_image, self.rect_high = load_image("image/score/high_score.png", 35, 35)
        self.current_score_image, self.rect_current = load_image("image/score/current_score.png", 35, 35)

        self.rect_high.topright = (SCREEN_WIDTH - 15, 20)
        self.rect_current.topright = (SCREEN_WIDTH - 15, 65)

        self.high_score = 0
        self.score = 0

        self.load()

        self.high_score_achieved = False

        self.call_count = 0

    def count(self):

        if self.call_count % 2 == 0:

            self.score += 1

            if self.high_score_achieved:
                self.high_score = self.score

            elif self.score > self.high_score:
                self.high_score = self.score
                self.high_score_achieved = True
                score_sound.play()

        self.call_count = self.call_count + 1

    def draw(self):

        window.blit(self.high_score_image, self.rect_high)
        window.blit(self.current_score_image, self.rect_current)

        draw_text(str(self.high_score), "font/monofonto.ttf", 28, (19, 130, 98), SCREEN_WIDTH - 60, 20, "topright")
        draw_text(str(self.score), "font/monofonto.ttf", 28, (19, 130, 98), SCREEN_WIDTH - 60, 65, "topright")

    def load(self):
        # load high score
        try:
            with open("high_score.txt", "r") as file:
                self.high_score = int(file.read())
        except (IOError, ValueError):
            self.high_score = 0

    def save(self):
        # save high score
        if self.high_score_achieved:
            with open("high_score.txt", "w") as file:
                file.write(str(self.high_score))


# class for showing game over screen
class GameOver:

    def __init__(self):
        self.replay_image, self.rect = load_image("image/game_over/replay_0.png", 200, 60)

        self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

    def draw(self):
        draw_text("GAME OVER", "font/northcliff_stencil.otf", 80, (255, 0, 0),
                  SCREEN_WIDTH/2, SCREEN_HEIGHT/3, "midtop")
        window.blit(self.replay_image, self.rect)


# main game function
def start_game():
    # declaring necessary variables and creating objects of the classes
    run = True
    play_again = False
    game_over = False

    game_speed = 15  # the speed the number of pixels the game moves

    backgrounds = AllBackgrounds(game_speed)
    cactus = Cactus(game_speed)
    dino = Dino()
    score = Score()
    game_over_screen = GameOver()

    # main game loop, this will run continuously and draw everything on the screen
    while run:
        clock.tick(FPS)  # limiting frames per second to run loop at the right speed

        # handling input events
        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()  # quits pygame
                sys.exit()  # exits the program

            if event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = pygame.mouse.get_pos()  # gets mouse click co-ordinates

                if game_over:
                    # checks if the play again button is clicked
                    if game_over_screen.rect.left < mx < game_over_screen.rect.right and \
                            game_over_screen.rect.top < my < game_over_screen.rect.bottom:
                        play_again = True
                        run = False

        key = pygame.key.get_pressed()  # gets pressed key

        if key[K_SPACE] or key[K_UP]:

            if game_over:
                play_again = True
                run = False
            elif not dino.jumping:
                jump_sound.play()
                dino.jumping = True
                dino.running = False

                if dino.idle:
                    dino.idle = False

        # calling draw functions to draw all the elements on the screen
        backgrounds.draw()
        cactus.draw()
        dino.draw()
        score.draw()

        if game_over:
            game_over_screen.draw()

        else:
            if not dino.idle:
                score.count()

                backgrounds.update()
                cactus.update()

                # increasing game speed over time
                if score.score % 120 == 0:
                    game_speed += 0.5
                    backgrounds.update_speed(game_speed)
                    cactus.update_speed(game_speed)
                    dino.jump_speed += 5

            dino.update()

            # calling function to check collision
            if dino.check_collision(cactus.get_cactus()):
                game_over = True
                game_over_screen.draw()
                game_over_sound.play()
                score.save()

        pygame.display.flip()  # clears the display before running the loop again

    return play_again  # returns true after game over, if the player wants to play again


# this loop keeps calling the main game function as long as the player wants to continue
while PLAY_GAME:
    PLAY_GAME = start_game()
