button.py:

import pygame

class Button():
  def __init__(self, x, y, image):
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.topleft = (x, y)

  def draw(self, surface):
    action = False

    #get mouse position
    pos = pygame.mouse.get_pos()

    #check mouseover and clicked conditions
    if self.rect.collidepoint(pos):
      if pygame.mouse.get_pressed()[0]:
        action = True

    surface.blit(self.image, self.rect)

    return action

character.py:
import pygame
import math
import weapon
import constants

class Character():
  def __init__(self, x, y, health, mob_animations, char_type, boss, size):
    self.char_type = char_type
    self.boss = boss
    self.score = 0
    self.flip = False
    self.animation_list = mob_animations[char_type]
    self.frame_index = 0
    self.action = 0#0:idle, 1:run
    self.update_time = pygame.time.get_ticks()
    self.running = False
    self.health = health
    self.alive = True
    self.hit = False
    self.last_hit = pygame.time.get_ticks()
    self.last_attack = pygame.time.get_ticks()
    self.stunned = False

    self.image = self.animation_list[self.action][self.frame_index]
    self.rect = pygame.Rect(0, 0, constants.TILE_SIZE * size, constants.TILE_SIZE * size)
    self.rect.center = (x, y)

  def move(self, dx, dy, obstacle_tiles, exit_tile = None):
    screen_scroll = [0, 0]
    level_complete = False
    self.running = False

    if dx != 0 or dy != 0:
      self.running = True
    if dx < 0:
      self.flip = True
    if dx > 0:
      self.flip = False
    #control diagonal speed
    if dx != 0 and dy != 0:
      dx = dx * (math.sqrt(2)/2)
      dy = dy * (math.sqrt(2)/2)

    #check for collision with map in x direction
    self.rect.x += dx
    for obstacle in obstacle_tiles:
      #check for collision
      if obstacle[1].colliderect(self.rect):
        #check which side the collision is from
        if dx > 0:
          self.rect.right = obstacle[1].left
        if dx < 0:
          self.rect.left = obstacle[1].right

    #check for collision with map in y direction
    self.rect.y += dy
    for obstacle in obstacle_tiles:
      #check for collision
      if obstacle[1].colliderect(self.rect):
        #check which side the collision is from
        if dy > 0:
          self.rect.bottom = obstacle[1].top
        if dy < 0:
          self.rect.top = obstacle[1].bottom


    #logic only applicable to player
    if self.char_type == 0:
      #check collision with exit ladder
      if exit_tile[1].colliderect(self.rect):
        #ensure player is close to the center of the exit ladder
        exit_dist = math.sqrt(((self.rect.centerx - exit_tile[1].centerx) ** 2) + ((self.rect.centery - exit_tile[1].centery) ** 2))
        if exit_dist < 20:
          level_complete = True

      #update scroll based on player position
      #move camera left and right
      if self.rect.right > (constants.SCREEN_WIDTH - constants.SCROLL_THRESH):
        screen_scroll[0] = (constants.SCREEN_WIDTH - constants.SCROLL_THRESH) - self.rect.right
        self.rect.right = constants.SCREEN_WIDTH - constants.SCROLL_THRESH
      if self.rect.left < constants.SCROLL_THRESH:
        screen_scroll[0] = constants.SCROLL_THRESH - self.rect.left
        self.rect.left = constants.SCROLL_THRESH

      #move camera up and down
      if self.rect.bottom > (constants.SCREEN_HEIGHT - constants.SCROLL_THRESH):
        screen_scroll[1] = (constants.SCREEN_HEIGHT - constants.SCROLL_THRESH) - self.rect.bottom
        self.rect.bottom = constants.SCREEN_HEIGHT - constants.SCROLL_THRESH
      if self.rect.top < constants.SCROLL_THRESH:
        screen_scroll[1] = constants.SCROLL_THRESH - self.rect.top
        self.rect.top = constants.SCROLL_THRESH

    return screen_scroll, level_complete


  def ai(self, player, obstacle_tiles, screen_scroll, fireball_image):
    clipped_line = ()
    stun_cooldown = 100
    ai_dx = 0
    ai_dy = 0
    fireball = None

    #reposition the mobs based on screen scroll
    self.rect.x += screen_scroll[0]
    self.rect.y += screen_scroll[1]

    #create a line of sight from the enemy to the player
    line_of_sight = ((self.rect.centerx, self.rect.centery), (player.rect.centerx, player.rect.centery))
    #check if line of sight passes through an obstacle tile
    for obstacle in obstacle_tiles:
      if obstacle[1].clipline(line_of_sight):
        clipped_line = obstacle[1].clipline(line_of_sight)

    #check distance to player
    dist = math.sqrt(((self.rect.centerx - player.rect.centerx) ** 2) + ((self.rect.centery - player.rect.centery) ** 2))
    if not clipped_line and dist > constants.RANGE:
      if self.rect.centerx > player.rect.centerx:
        ai_dx = -constants.ENEMY_SPEED
      if self.rect.centerx < player.rect.centerx:
        ai_dx = constants.ENEMY_SPEED
      if self.rect.centery > player.rect.centery:
        ai_dy = -constants.ENEMY_SPEED
      if self.rect.centery < player.rect.centery:
        ai_dy = constants.ENEMY_SPEED

    if self.alive:
      if not self.stunned:
        #move towards player
        self.move(ai_dx, ai_dy, obstacle_tiles)
        #attack player
        if dist < constants.ATTACK_RANGE and player.hit == False:
          player.health -= 10
          player.hit = True
          player.last_hit = pygame.time.get_ticks()
        #boss enemies shoot fireballs
        fireball_cooldown = 700
        if self.boss:
          if dist < 500:
            if pygame.time.get_ticks() - self.last_attack >= fireball_cooldown:
              fireball = weapon.Fireball(fireball_image, self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
              self.last_attack = pygame.time.get_ticks()


      #check if hit
      if self.hit == True:
        self.hit = False
        self.last_hit = pygame.time.get_ticks()
        self.stunned = True
        self.running = False
        self.update_action(0)

      if (pygame.time.get_ticks() - self.last_hit > stun_cooldown):
        self.stunned = False

    return fireball

  def update(self):
    #check if character has died
    if self.health <= 0:
      self.health = 0
      self.alive = False

    #timer to reset player taking a hit
    hit_cooldown = 1000
    if self.char_type == 0:
      if self.hit == True and (pygame.time.get_ticks() - self.last_hit) > hit_cooldown:
        self.hit = False

    #check what action the player is performing
    if self.running == True:
      self.update_action(1)#1:run
    else:
      self.update_action(0)#0:idle

    animation_cooldown = 70
    #handle animation
    #update image
    self.image = self.animation_list[self.action][self.frame_index]
    #check if enough time has passed since the last update
    if pygame.time.get_ticks() - self.update_time > animation_cooldown:
      self.frame_index += 1
      self.update_time = pygame.time.get_ticks()
    #check if the animation has finished
    if self.frame_index >= len(self.animation_list[self.action]):
      self.frame_index = 0


  def update_action(self, new_action):
    #check if the new action is different to the previous one
    if new_action != self.action:
      self.action = new_action
      #update the animation settings
      self.frame_index = 0
      self.update_time = pygame.time.get_ticks()


  def draw(self, surface):
    flipped_image = pygame.transform.flip(self.image, self.flip, False)
    if self.char_type == 0:
      surface.blit(flipped_image, (self.rect.x, self.rect.y - constants.SCALE * constants.OFFSET))
    else:
      surface.blit(flipped_image, self.rect)

constants.py:
FPS = 60
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCALE = 3
BUTTON_SCALE = 1
WEAPON_SCALE = 1.5
ITEM_SCALE = 3
POTION_SCALE = 2
FIREBALL_SCALE = 1
SPEED = 5
ARROW_SPEED = 10
FIREBALL_SPEED = 4
ENEMY_SPEED = 4
OFFSET = 12
TILE_SIZE = 16 * SCALE
TILE_TYPES = 18
ROWS = 150
COLS = 150
SCROLL_THRESH = 200
RANGE = 50
ATTACK_RANGE = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)
RED = (255, 0, 0)
BG = (40, 25, 25)
MENU_BG = (130, 0, 0)
PANEL = (50, 50, 50)

