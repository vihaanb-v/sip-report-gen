import pygame
import numpy as np

class PygameDisplay:
    def __init__(self, title="Pygame Window"):
        pygame.init()
        self.screen = None
        self.title = title
    
    def process_masks(self, masks):
        # Reshape masks to match image dimensions
        masks = masks.transpose(1, 2, 0)  # from (15, 192, 192) to (192, 192, 15)

        # Extract specific mask frames
        drivable_area = masks[:, :, 0]
        desired_route = masks[:, :, 1]
        lane_boundaries = masks[:, :, 2]
        vehicles = masks[:, :, 3:6]  # Use the first 3 frames for vehicles
        pedestrians = masks[:, :, 7:10]  # Use the first 3 frames for pedestrians
        lights_stops = masks[:, :, 11:14]  # Combine all lights and stops frames

        return drivable_area, desired_route, lane_boundaries, vehicles, pedestrians, lights_stops
    
    def display_image(self, image, image_org):
        # drivable_area, desired_route, lane_boundaries, vehicles, pedestrians, lights_stops = self.process_masks(masks)

        # Combine rows and the padded RGB image for the final display
        if image_org is None:
            merged_display = np.concatenate([image], axis=1)
        else:
            merged_display = np.concatenate([image_org, image], axis=1)
            
        if self.screen is None:
            height, width, _ = merged_display.shape
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption(self.title)

        # Convert the merged display to a format suitable for Pygame and display it
        pyg_image = pygame.surfarray.make_surface(np.swapaxes(merged_display, 0, 1))
        self.screen.blit(pyg_image, (0, 0))
        pygame.display.flip()
        pass

    def check_for_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False

    def close(self):
        pygame.quit()
