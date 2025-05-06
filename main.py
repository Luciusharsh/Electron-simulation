import pygame
import simpy
import random
import math

# CONFIGURATION
FPS = 30
WIDTH, HEIGHT = 1000, 800
SCALE = 1e-4       # meters per pixel (0.1 mm/px)
NUM_ELECTRONS = 10
TIME_STEP = 5e-7   # simulation time step (seconds)
ELECTRON_MASS = 9.1093837e-31  # kg
ELECTRON_CHARGE = -1.602e-19   # C
K_CONST = 8.99e9   # N·m²/C²
RADIUS_PIXELS = 10
BACKGROUND = (0, 0, 0)
E_COLOR = (255, 255, 0)
V0 = 1e3          # initial max speed (m/s)

class Electron:
    def __init__(self, env, electron_id, x, y, vx, vy):
        self.env = env
        self.id = electron_id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.force_x = 0
        self.force_y = 0
        self.process = env.process(self.update())

    def update(self):
        while True:
            # Calculate forces from other electrons
            self.calculate_forces()
            
            # Update velocity and position
            self.update_kinematics()
            
            # Handle boundary collisions
            self.handle_boundaries()
            
            # Wait for next time step
            yield self.env.timeout(TIME_STEP)

    def calculate_forces(self):
        self.force_x = 0
        self.force_y = 0
        for other in self.env.electrons:
            if other.id != self.id:
                dx = self.x - other.x
                dy = self.y - other.y
                dist = math.hypot(dx, dy)
                if dist < 1e-12:
                    continue
                force_mag = K_CONST * ELECTRON_CHARGE**2 / dist**2
                self.force_x += force_mag * (dx / dist)
                self.force_y += force_mag * (dy / dist)

    def update_kinematics(self):
        # Update velocity
        self.vx += (self.force_x / ELECTRON_MASS) * TIME_STEP
        self.vy += (self.force_y / ELECTRON_MASS) * TIME_STEP
        
        # Update position
        self.x += self.vx * TIME_STEP
        self.y += self.vy * TIME_STEP

    def handle_boundaries(self):
        max_x = WIDTH * SCALE
        max_y = HEIGHT * SCALE
        
        if self.x <= 0:
            self.x = 0
            self.vx = abs(self.vx)
        elif self.x >= max_x:
            self.x = max_x
            self.vx = -abs(self.vx)
            
        if self.y <= 0:
            self.y = 0
            self.vy = abs(self.vy)
        elif self.y >= max_y:
            self.y = max_y
            self.vy = -abs(self.vy)

class ElectronSim:
    def __init__(self, env):
        self.env = env
        self.electrons = []
        env.electrons = self.electrons  # Make electrons accessible to all processes
        
        # Initialize electrons
        for i in range(NUM_ELECTRONS):
            x = random.uniform(0, WIDTH) * SCALE
            y = random.uniform(0, HEIGHT) * SCALE
            vx = random.uniform(-V0, V0)
            vy = random.uniform(-V0, V0)
            self.electrons.append(Electron(env, i, x, y, vx, vy))

    def get_positions(self):
        return [(e.x, e.y) for e in self.electrons]

    def draw(self, screen):
        for x, y in self.get_positions():
            px = int(x / SCALE)
            py = int(y / SCALE)
            pygame.draw.circle(screen, E_COLOR, (px, py), RADIUS_PIXELS)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Electron Simulation")
    clock = pygame.time.Clock()

    # Create SimPy environment and simulation
    env = simpy.Environment()
    elsim = ElectronSim(env)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Step simulation multiple times per frame for smoother animation
        for _ in range(10):  # Step simulation 10 times per frame
            env.step()

        # Render
        screen.fill(BACKGROUND)
        elsim.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()