items.py:
import pygame

class Item(pygame.sprite.Sprite):
  def __init__(self, x, y, item_type, animation_list, dummy_coin = False):
    pygame.sprite.Sprite.__init__(self)
    self.item_type = item_type#0: coin, 1: health potion
    self.animation_list = animation_list
    self.frame_index = 0
    self.update_time = pygame.time.get_ticks()
    self.image = self.animation_list[self.frame_index]
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.dummy_coin = dummy_coin

  def update(self, screen_scroll, player, coin_fx, heal_fx):
    #doesn't apply to the dummy coin that is always displayed at the top of the screen
    if not self.dummy_coin:
      #reposition based on screen scroll
      self.rect.x += screen_scroll[0]
      self.rect.y += screen_scroll[1]

    #check to see if item has been collected by the player
    if self.rect.colliderect(player.rect):
      #coin collected
      if self.item_type == 0:
        player.score += 1
        coin_fx.play()
      elif self.item_type == 1:
        player.health += 10
        heal_fx.play()
        if player.health > 100:
          player.health = 100
      self.kill()

    #handle animation
    animation_cooldown = 150
    #update image
    self.image = self.animation_list[self.frame_index]
    #check if enough time has passed since the last update
    if pygame.time.get_ticks() - self.update_time > animation_cooldown:
      self.frame_index += 1
      self.update_time = pygame.time.get_ticks()
    #check if the animation has finished
    if self.frame_index >= len(self.animation_list):
      self.frame_index = 0


  def draw(self, surface):
    surface.blit(self.image, self.rect)
