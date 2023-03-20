import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600

# Set up the display
screen = pygame.display.set_mode((width, height))

# Load firework sound
firework_sound = pygame.mixer.Sound("source/firework_sound.wav")

# Colors
colors = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
]

class Firework:
    def __init__(self):
        self.x = random.randint(100, width - 100)
        self.y = height
        self.color = random.choice(colors)
        self.speed = random.randint(-30, -20)  # Increase the height by decreasing initial speed
        self.radius = random.randint(2, 6)
        self.particles = []

    def reset(self):
        self.x = random.randint(100, width - 100)
        self.y = height
        self.color = random.choice(colors)
        self.speed = random.randint(-30, -20)  # Increase the height by decreasing initial speed
        self.radius = random.randint(2, 6)
        self.particles = []

    def launch(self):
        self.y += self.speed
        if self.speed < 0:
            self.speed += 1

    def explode(self):
        angle_step = 2 * math.pi / 100
        for angle in range(100):
            speed = random.uniform(2, 5)
            x_speed = speed * math.cos(angle * angle_step)
            y_speed = speed * math.sin(angle * angle_step)
            self.particles.append([self.x, self.y, x_speed, y_speed, self.radius])

    def update_particles(self):
        for particle in self.particles:
            particle[0] += particle[2]
            particle[1] += particle[3]
            particle[3] += 0.1
            particle[4] -= 0.03

def main():
    clock = pygame.time.Clock()
    fireworks = [Firework() for _ in range(5)]

    while True:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        for firework in fireworks:
            if not firework.particles:
                pygame.draw.circle(screen, firework.color, (int(firework.x), int(firework.y)), firework.radius)
                firework.launch()
                if firework.speed >= 0:
                    firework_sound.play()
                    firework.explode()
            else:
                firework.update_particles()
                for particle in firework.particles:
                    if particle[4] > 0:
                        pygame.draw.circle(screen, firework.color, (int(particle[0]), int(particle[1])), int(particle[4]))
                    else:
                        firework.reset()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
