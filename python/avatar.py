import pygame
import math
import threading
import time
import sys
import os

# Hide pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Colors
BLACK = (10, 10, 15)
CYAN = (0, 255, 255)
GREEN = (50, 255, 100)
PURPLE = (180, 50, 255)

class AvatarWindow:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Jarvis - Anti-Gravity Core")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Thread-safe state
        self.lock = threading.Lock()
        self.state = 'idle'
        self.volume = 0.0
        self.start_time = time.time()
        
    def set_state(self, new_state, volume=0.0):
        with self.lock:
            self.state = new_state
            self.volume = min(1.0, max(0.0, volume))
            
    def run(self):
        """Main Pygame event loop. Must be called from the main thread."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    # We might want to handle clean exit of the other threads here
                    return
                    
            self.draw()
            self.clock.tick(60)

    def draw(self):
        self.screen.fill(BLACK)
        
        with self.lock:
            current_state = self.state
            current_volume = self.volume
            
        t = time.time() - self.start_time
        
        # Base parameters
        base_y = self.height // 2
        base_radius = 80
        color = CYAN
        bob_speed = 2.0
        bob_height = 30
        pulse = 0
        
        if current_state == 'listening':
            color = GREEN
            bob_speed = 4.0
            bob_height = 40
        elif current_state == 'processing':
            color = PURPLE
            bob_speed = 1.0
            bob_height = 20
            # Continuous pulsing
            pulse = math.sin(t * 8.0) * 15
        elif current_state == 'speaking':
            color = CYAN
            bob_speed = 2.0
            bob_height = 30
            # Pulse based on audio volume (magnified for visual effect)
            pulse = current_volume * 150 
        elif current_state == 'idle':
            color = CYAN
            bob_speed = 1.5
            bob_height = 20
        
        # Calculate positions
        y = base_y + math.sin(t * bob_speed) * bob_height
        radius = max(10, base_radius + pulse)
        
        # Draw anti-gravity distortion field (shadow/glow underneath)
        shadow_rect = pygame.Rect(0, 0, int(radius * 2.5), int(radius * 0.4))
        shadow_rect.center = (self.width // 2, self.height - 80)
        shadow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # alpha pulsing slightly even when idle
        shadow_alpha = int(50 + 20 * math.sin(t * bob_speed))
        pygame.draw.ellipse(shadow_surface, (color[0], color[1], color[2], shadow_alpha), shadow_rect)
        self.screen.blit(shadow_surface, (0, 0))

        # Draw glowing sphere core
        center_x = self.width // 2
        center_y = int(y)
        
        # Multiple translucent circles to create 3D glow effect
        for i in range(12, 0, -1):
            alpha = int(255 * (1 - i/12))
            r = int(radius + i * 4)
            glow_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, max(0, alpha - 50)), (r, r), r)
            self.screen.blit(glow_surf, (center_x - r, center_y - r))
        
        # Solid center core with geometric inner styling
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), int(radius * 0.4))
        
        # Anti-gravity data rings
        ring_radius = int(radius * 1.5)
        pygame.draw.arc(self.screen, color, (center_x - ring_radius, center_y - ring_radius, ring_radius*2, ring_radius*2), t, t + math.pi/2, 2)
        pygame.draw.arc(self.screen, color, (center_x - ring_radius, center_y - ring_radius, ring_radius*2, ring_radius*2), t + math.pi, t + math.pi*1.5, 2)
        
        pygame.display.flip()

if __name__ == "__main__":
    # Test script for AvatarWindow
    app = AvatarWindow()
    import threading
    
    def simulate_states():
        time.sleep(2)
        app.set_state('listening')
        time.sleep(3)
        app.set_state('processing')
        time.sleep(2)
        app.set_state('speaking', 0.8)
        time.sleep(0.5)
        app.set_state('speaking', 0.2)
        time.sleep(0.5)
        app.set_state('speaking', 0.9)
        time.sleep(1)
        app.set_state('idle')
        
    threading.Thread(target=simulate_states, daemon=True).start()
    app.run()