main.py:
import pygame
from pygame import mixer
import csv
import constants
from character import Character
from weapon import Weapon
from items import Item
from world import World
from button import Button

mixer.init()
pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Crawler")

#create clock for maintaining frame rate
clock = pygame.time.Clock()

#define game variables
level = 1
start_game = False
pause_game = False
start_intro = False
screen_scroll = [0, 0]

#define player movement variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False

#define font
font = pygame.font.Font("assets/fonts/AtariClassic.ttf", 20)

#helper function to scale image
def scale_img(image, scale):
  w = image.get_width()
  h = image.get_height()
  return pygame.transform.scale(image, (w * scale, h * scale))

#load music and sounds
pygame.mixer.music.load("assets/audio/music.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
shot_fx = pygame.mixer.Sound("assets/audio/arrow_shot.mp3")
shot_fx.set_volume(0.5)
hit_fx = pygame.mixer.Sound("assets/audio/arrow_hit.wav")
hit_fx.set_volume(0.5)
coin_fx = pygame.mixer.Sound("assets/audio/coin.wav")
coin_fx.set_volume(0.5)
heal_fx = pygame.mixer.Sound("assets/audio/heal.wav")
heal_fx.set_volume(0.5)

#load button images
start_img = scale_img(pygame.image.load("assets/images/buttons/button_start.png").convert_alpha(), constants.BUTTON_SCALE)
exit_img = scale_img(pygame.image.load("assets/images/buttons/button_exit.png").convert_alpha(), constants.BUTTON_SCALE)
restart_img = scale_img(pygame.image.load("assets/images/buttons/button_restart.png").convert_alpha(), constants.BUTTON_SCALE)
resume_img = scale_img(pygame.image.load("assets/images/buttons/button_resume.png").convert_alpha(), constants.BUTTON_SCALE)

#load heart images
heart_empty = scale_img(pygame.image.load("assets/images/items/heart_empty.png").convert_alpha(), constants.ITEM_SCALE)
heart_half = scale_img(pygame.image.load("assets/images/items/heart_half.png").convert_alpha(), constants.ITEM_SCALE)
heart_full = scale_img(pygame.image.load("assets/images/items/heart_full.png").convert_alpha(), constants.ITEM_SCALE)

#load coin images
coin_images = []
for x in range(4):
  img = scale_img(pygame.image.load(f"assets/images/items/coin_f{x}.png").convert_alpha(), constants.ITEM_SCALE)
  coin_images.append(img)

#load potion image
red_potion = scale_img(pygame.image.load("assets/images/items/potion_red.png").convert_alpha(), constants.POTION_SCALE)

item_images = []
item_images.append(coin_images)
item_images.append(red_potion)

#load weapon images
bow_image = scale_img(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_image = scale_img(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), constants.WEAPON_SCALE)
fireball_image = scale_img(pygame.image.load("assets/images/weapons/fireball.png").convert_alpha(), constants.FIREBALL_SCALE)

#load tilemap images
tile_list = []
for x in range(constants.TILE_TYPES):
  tile_image = pygame.image.load(f"assets/images/tiles/{x}.png").convert_alpha()
  tile_image = pygame.transform.scale(tile_image, (constants.TILE_SIZE, constants.TILE_SIZE))
  tile_list.append(tile_image)

#load character images
mob_animations = []
mob_types = ["elf", "imp", "skeleton", "goblin", "muddy", "tiny_zombie", "big_demon"]

animation_types = ["idle", "run"]
for mob in mob_types:
  #load images
  animation_list = []
  for animation in animation_types:
    #reset temporary list of images
    temp_list = []
    for i in range(4):
      img = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
      img = scale_img(img, constants.SCALE)
      temp_list.append(img)
    animation_list.append(temp_list)
  mob_animations.append(animation_list)


#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

#function for displaying game info
def draw_info():
  pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 50))
  pygame.draw.line(screen, constants.WHITE, (0, 50), (constants.SCREEN_WIDTH, 50))
  #draw lives
  half_heart_drawn = False
  for i in range(5):
    if player.health >= ((i + 1) * 20):
      screen.blit(heart_full, (10 + i * 50, 0))
    elif (player.health % 20 > 0) and half_heart_drawn == False:
      screen.blit(heart_half, (10 + i * 50, 0))
      half_heart_drawn = True
    else:
      screen.blit(heart_empty, (10 + i * 50, 0))

  #level
  draw_text("LEVEL: " + str(level), font, constants.WHITE, constants.SCREEN_WIDTH / 2, 15)
  #show score
  draw_text(f"X{player.score}", font, constants.WHITE, constants.SCREEN_WIDTH - 100, 15)

