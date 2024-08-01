- **get_observation()**
  - This method calculates the below quantities,
    - **speed** : Speed of the ego vehicle calculated from x, y, z component of velocity.
    - **speed_xy** : Speed of the ego vehicle calculated from x, y component of velocity.
    - **forward_speed** : Speed along the forward vector of the ego vehicle.
  - These values are collected and returned as **obs** dictionary which is initialized as below,

        {
            'speed': np.array([speed], dtype=np.float32),
            'speed_xy': np.array([speed_xy], dtype=np.float32),
            'forward_speed': np.array([forward_speed], dtype=np.float32)
        }