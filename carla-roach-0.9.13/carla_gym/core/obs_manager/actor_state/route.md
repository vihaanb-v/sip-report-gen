- **__ init__()**
  - **self._parent_actor** is the ego vehicle to which this observation manager is attached.
  - **self._route_steps** is an attribute that determines the number of steps to consider from the planned route when computing observations.
  - **super(ObsManager, self).__init__()** internally calls the **_define_obs_space()** method.
- **_define_obs_space()**
  - **self.obs_space** is a dictionary of **Space** instances, composed of several **Box** instances. It is initialized as below,
  
        spaces.Dict(
            {
            'lateral_dist': spaces.Box(low=0.0, high=2.0, shape=(1,), dtype=np.float32),
            'angle_diff': spaces.Box(low=-2.0, high=2.0, shape=(1,), dtype=np.float32),
            'route_locs': spaces.Box(low=-5.0, high=5.0, shape=(self._route_steps*2,), dtype=np.float32),
            'dist_remaining': spaces.Box(low=0.0, high=100, shape=(1,), dtype=np.float32)
            }
        )
- **attach_ego_vehicle()**
  - The observation manager is attached to the ego vehicle.
- **get_observation()**
  - The below quantities are calculated in this method,
    - **lateral_dist**: Represents lateral distance between the ego vehicle and the planned route.
    - **angle_diff**: Represents the angle difference between the ego vehicle's orientation and the planned route.
    - **route_locs**: Represents locations along the planned route.
    - **dist_remaining**: Represents the remaining distance to the destination.
  - They are collected in **obs** dictionary and returned. **obs** is initialized as below,

        {
            'lateral_dist': np.array([lateral_dist], dtype=np.float32),
            'angle_diff': np.array([angle_diff], dtype=np.float32),
            'route_locs': np.array(location_list, dtype=np.float32),
            'dist_remaining': np.array([dist_remaining_in_km], dtype=np.float32)
        }