#function to reset level
def reset_level():
  damage_text_group.empty()
  arrow_group.empty()
  item_group.empty()
  fireball_group.empty()

  #create empty tile list
  data = []
  for row in range(constants.ROWS):
    r = [-1] * constants.COLS
    data.append(r)

  return data



#damage text class
class DamageText(pygame.sprite.Sprite):
  def __init__(self, x, y, damage, color):
    pygame.sprite.Sprite.__init__(self)
    self.image = font.render(damage, True, color)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.counter = 0

  def update(self):
    #reposition based on screen scroll
    self.rect.x += screen_scroll[0]
    self.rect.y += screen_scroll[1]

    #move damage text up
    self.rect.y -= 1
    #delete the counter after a few seconds
    self.counter += 1
    if self.counter > 30:
      self.kill()

#class for handling screen fade
class ScreenFade():
  def __init__(self, direction, colour, speed):
    self.direction = direction
    self.colour = colour
    self.speed = speed
    self.fade_counter = 0

  def fade(self):
    fade_complete = False
    self.fade_counter += self.speed
    if self.direction == 1:#whole screen fade
      pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT))
      pygame.draw.rect(screen, self.colour, (constants.SCREEN_WIDTH // 2 + self.fade_counter, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
      pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT // 2))
      pygame.draw.rect(screen, self.colour, (0, constants.SCREEN_HEIGHT // 2 + self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    elif self.direction == 2:#vertical screen fade down
      pygame.draw.rect(screen, self.colour, (0, 0, constants.SCREEN_WIDTH, 0 + self.fade_counter))

    if self.fade_counter >= constants.SCREEN_WIDTH:
      fade_complete = True

    return fade_complete


#create empty tile list
world_data = []
for row in range(constants.ROWS):
  r = [-1] * constants.COLS
  world_data.append(r)
#load in level data and create world
with open(f"levels/level{level}_data.csv", newline="") as csvfile:
  reader = csv.reader(csvfile, delimiter = ",")
  for x, row in enumerate(reader):
    for y, tile in enumerate(row):
      world_data[x][y] = int(tile)


world = World()
world.process_data(world_data, tile_list, item_images, mob_animations)

#create player
player = world.player
#create player's weapon
bow = Weapon(bow_image, arrow_image)

#extract enemies from world data
enemy_list = world.character_list

#create sprite groups
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()

score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
item_group.add(score_coin)
#add the items from the level data
for item in world.item_list:
  item_group.add(item)


#create screen fades
intro_fade = ScreenFade(1, constants.BLACK, 4)
death_fade = ScreenFade(2, constants.PINK, 4)

#create button
start_button = Button(constants.SCREEN_WIDTH // 2 - 145, constants.SCREEN_HEIGHT // 2 - 150, start_img)
exit_button = Button(constants.SCREEN_WIDTH // 2 - 110, constants.SCREEN_HEIGHT // 2 + 50, exit_img)
restart_button = Button(constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 50, restart_img)
resume_button = Button(constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 150, resume_img)

#main game loop
run = True
while run:

  #control frame rate
  clock.tick(constants.FPS)

  if start_game == False:
    screen.fill(constants.MENU_BG)
    if start_button.draw(screen):
      start_game = True
      start_intro = True
    if exit_button.draw(screen):
      run = False
  else:
    if pause_game == True:
      screen.fill(constants.MENU_BG)
      if resume_button.draw(screen):
        pause_game = False
      if exit_button.draw(screen):
        run = False
    else:
      screen.fill(constants.BG)

      if player.alive:
        #calculate player movement
        dx = 0
        dy = 0
        if moving_right == True:
          dx = constants.SPEED
        if moving_left == True:
          dx = -constants.SPEED
        if moving_up == True:
          dy = -constants.SPEED
        if moving_down == True:
          dy = constants.SPEED

        #move player
        screen_scroll, level_complete = player.move(dx, dy, world.obstacle_tiles, world.exit_tile)

        #update all objects
        world.update(screen_scroll)
        for enemy in enemy_list:
          fireball = enemy.ai(player, world.obstacle_tiles, screen_scroll, fireball_image)
          if fireball:
            fireball_group.add(fireball)
          if enemy.alive:
            enemy.update()
        player.update()
        arrow = bow.update(player)
        if arrow:
          arrow_group.add(arrow)
          shot_fx.play()
        for arrow in arrow_group:
          damage, damage_pos = arrow.update(screen_scroll, world.obstacle_tiles, enemy_list)
          if damage:
            damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), constants.RED)
            damage_text_group.add(damage_text)
            hit_fx.play()
        damage_text_group.update()
        fireball_group.update(screen_scroll, player)
        item_group.update(screen_scroll, player, coin_fx, heal_fx)

      #draw player on screen
      world.draw(screen)
      for enemy in enemy_list:
        enemy.draw(screen)
      player.draw(screen)
      bow.draw(screen)
      for arrow in arrow_group:
        arrow.draw(screen)
      for fireball in fireball_group:
        fireball.draw(screen)
      damage_text_group.draw(screen)
      item_group.draw(screen)
      draw_info()
      score_coin.draw(screen)

      #check level complete
      if level_complete == True:
        start_intro = True
        level += 1
        world_data = reset_level()
        #load in level data and create world
        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
          reader = csv.reader(csvfile, delimiter = ",")
          for x, row in enumerate(reader):
            for y, tile in enumerate(row):
              world_data[x][y] = int(tile)
        world = World()
        world.process_data(world_data, tile_list, item_images, mob_animations)
        temp_hp = player.health
        temp_score = player.score
        player = world.player
        player.health = temp_hp
        player.score = temp_score
        enemy_list = world.character_list
        score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
        item_group.add(score_coin)
        #add the items from the level data
        for item in world.item_list:
          item_group.add(item)


      #show intro
      if start_intro == True:
        if intro_fade.fade():
          start_intro = False
          intro_fade.fade_counter = 0

      #show death screen
      if player.alive == False:
        if death_fade.fade():
          if restart_button.draw(screen):
            death_fade.fade_counter = 0
            start_intro = True
            world_data = reset_level()
            #load in level data and create world
            with open(f"levels/level{level}_data.csv", newline="") as csvfile:
              reader = csv.reader(csvfile, delimiter = ",")
              for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                  world_data[x][y] = int(tile)
            world = World()
            world.process_data(world_data, tile_list, item_images, mob_animations)
            temp_score = player.score
            player = world.player
            player.score = temp_score
            enemy_list = world.character_list
            score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
            item_group.add(score_coin)
            #add the items from the level data
            for item in world.item_list:
              item_group.add(item)

  #event handler
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
    #take keyboard presses
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_a:
        moving_left = True
      if event.key == pygame.K_d:
        moving_right = True
      if event.key == pygame.K_w:
        moving_up = True
      if event.key == pygame.K_s:
        moving_down = True
      if event.key == pygame.K_ESCAPE:
        pause_game = True


    #keyboard button released
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_a:
        moving_left = False
      if event.key == pygame.K_d:
        moving_right = False
      if event.key == pygame.K_w:
        moving_up = False
      if event.key == pygame.K_s:
        moving_down = False

  pygame.display.update()


pygame.quit()
weapon.py:
import pygame
import math
import random
import constants

class Weapon():
  def __init__(self, image, arrow_image):
    self.original_image = image
    self.angle = 0
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.arrow_image = arrow_image
    self.rect = self.image.get_rect()
    self.fired = False
    self.last_shot = pygame.time.get_ticks()

  def update(self, player):
    shot_cooldown = 300
    arrow = None

    self.rect.center = player.rect.center

    pos = pygame.mouse.get_pos()
    x_dist = pos[0] - self.rect.centerx
    y_dist = -(pos[1] - self.rect.centery)#-ve because pygame y coordinates increase down the screen
    self.angle = math.degrees(math.atan2(y_dist, x_dist))

    #get mouseclick
    if pygame.mouse.get_pressed()[0] and self.fired == False and (pygame.time.get_ticks() - self.last_shot) >= shot_cooldown:
      arrow = Arrow(self.arrow_image, self.rect.centerx, self.rect.centery, self.angle)
      self.fired = True
      self.last_shot = pygame.time.get_ticks()
    #reset mouseclick
    if pygame.mouse.get_pressed()[0] == False:
      self.fired = False


    return arrow

  def draw(self, surface):
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), self.rect.centery - int(self.image.get_height()/2)))


class Arrow(pygame.sprite.Sprite):
  def __init__(self, image, x, y, angle):
    pygame.sprite.Sprite.__init__(self)
    self.original_image = image
    self.angle = angle
    self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    #calculate the horizontal and vertical speeds based on the angle
    self.dx = math.cos(math.radians(self.angle)) * constants.ARROW_SPEED
    self.dy = -(math.sin(math.radians(self.angle)) * constants.ARROW_SPEED)#-ve because pygame y coordiate increases down the screen


  def update(self, screen_scroll, obstacle_tiles, enemy_list):
    #reset variables
    damage = 0
    damage_pos = None

    #reposition based on speed
    self.rect.x += screen_scroll[0] + self.dx
    self.rect.y += screen_scroll[1] + self.dy

    #check for collision between arrow and tile walls
    for obstacle in obstacle_tiles:
      if obstacle[1].colliderect(self.rect):
        self.kill()

    #check if arrow has gone off screen
    if self.rect.right < 0 or self.rect.left > constants.SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT:
      self.kill()

    #check collision between arrow and enemies
    for enemy in enemy_list:
      if enemy.rect.colliderect(self.rect) and enemy.alive:
        damage = 10 + random.randint(-5, 5)
        damage_pos = enemy.rect
        enemy.health -= damage
        enemy.hit = True
        self.kill()
        break

    return damage, damage_pos

  def draw(self, surface):
    surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), self.rect.centery - int(self.image.get_height()/2)))


