- Will describe in detail later.
- **tick()**
  - This method returns information if the ego vehicle deviates from its predetermined route which is initialized below,
  
            {
                'step': timestamp['step'],
                'simulation_time': timestamp['relative_simulation_time'],
                'ev_loc': [ev_loc.x, ev_loc.y, ev_loc.z],
                'off_route_max': off_route_max,
                'off_route_min': off_route_min
            }