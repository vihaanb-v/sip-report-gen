- Will describe in detail later.
- **tick()**
  - If the ego vehicle is in a wrong lane or outside driving/parking lane, then this method will return information dictionary regarding the incident which is initialized as below,
  
        {
            'step': timestamp['step'],
            'simulation_time': timestamp['relative_simulation_time'],
            'ev_loc': [ev_loc.x, ev_loc.y, ev_loc.z],
            'distance_traveled': distance_traveled,
            'outside_lane': self._outside_lane_active,
            'wrong_lane': self._wrong_lane_active
        }