class Fireball(pygame.sprite.Sprite):
  def __init__(self, image, x, y, target_x, target_y):
    pygame.sprite.Sprite.__init__(self)
    self.original_image = image
    x_dist = target_x - x
    y_dist = -(target_y - y)
    self.angle = math.degrees(math.atan2(y_dist, x_dist))
    self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    #calculate the horizontal and vertical speeds based on the angle
    self.dx = math.cos(math.radians(self.angle)) * constants.FIREBALL_SPEED
    self.dy = -(math.sin(math.radians(self.angle)) * constants.FIREBALL_SPEED)#-ve because pygame y coordiate increases down the screen


  def update(self, screen_scroll, player):
    #reposition based on speed
    self.rect.x += screen_scroll[0] + self.dx
    self.rect.y += screen_scroll[1] + self.dy

    #check if fireball has gone off screen
    if self.rect.right < 0 or self.rect.left > constants.SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT:
      self.kill()

    #check collision between self and player
    if player.rect.colliderect(self.rect) and player.hit == False:
      player.hit = True
      player.last_hit = pygame.time.get_ticks()
      player.health -= 10
      self.kill()


  def draw(self, surface):
    surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), self.rect.centery - int(self.image.get_height()/2)))
world.py:
from character import Character
from items import Item
import constants

