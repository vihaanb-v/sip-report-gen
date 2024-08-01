from enum import Enum
import carla

class GazeDirection(Enum):
    LEFTBLINDSPOT = 0       
    LEFTMIRROR = 1          
    LEFT = 2                
    CENTER = 3              
    RIGHT = 4               
    RIGHTMIRROR = 5         
    RIGHTBLINDSPOT = 6      
    BACK = 7
    pass

# colors
red = carla.Color(255, 0, 0)
green = carla.Color(0, 255, 0)
blue = carla.Color(47, 210, 231)
cyan = carla.Color(0, 255, 255)
yellow = carla.Color(255, 255, 0)
orange = carla.Color(255, 162, 0)
white = carla.Color(255, 255, 255)

Gaze_Settings = {
    GazeDirection.CENTER: (0, 30, 40, red),
    GazeDirection.LEFT:  (70, 70, 35, green),
    GazeDirection.RIGHT:  (-70, 70, 35, blue),
    GazeDirection.LEFTBLINDSPOT:  (130, 5, 5, green),
    GazeDirection.RIGHTBLINDSPOT:  (-130, 5, 5, blue),
    GazeDirection.LEFTMIRROR:  (159.9, 20, 10, green),
    GazeDirection.RIGHTMIRROR:  (-159.9, 20, 10, blue),
    GazeDirection.BACK:  (179, 45, 20, red),
}


gaze_probability_normal = [0.04, 0.08, 0.1, 0.5, 0.1, 0.08, 0.04, 0.06] # --- normal
gaze_probability_distracted = [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125] # --- driver 2

gaze_frequency_normal = [3, 10]
gaze_frequency_distracted = [6, 15]
gaze_frequency_radar = [1, 1]


driver = {
    'normal': [gaze_probability_normal, gaze_frequency_normal],
    'distracted': [gaze_probability_distracted, gaze_frequency_radar]
}
