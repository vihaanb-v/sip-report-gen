- **__ init__()**
  - **self._parent_actor** is typically an ego vehicle to which this observation manager is attached.
  - **super(ObsManager, self).__init__()** internally calls the **_define_obs_space()** method.
- **_define_obs_space()**
  - **self.obs_space** is a dictionary of **Space** instances, composed of several **Box** instances. It is initialized as below,
   
        spaces.Dict(
            {
            'throttle': spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32),
            'steer': spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32),
            'brake': spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32),
            'gear': spaces.Box(low=0.0, high=5.0, shape=(1,), dtype=np.float32),  # 0-5
            'speed_limit': spaces.Box(low=0.0, high=50.0, shape=(1,), dtype=np.float32)
            }
            )
- **attach_ego_vehicle()**
  - This observation manager is attached to a specific ego vehicle.
- **get_observation()**
  - **control** contains the control applied on the ego vehicle in the last tick of simulation. 
  - **speed_limit** contains a modified speed limit by converting the original speed limit from km/h to m/s and then reducing it by 20% (multiplying by 0.8). The purpose of reducing the speed limit may be to account for a safety margin or to adjust the vehicle's behavior within the simulation.
  - **obs** is a dictionary which populated from the information stored in **control**. 
  - **obs** is then returned.
- **clean()**:
  - The ego vehicle is detached from this observation manager.