import random
import pygame
import constants

class Environment():
    def __init__(self):
        self.weather_types = ["clear", "rain", "storm", "fog"]
        self.current_weather = "clear"
        self.time_of_day = 0
        self.particles = []
        self.last_particle = pygame.time.get_ticks()
        
    def update(self):
        if random.random() < 0.001:
            self.change_weather()
        self.time_of_day = (self.time_of_day + 0.1) % 24
        self.create_weather_effects()
        self.update_particles()
        
    def change_weather(self):
        self.current_weather = random.choice(self.weather_types)
        
    def create_weather_effects(self):
        particle_cooldown = 50  # Milliseconds between particles
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_particle >= particle_cooldown:
            if self.current_weather == "rain":
                # Tạo hạt mưa
                for _ in range(5):
                    x = random.randint(0, constants.SCREEN_WIDTH)
                    particle = {
                        "x": x,
                        "y": 0,
                        "speed": random.randint(8, 12),
                        "size": random.randint(2, 4)
                    }
                    self.particles.append(particle)
            
            elif self.current_weather == "storm":
                # Tạo hạt mưa bão
                for _ in range(10):
                    x = random.randint(0, constants.SCREEN_WIDTH)
                    particle = {
                        "x": x,
                        "y": 0,
                        "speed": random.randint(12, 15),
                        "size": random.randint(3, 5)
                    }
                    self.particles.append(particle)
            
            self.last_particle = current_time

    def update_particles(self):
        # Cập nhật vị trí của các hạt
        for particle in self.particles[:]:
            particle["y"] += particle["speed"]
            if particle["y"] > constants.SCREEN_HEIGHT:
                self.particles.remove(particle)

    def draw(self, surface):
        # Vẽ hiệu ứng thời tiết
        if self.current_weather in ["rain", "storm"]:
            for particle in self.particles:
                pygame.draw.line(
                    surface,
                    (200, 200, 255),
                    (particle["x"], particle["y"]),
                    (particle["x"], particle["y"] + particle["size"]),
                    1
                )
        
        elif self.current_weather == "fog":
            fog_surface = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
            fog_surface.fill((200, 200, 200))
            fog_surface.set_alpha(100)
            surface.blit(fog_surface, (0, 0))