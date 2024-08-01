import pygame
import numpy as np

def convert_bb_to_pygame_rect(bb, scale_factor=1.0):
    return (int(bb.location.x * scale_factor), int(bb.location.y * scale_factor),
            int(bb.extent.x * 2 * scale_factor), int(bb.extent.y * 2 * scale_factor))


class BirdViewRenderer:
    def __init__(self, title="Pygame Window"):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(title)

    def tick(self, vehicle_bb, pedestrian_bb, bb):
        # draw all vehicle bounding boxes
        for b in vehicle_bb:
            pygame_rect = convert_bb_to_pygame_rect(b)
            pygame.draw.rect(self.screen, (0, 255, 0), pygame_rect, 3)
            
        # draw all pedestrian bounding boxes
        for b in pedestrian_bb:
            pygame_rect = convert_bb_to_pygame_rect(b)
            pygame.draw.rect(self.screen, (0, 0, 255), pygame_rect, 3)

        pygame.display.flip()
        self.clock.tick(60)  

    def run(self, vehicle_bb, pedestrian_bb, bb):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
        while self.running:
            self.tick(vehicle_bb, pedestrian_bb, bb)
        pygame.quit()