class World():
  def __init__(self):
    self.map_tiles = []
    self.obstacle_tiles = []
    self.exit_tile = None
    self.item_list = []
    self.player = None
    self.character_list = []


  def process_data(self, data, tile_list, item_images, mob_animations):
    self.level_length = len(data)
    #iterate through each value in level data file
    for y, row in enumerate(data):
      for x, tile in enumerate(row):
        image = tile_list[tile]
        image_rect = image.get_rect()
        image_x = x * constants.TILE_SIZE
        image_y = y * constants.TILE_SIZE
        image_rect.center = (image_x, image_y)
        tile_data = [image, image_rect, image_x, image_y]

        if tile == 7:
          self.obstacle_tiles.append(tile_data)
        elif tile == 8:
          self.exit_tile = tile_data
        elif tile == 9:
          coin = Item(image_x, image_y, 0, item_images[0])
          self.item_list.append(coin)
          tile_data[0] = tile_list[0]
        elif tile == 10:
          potion = Item(image_x, image_y, 1, [item_images[1]])
          self.item_list.append(potion)
          tile_data[0] = tile_list[0]
        elif tile == 11:
          player = Character(image_x, image_y, 100, mob_animations, 0, False, 1)
          self.player = player
          tile_data[0] = tile_list[0]
        elif tile >= 12 and tile <= 16:
          enemy = Character(image_x, image_y, 100, mob_animations, tile - 11, False, 1)
          self.character_list.append(enemy)
          tile_data[0] = tile_list[0]
        elif tile == 17:
          enemy = Character(image_x, image_y, 100, mob_animations, 6, True, 2)
          self.character_list.append(enemy)
          tile_data[0] = tile_list[0]
          
        #add image data to main tiles list
        if tile >= 0:
          self.map_tiles.append(tile_data)

  def update(self, screen_scroll):
    for tile in self.map_tiles:
      tile[2] += screen_scroll[0]
      tile[3] += screen_scroll[1]
      tile[1].center = (tile[2], tile[3])

  def draw(self, surface):
    for tile in self.map_tiles:
      surface.blit(tile[0], tile[1])# Pygame_weapon_game_custom
