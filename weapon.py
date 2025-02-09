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
      super().__init__()
      self.original_image = image
      self.angle = angle
      self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
      self.image.fill((255, 255, 0, 100), None, pygame.BLEND_RGBA_ADD)  # Màu vàng phát sáng
      self.rect = self.image.get_rect(center=(x, y))
      self.dx = math.cos(math.radians(self.angle)) * constants.ARROW_SPEED
      self.dy = -(math.sin(math.radians(self.angle)) * constants.ARROW_SPEED)


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
class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        self.angle = angle
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Tính toán tốc độ di chuyển dựa trên góc
        self.dx = math.cos(math.radians(self.angle)) * constants.ARROW_SPEED
        self.dy = -(math.sin(math.radians(self.angle)) * constants.ARROW_SPEED)  # -ve vì tọa độ y tăng xuống dưới

    def update(self, screen_scroll, obstacle_tiles, enemy_list):
        # Reset các biến
        damage = 0
        damage_pos = None

        # Di chuyển viên đạn dựa trên tốc độ
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy

        # Kiểm tra va chạm với các chướng ngại vật
        for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.rect):
                self.kill()

        # Kiểm tra nếu viên đạn ra khỏi màn hình
        if self.rect.right < 0 or self.rect.left > constants.SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT:
            self.kill()

        # Kiểm tra va chạm với kẻ thù
        for enemy in enemy_list:
            if enemy.rect.colliderect(self.rect) and enemy.alive:
                damage = 10 + random.randint(-5, 5)  # Sát thương dao động
                damage_pos = enemy.rect
                enemy.health -= damage
                enemy.hit = True
                self.kill()
                break

        return damage, damage_pos

    def draw(self, surface):
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width() / 2)), self.rect.centery - int(self.image.get_height() / 2)))

class Gun(Weapon):
    def __init__(self, image, bullet_image):
        super().__init__(image, bullet_image)

    def update(self, player):
        shot_cooldown = 200
        bullet = None
        self.rect.center = player.rect.center
        pos = pygame.mouse.get_pos()
        x_dist = pos[0] - self.rect.centerx
        y_dist = -(pos[1] - self.rect.centery)
        self.angle = math.degrees(math.atan2(y_dist, x_dist))

        # Bắn đạn khi nhấn chuột trái
        if pygame.mouse.get_pressed()[0] and not self.fired and (pygame.time.get_ticks() - self.last_shot) >= shot_cooldown:
            bullet = Bullet(self.arrow_image, self.rect.centerx, self.rect.centery, self.angle)
            self.fired = True
            self.last_shot = pygame.time.get_ticks()

        # Reset trạng thái bắn
        if not pygame.mouse.get_pressed()[0]:
            self.fired = False

        return bullet

class Sword(Weapon):
    def __init__(self, image):
        super().__init__(image, None)  # Kiếm không cần ảnh mũi tên
        self.range = 50  # Khoảng cách tấn công của kiếm

    def update(self, player, enemy_list):
        damage = 0
        if pygame.mouse.get_pressed()[0]:  # Nếu nhấn chuột trái
            for enemy in enemy_list:
                if enemy.rect.colliderect(player.rect):  # Kiểm tra va chạm giữa nhân vật và kẻ địch
                    damage = 20  # Sát thương gấp đôi
                    enemy.health -= damage
                    enemy.hit = True
                    break  # Chỉ đánh một kẻ thù mỗi lần

        return damage



    def draw(self, surface, player):
        # Vẽ kiếm ở vị trí của nhân vật
        self.rect.center = player.rect.center
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image, (self.rect.centerx - int(self.image.get_width() / 2), self.rect.centery - int(self.image.get_height() / 2)))
