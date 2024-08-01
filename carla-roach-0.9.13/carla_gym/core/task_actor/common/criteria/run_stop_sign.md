- **tick()**
  - Will be writing about other methods' details and this method details later.
  - This method returns information if the ego vehicle faced a stop sign which is initialized as below,
  
        {
            'event': 'encounter',
            'step': timestamp['step'],
            'simulation_time': timestamp['relative_simulation_time'],
            'id': self._target_stop_sign.id,
            'stop_loc': [stop_loc.x, stop_loc.y, stop_loc.z],
            'ev_loc': [ev_loc.x, ev_loc.y, ev_loc.z]
        }
    or it ran through a stop sign which is initialized as below,

        {
            'event': 'run',
            'step': timestamp['step'],
            'simulation_time': timestamp['relative_simulation_time'],
            'id': self._target_stop_sign.id,
            'stop_loc': [stop_loc.x, stop_loc.y, stop_loc.z],
            'ev_loc': [ev_loc.x, ev_loc.y, ev_loc.z]
        }
  - This contains information about timing and location information of ego vehicle and stop sign.