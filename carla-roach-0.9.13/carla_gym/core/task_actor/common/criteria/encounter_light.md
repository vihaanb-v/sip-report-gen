- This class basically returns the information about recent traffic light encountered by the ego vehicle.
- **__init__()**:
  - Will describe later.
- **tick()**:
  - Will describe later.
  - This returns an information dictionary that is initialized as below,
  
        {
            'step': timestamp['step'],
            'simulation_time': timestamp['relative_simulation_time'],
            'id': light_id,
            'tl_loc': light_loc.tolist()
        }
  - So, this returns timing and location information about the encountered traffic light. 